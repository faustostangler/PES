"""Use Case: Synthesize Atomic Note Batches.

Generates rich AtomicNote domain aggregates from an AtomicEntityInventory in small,
controlled batches (default: <= 5), enforcing incremental vault persistence and
tiered index reconciliation.

Conforms to:
- SPEC-001: §1 (Batched Atomic Synthesis)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import json
import re
from typing import Any, Final

from cresmo.application.json_parser import extract_json_data
from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpPromptProviderPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
    PromptKey,
)

# Honorific prefixes stripped during entity normalization to prevent duplicate notes
_HONORIFIC_PREFIXES: tuple[str, ...] = ("dom ", "dona ", "d. ", "d ")
_PUNCT_COLLAPSE_RE = re.compile(r"[\s\-_.,()]+")
_MIN_HONORIFIC_NORMALIZED_LENGTH: Final[int] = 4


def _norm_honorific(s: str) -> str:
    """Normalize note title by stripping honorific prefixes and collapsing punctuation.

    Args:
        s: Raw title string.

    Returns:
        Cleaned lowercase title without honorific prefix.
    """
    cleaned = s.lower().strip()
    for pfx in _HONORIFIC_PREFIXES:
        if cleaned.startswith(pfx):
            cleaned = cleaned[len(pfx) :].strip()
            break
    return _PUNCT_COLLAPSE_RE.sub(" ", cleaned).strip()


def _build_existing_lookups(
    notes: list[AtomicNote],
) -> tuple[dict[str, AtomicNote], dict[str, AtomicNote]]:
    """Build exact and honorific-normalized title lookup tables."""
    lookup: dict[str, AtomicNote] = {}
    norm_lookup: dict[str, AtomicNote] = {}
    for n in notes:
        lookup[n.title.value.lower()] = n
        for a in n.aliases:
            lookup[a.lower()] = n
        norm_title = _norm_honorific(n.title.value)
        if len(norm_title) >= _MIN_HONORIFIC_NORMALIZED_LENGTH:
            norm_lookup[norm_title] = n
    return lookup, norm_lookup


def _partition_inventory_items(
    inventory: AtomicEntityInventory,
    existing_lookup: dict[str, AtomicNote],
    norm_lookup: dict[str, AtomicNote],
) -> tuple[list[AtomicNote], list[tuple[NoteTitle, NoteType]]]:
    """Segregate inventory entities into existing cached notes and pending synthesis items."""
    synthesized: list[AtomicNote] = []
    pending: list[tuple[NoteTitle, NoteType]] = []
    for title, note_type in inventory.items:
        key = title.value.lower()
        norm_key = _norm_honorific(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def _parse_single_atomic_note(
    entry: dict[str, Any],
    compendium: EnrichedCompendium,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get("title")
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    type_raw = entry.get("type", "concept")
    try:
        note_type = NoteType.from_string(str(type_raw))
    except NoteTypologyError:
        note_type = NoteType.CONCEPT

    definition = str(entry.get("definition", "")).strip()
    relations_raw = entry.get("direct_relations", [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get("causal_matrix")
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get("cause", "")),
            effect=str(cm_raw.get("effect", "")),
            epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get("cross_context")
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get("precursors", "")),
            lateral_events=str(cc_raw.get("lateral_events", "")),
            aftermath=str(cc_raw.get("aftermath", "")),
        )

    aliases_raw = entry.get("aliases", [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get("content_tags", [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get("domain", compendium.channel_name)),
        cluster=str(entry.get("cluster", "")),
        source=str(entry.get("source", compendium.title.value)),
        aliases=aliases,
        direct_relations=relations,
        causal_matrix=causal_matrix,
        cross_context=cross_context,
    )


class SynthesizeAtomicBatchUseCase:
    """Batched Atomic Note synthesis and incremental reconciliation orchestrator."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with ports and batch sizing.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing vault atomic note and index persistence.
            batch_size: Maximum count of entities per LLM prompt chunk (default: 5).
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for atomic note synthesis.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def _synthesize_chunk(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {"title": title.value, "type": note_type.value} for title, note_type in chunk
        ]

        system_instruction, user_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            compendium_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        session_id = PipelineSessionId.create(
            channel=compendium.channel_name,
            content_id=compendium.content_id,
            channel_id=compendium.channel_id,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        response = self.llm_synthesis_port.transform(
            prompt=user_prompt,
            system_instruction=system_instruction,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_atomic_batch",
            session_id=session_id,
            user_id=user_id,
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Batch synthesis expected JSON array, got: {type(data).__name__}"
            )

        notes: list[AtomicNote] = []
        for entry in data:
            if isinstance(entry, dict) and (note := _parse_single_atomic_note(entry, compendium)):
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                notes.append(note)
        return notes

    def execute(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
        user: UserIdentity | None = None,
    ) -> list[AtomicNote]:
        """Execute batched atomic note synthesis.

        Args:
            inventory: Discovered unique entity inventory.
            compendium: Enriched compendium from narrative expansion.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        existing_notes = self.vault_port.get_all_atomic_notes()
        existing_lookup, norm_lookup = _build_existing_lookups(existing_notes)
        synthesized_notes, pending_items = _partition_inventory_items(
            inventory, existing_lookup, norm_lookup
        )

        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(self._synthesize_chunk(chunk, compendium, user=user))

        return synthesized_notes
