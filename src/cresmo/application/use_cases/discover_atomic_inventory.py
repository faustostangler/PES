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
    LlmJudgePort,
    LLMTransformationPort,
    NoOpPromptProviderPort,
    PromptProviderPort,
)
from cresmo.application.use_cases.index_raw_transcripts import (
    _can_retry,
    parse_judge_boolean,
)
from cresmo.domain.entities import (
    EnrichedCompendium,
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    ChannelId,
    ChannelName,
    ChatPrompt,
    EvaluationContext,
    JudgeCriterion,
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


def _parse_and_deduplicate_items(
    candidate_data: list[Any], content_title: str
) -> tuple[tuple[NoteTitle, NoteType], ...]:
    """Deduplicate and normalize discovered entity candidates by canonical title.

    Args:
        candidate_data: Raw parsed JSON entries.
        content_title: Title of content for validation reporting.

    Returns:
        Tuple of (NoteTitle, NoteType) pairs.

    Raises:
        DomainValidationError: If no valid entities could be discovered.
    """
    seen_titles: set[str] = set()
    items: list[tuple[NoteTitle, NoteType]] = []
    for entry in candidate_data:
        if not isinstance(entry, dict):
            continue
        title_str = entry.get("title")
        if not title_str or not isinstance(title_str, str):
            continue
        note_title = NoteTitle(title_str)
        key = note_title.value.casefold()
        if key in seen_titles:
            continue
        seen_titles.add(key)

        type_raw = entry.get("type")
        if type_raw is None:
            note_type = NoteType.CONCEPT
        else:
            try:
                note_type = NoteType.from_string(str(type_raw))
            except NoteTypologyError:
                note_type = NoteType.CONCEPT

        items.append((note_title, note_type))

    if not items:
        raise DomainValidationError(
            f"No valid entities discovered in compendium '{content_title}'."
        )

    return tuple(items)


class DiscoverAtomicInventoryUseCase:
    """Holistic entity discovery orchestrator across enriched compendium text."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float = 0.0,
        max_rewrites: int = 3,
        judge_enabled: bool | None = None,
        llm_judge_port: LlmJudgePort | None = None,
    ) -> None:
        """Initialize use case with required Hexagonal ports and judge parameters.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override (default: 0.0 for deterministic JSON extraction).
            max_rewrites: Maximum retry attempts when compliance check fails (default: 3).
            judge_enabled: Whether to execute LLM-as-a-judge verification loop.
                If None, defaults to True when prompt_provider is provided, False otherwise.
            llm_judge_port: Optional decoupled LlmJudgePort adapter (ADR-029).
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port
        self.judge_enabled = (
            (prompt_provider is not None or self.llm_judge_port is not None)
            if judge_enabled is None
            else judge_enabled
        )

    def _query_candidate_inventory(
        self,
        prompt: ChatPrompt,
        trace_id: str,
        session_id: str,
        user_id: str,
    ) -> list[Any]:
        """Query LLM synthesis port and extract candidate JSON inventory."""
        raw_response = self.llm_synthesis_port.transform(
            prompt=prompt,
            temperature=self.temperature,
            trace_id=trace_id,
            session_id=session_id,
            user_id=user_id,
        )
        try:
            return extract_json_data(raw_response)
        except (ValueError, TypeError, json.JSONDecodeError):
            return []

    def _evaluate_candidate_inventory(
        self,
        candidate_data: Any,
        compendium: EnrichedCompendium,
        judge_trace_id: str,
        session_id: str,
        user_id: str,
    ) -> bool:
        """Validate candidate inventory structure and optional semantic judge."""
        if not self.judge_enabled:
            if not isinstance(candidate_data, list):
                raise DomainValidationError(
                    f"Expected JSON array of entities for '{compendium.title.value}', got: {type(candidate_data).__name__}"
                )
            return True

        if not is_valid_inventory_json_structure(candidate_data):
            return False

        # Priority 1: Decoupled LlmJudgePort (ADR-029)
        if self.llm_judge_port is not None:
            context = EvaluationContext(
                stage_name="atomic_inventory",
                raw_text=compendium.body,
                candidate_text=json.dumps(candidate_data),
                metadata={
                    "title": compendium.title.value,
                    "channel": (
                        compendium.channel_name.value
                        if isinstance(compendium.channel_name, ChannelName)
                        else compendium.channel_name
                    ),
                },
                trace_id=judge_trace_id,
                required_criteria=(JudgeCriterion.INVENTORY_COHERENCE,),
            )
            evaluation = self.llm_judge_port.evaluate(context)
            return evaluation.passed

        # Priority 2: Transitional fallback when LlmJudgePort is not injected (ADR-010 / ADR-029)
        if not isinstance(self.prompt_provider, NoOpPromptProviderPort):
            judge_prompt = self.prompt_provider.get_prompt(
                PromptKey.JUDGE_ATOMIC_INVENTORY,
                content_title=compendium.title.value,
                channel_name=compendium.channel_name,
                compendium_body=compendium.body,
                inventory_json=json.dumps(candidate_data),
            )
            judge_response = self.llm_synthesis_port.transform(
                prompt=judge_prompt,
                temperature=0.0,
                trace_id=judge_trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            return parse_judge_boolean(judge_response)

        return True

    def execute(
        self,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> AtomicEntityInventory:
        """Execute discovery scan with deterministic guardrails and iterative LLM judge loop.

        Args:
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            AtomicEntityInventory Value Object containing deduplicated entities.

        Raises:
            DomainValidationError: If candidate entities are rejected by the judge or no valid entities could be discovered.
        """
        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_INVENTORY,
            content_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
        )

        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id if isinstance(compendium.channel_id, ChannelId) else None,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        content_id = compendium.content_id.value

        retries = 0

        while True:
            trace_suffix = "" if retries == 0 else f"_retry_{retries}"
            if retries > 0:
                logger.info(
                    "[InventoryDiscovery] Attempt %d: candidate inventory compliance check failed for '%s'. Re-extracting.",
                    retries,
                    content_id,
                )
            trace_id = f"{content_id}_inventory{trace_suffix}"
            judge_trace_id = f"{content_id}_inventory_judge{trace_suffix}"

            candidate_data = self._query_candidate_inventory(
                prompt=chat_prompt,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            is_valid = self._evaluate_candidate_inventory(
                candidate_data=candidate_data,
                compendium=compendium,
                judge_trace_id=judge_trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            if is_valid:
                break
            if not _can_retry(retries, self.max_rewrites):
                raise DomainValidationError(
                    f"Candidate entity inventory rejected by LLM-as-a-judge for '{compendium.title.value}'."
                )
            retries += 1

        items = _parse_and_deduplicate_items(candidate_data, compendium.title.value)
        return AtomicEntityInventory(items=items)
