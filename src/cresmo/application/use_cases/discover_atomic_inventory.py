"""Use Case: Discover Atomic Entity Inventory.

Executes holistic discovery scan across an Enriched Compendium to extract unique candidate
entities (concepts, entities, events, processes) conforming to the Cresmo style guide taxonomy.
Enhanced with Deterministic Guardrails and iterative LLM-as-a-judge verification loop.

Conforms to:
- SPEC-001: §1 (Holistic Inventory Discovery)
- SPEC-009: Atomic Inventory Discovery Judge and Guardrails Specification
- ADR-001: Modular Monolith Domain Integrity
- ADR-024: Iterative LLM-as-a-Judge and Deterministic Guardrails for Atomic Inventory Discovery
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from cresmo.application.json_parser import extract_json_data
from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpPromptProviderPort,
    PromptProviderPort,
)
from cresmo.application.use_cases.index_raw_transcripts import (
    _can_retry,
    parse_judge_boolean,
)
from cresmo.domain.entities import (
    ChannelTenantId,
    EnrichedCompendium,
    PipelineSessionId,
)
from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    NoteTitle,
    NoteType,
    PromptKey,
)

logger = logging.getLogger(__name__)

_BIG_ENDIAN_YEAR_REGEX = re.compile(r"^\d{4}")


def is_valid_inventory_json_structure(data: Any) -> bool:
    """Deterministic fast-fail guardrail for candidate entity inventory.

    Evaluates structural invariants before invoking the semantic LLM judge:
    1. Must be a non-empty list of dictionaries.
    2. Every dictionary must contain a non-empty string 'title'.
    3. Every dictionary must have a 'type' belonging to NoteType ('entity', 'concept', 'event', 'process').
    4. If 'type' is 'event', the title must start with a Big-Endian year (YYYY).

    Args:
        data: Parsed candidate JSON data.

    Returns:
        True if all structural invariants are satisfied; False otherwise.
    """
    if not isinstance(data, list) or not data:
        return False

    for entry in data:
        if not isinstance(entry, dict):
            return False
        title = entry.get("title")
        if not isinstance(title, str) or not title.strip():
            return False
        type_raw = entry.get("type")
        if not isinstance(type_raw, str):
            return False
        type_clean = type_raw.strip().lower()
        if type_clean not in {"entity", "concept", "event", "process"}:
            return False
        if type_clean == "event" and not _BIG_ENDIAN_YEAR_REGEX.match(title.strip()):
            return False

    return True


class DiscoverAtomicInventoryUseCase:
    """Holistic entity discovery orchestrator across enriched compendium text."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float = 0.0,
        max_rewrites: int = 3,
        judge_enabled: bool | None = None,
    ) -> None:
        """Initialize use case with required Hexagonal ports and judge parameters.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override (default: 0.0 for deterministic JSON extraction).
            max_rewrites: Maximum retry attempts when compliance check fails (default: 3).
            judge_enabled: Whether to execute LLM-as-a-judge verification loop.
                If None, defaults to True when prompt_provider is provided, False otherwise.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()
        self.max_rewrites = max_rewrites
        self.judge_enabled = (
            (prompt_provider is not None) if judge_enabled is None else judge_enabled
        )

    def execute(self, compendium: EnrichedCompendium) -> AtomicEntityInventory:
        """Execute discovery scan with deterministic guardrails and iterative LLM judge loop.

        Args:
            compendium: Enriched compendium from narrative expansion.

        Returns:
            AtomicEntityInventory Value Object containing deduplicated entities.

        Raises:
            DomainValidationError: If candidate entities are rejected by the judge or no valid entities could be discovered.
        """
        system_instruction, user_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_INVENTORY,
            compendium_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
        )

        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id,
        ).value
        user_id = ChannelTenantId.create(
            channel=compendium.channel_name,
            channel_id=compendium.channel_id,
        ).value
        content_id = compendium.content_id.value

        is_valid = False
        retries = 0
        candidate_data: list[Any] = []

        while not is_valid:
            if retries == 0:
                trace_id = f"{content_id}_inventory"
                judge_trace_id = f"{content_id}_inventory_judge"
            else:
                logger.info(
                    "[InventoryDiscovery] Attempt %d: candidate inventory compliance check failed for '%s'. Re-extracting.",
                    retries,
                    content_id,
                )
                trace_id = f"{content_id}_inventory_retry_{retries}"
                judge_trace_id = f"{content_id}_inventory_judge_retry_{retries}"

            raw_response = self.llm_synthesis_port.transform(
                prompt=user_prompt,
                system_instruction=system_instruction,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )

            try:
                candidate_data = extract_json_data(raw_response)
            except (ValueError, TypeError, json.JSONDecodeError):
                candidate_data = []

            if not self.judge_enabled:
                if not isinstance(candidate_data, list):
                    raise DomainValidationError(
                        f"Expected JSON array of entities for '{compendium.title.value}', got: {type(candidate_data).__name__}"
                    )
                is_valid = True
                break

            # Gate 1: Deterministic Guardrail (0 tokens / 0ms)
            if is_valid_inventory_json_structure(candidate_data):
                # Gate 2: Semantic LLM-as-a-Judge Evaluation (temperature=0.0)
                judge_sys, judge_prompt = self.prompt_provider.get_prompt(
                    PromptKey.JUDGE_ATOMIC_INVENTORY,
                    compendium_title=compendium.title.value,
                    channel_name=compendium.channel_name,
                    compendium_body=compendium.body,
                    inventory_json=json.dumps(candidate_data, ensure_ascii=False),
                )
                judge_response = self.llm_synthesis_port.transform(
                    prompt=judge_prompt,
                    system_instruction=judge_sys,
                    temperature=0.0,
                    trace_id=judge_trace_id,
                    session_id=session_id,
                    user_id=user_id,
                )
                is_valid = parse_judge_boolean(judge_response)
            else:
                is_valid = False

            if not is_valid:
                if not _can_retry(retries, self.max_rewrites):
                    break
                retries += 1

        if not is_valid:
            raise DomainValidationError(
                f"Candidate entity inventory rejected by LLM-as-a-judge for '{compendium.title.value}'."
            )

        # Step 4: Deduplicate and normalize by canonical title.
        seen_titles: set[str] = set()
        items: list[tuple[NoteTitle, NoteType]] = []
        for entry in candidate_data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            note_title = NoteTitle(title_str)
            key = note_title.value.lower()
            if key in seen_titles:
                continue
            seen_titles.add(key)

            type_raw = entry.get("type", "concept")
            try:
                note_type = NoteType.from_string(str(type_raw))
            except NoteTypologyError:
                note_type = NoteType.CONCEPT

            items.append((note_title, note_type))

        if not items:
            raise DomainValidationError(
                f"No valid entities discovered in compendium '{compendium.title.value}'."
            )

        # Step 5: Return AtomicEntityInventory Value Object.
        return AtomicEntityInventory(items=tuple(items))
