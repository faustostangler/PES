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
from typing import Any, Final

from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpPromptProviderPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.application.services.json_parser import extract_json_data
from cresmo.domain.entities import (
    AtomicNote,
    PipelineSessionId,
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import (
    DomainValidationError,
    NoteTypologyError,
)
from cresmo.domain.services.entity_matching import (
    MIN_HONORIFIC_NORMALIZED_LENGTH,
    normalize_entity_title_for_matching,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
    PromptKey,
)

DEFAULT_ATOMIC_BATCH_SIZE: Final[int] = 5
MIN_ATOMIC_BATCH_SIZE: Final[int] = 1
TRACE_SUFFIX_ATOMIC_BATCH: Final[str] = "_atomic_batch"

_KEY_TITLE: Final[str] = "title"
_KEY_TYPE: Final[str] = "type"
_KEY_DEFINITION: Final[str] = "definition"
_KEY_DIRECT_RELATIONS: Final[str] = "direct_relations"
_KEY_CAUSAL_MATRIX: Final[str] = "causal_matrix"
_KEY_CAUSE: Final[str] = "cause"
_KEY_EFFECT: Final[str] = "effect"
_KEY_EPISTEMIC_ATTRIBUTION: Final[str] = "epistemic_attribution"
_KEY_CROSS_CONTEXT: Final[str] = "cross_context"
_KEY_PRECURSORS: Final[str] = "precursors"
_KEY_LATERAL_EVENTS: Final[str] = "lateral_events"
_KEY_AFTERMATH: Final[str] = "aftermath"
_KEY_ALIASES: Final[str] = "aliases"
_KEY_CONTENT_TAGS: Final[str] = "content_tags"
_KEY_DOMAIN: Final[str] = "domain"
_KEY_CLUSTER: Final[str] = "cluster"
_KEY_SOURCE: Final[str] = "source"


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
        norm_title = normalize_entity_title_for_matching(n.title.value)
        if len(norm_title) >= MIN_HONORIFIC_NORMALIZED_LENGTH:
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
        norm_key = normalize_entity_title_for_matching(key)
        if key in existing_lookup:
            synthesized.append(existing_lookup[key])
        elif norm_key in norm_lookup:
            synthesized.append(norm_lookup[norm_key])
        else:
            pending.append((title, note_type))
    return synthesized, pending


def _parse_single_atomic_note(
    entry: dict[str, Any],
    compendium: StageTranscript,
) -> AtomicNote | None:
    """Parse raw dictionary payload from LLM into a validated AtomicNote aggregate."""
    title_str = entry.get(_KEY_TITLE)
    if not isinstance(title_str, str) or not title_str.strip():
        return None

    raw_type = entry.get(_KEY_TYPE)
    if isinstance(raw_type, str):
        try:
            note_type = NoteType.from_string(raw_type)
        except NoteTypologyError:
            note_type = NoteType.CONCEPT
    else:
        note_type = NoteType.CONCEPT

    definition = str(entry.get(_KEY_DEFINITION, "")).strip()
    relations_raw = entry.get(_KEY_DIRECT_RELATIONS, [])
    relations = tuple(NoteTitle(r) for r in relations_raw if isinstance(r, str) and r.strip())

    causal_matrix: CausalMatrix | None = None
    cm_raw = entry.get(_KEY_CAUSAL_MATRIX)
    if isinstance(cm_raw, dict):
        causal_matrix = CausalMatrix(
            cause=str(cm_raw.get(_KEY_CAUSE, "")),
            effect=str(cm_raw.get(_KEY_EFFECT, "")),
            epistemic_attribution=str(cm_raw.get(_KEY_EPISTEMIC_ATTRIBUTION, "")),
        )

    cross_context: CrossContextRelations | None = None
    cc_raw = entry.get(_KEY_CROSS_CONTEXT)
    if isinstance(cc_raw, dict):
        cross_context = CrossContextRelations(
            precursors=str(cc_raw.get(_KEY_PRECURSORS, "")),
            lateral_events=str(cc_raw.get(_KEY_LATERAL_EVENTS, "")),
            aftermath=str(cc_raw.get(_KEY_AFTERMATH, "")),
        )

    aliases_raw = entry.get(_KEY_ALIASES, [])
    aliases = tuple(a.strip() for a in aliases_raw if isinstance(a, str) and a.strip())
    tags_raw = entry.get(_KEY_CONTENT_TAGS, [])
    content_tags = tuple(t.strip() for t in tags_raw if isinstance(t, str) and t.strip())

    return AtomicNote(
        title=NoteTitle(title_str),
        note_type=note_type,
        definition=definition,
        content_tags=content_tags,
        domain=str(entry.get(_KEY_DOMAIN, compendium.channel.name)),
        cluster=str(entry.get(_KEY_CLUSTER, "")),
        source=str(entry.get(_KEY_SOURCE, compendium.content.title)),
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
        batch_size: int = DEFAULT_ATOMIC_BATCH_SIZE,
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
        self.batch_size = max(MIN_ATOMIC_BATCH_SIZE, batch_size)
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def _synthesize_chunk(
        self,
        chunk: list[tuple[NoteTitle, NoteType]],
        compendium: StageTranscript,
        session_id: str,
        user_id: str,
    ) -> list[AtomicNote]:
        """Synthesize and persist notes for a single batch chunk via LLM."""
        targets_summary = [
            {_KEY_TITLE: title.value, _KEY_TYPE: note_type.value} for title, note_type in chunk
        ]

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.ATOMIC_BATCH,
            content_title=compendium.content.title,
            channel_name=compendium.channel.name,
            compendium_body=compendium.content.text,
            targets_json=json.dumps(targets_summary, ensure_ascii=False),
        )
        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content.id.value}{TRACE_SUFFIX_ATOMIC_BATCH}",
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
        compendium: StageTranscript,
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

        session_id = PipelineSessionId.create(
            channel=compendium.channel,
            content_id=compendium.content,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value
        for i in range(0, len(pending_items), self.batch_size):
            chunk = pending_items[i : i + self.batch_size]
            synthesized_notes.extend(
                self._synthesize_chunk(chunk, compendium, session_id=session_id, user_id=user_id)
            )

        return synthesized_notes
