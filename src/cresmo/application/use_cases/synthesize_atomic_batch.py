"""Stage 5 Use Case: Synthesize Atomic Note Batches.

Generates rich AtomicNote entities from an AtomicEntityInventory in small batches (<= 5).
"""

from __future__ import annotations

import json

from cresmo.application.json_parser import extract_json_data
from cresmo.application.ports import LLMTransformationPort, VaultRepositoryPort
from cresmo.domain.entities import AtomicNote, EnrichedCompendium
from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)


class SynthesizeAtomicBatchUseCase:
    """Stage 5: Batched atomic note synthesis and incremental vault persistence."""

    def __init__(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        batch_size: int = 5,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.batch_size = max(1, batch_size)

    def execute(
        self,
        inventory: AtomicEntityInventory,
        compendium: EnrichedCompendium,
    ) -> list[AtomicNote]:
        """Execute Stage 5 batched synthesis.

        Args:
            inventory: Discovered unique entity inventory from Stage 4.
            compendium: Enriched compendium from Stage 3.

        Returns:
            List of all synthesized and persisted AtomicNote domain aggregates.

        Raises:
            DomainValidationError: If synthesis payload violates domain rules.
        """
        all_items = list(inventory.items)
        synthesized_notes: list[AtomicNote] = []

        # Step 1: Partition pending entities into chunks of size <= batch_size.
        for i in range(0, len(all_items), self.batch_size):
            chunk = all_items[i : i + self.batch_size]
            targets_summary = [
                {"title": title.value, "type": note_type.value}
                for title, note_type in chunk
            ]

            # Step 2a: Prompt LLM for structured JSON definitions, causal matrices, and relations.
            prompt = (
                f"Source Compendium Title: {compendium.title.value}\n"
                f"Source Channel: {compendium.channel_name}\n\n"
                f"Source Context:\n{compendium.body}\n\n"
                f"Target Entities to Synthesize in this batch:\n{json.dumps(targets_summary, ensure_ascii=False)}\n\n"
                "Synthesize each entity into an Obsidian Atomic Note object.\n"
                "Output strictly a JSON array of note objects with keys:\n"
                "- title (string)\n"
                "- type (concept|entity|event|process)\n"
                "- definition (string, minimum 20 characters of contextual analysis)\n"
                "- direct_relations (list of related entity titles, MUST NOT include the note's own title)\n"
                "- causal_matrix (object with cause, effect, epistemic_attribution)\n"
                "- cross_context (object with precursors, lateral_events, aftermath)\n"
                "- domain (string)\n"
                "- cluster (string)\n"
                "- source (string)\n"
                "- aliases (list of strings)"
            )

            response = self.llm_port.transform(prompt=prompt)
            data = extract_json_data(response)
            if not isinstance(data, list):
                raise DomainValidationError(
                    f"Batch synthesis expected JSON array, got: {type(data).__name__}"
                )

            # Step 2b: Parse response into AtomicNote domain aggregates.
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                title_str = entry.get("title")
                if not title_str or not isinstance(title_str, str):
                    continue
                title = NoteTitle(title_str)

                type_raw = entry.get("type", "concept")
                try:
                    note_type = NoteType.from_string(str(type_raw))
                except NoteTypologyError:
                    note_type = NoteType.CONCEPT

                definition = str(entry.get("definition", "")).strip()

                relations_raw = entry.get("direct_relations", [])
                relations = tuple(
                    NoteTitle(r)
                    for r in relations_raw
                    if isinstance(r, str) and r.strip()
                )

                cm_raw = entry.get("causal_matrix")
                causal_matrix: CausalMatrix | None = None
                if isinstance(cm_raw, dict):
                    causal_matrix = CausalMatrix(
                        cause=str(cm_raw.get("cause", "")),
                        effect=str(cm_raw.get("effect", "")),
                        epistemic_attribution=str(cm_raw.get("epistemic_attribution", "")),
                    )

                cc_raw = entry.get("cross_context")
                cross_context: CrossContextRelations | None = None
                if isinstance(cc_raw, dict):
                    cross_context = CrossContextRelations(
                        precursors=str(cc_raw.get("precursors", "")),
                        lateral_events=str(cc_raw.get("lateral_events", "")),
                        aftermath=str(cc_raw.get("aftermath", "")),
                    )

                aliases_raw = entry.get("aliases", [])
                aliases = tuple(
                    a.strip()
                    for a in aliases_raw
                    if isinstance(a, str) and a.strip()
                )

                tags_raw = entry.get("content_tags", [])
                content_tags = tuple(
                    t.strip()
                    for t in tags_raw
                    if isinstance(t, str) and t.strip()
                )

                note = AtomicNote(
                    title=title,
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

                # Step 2c & 2d: Save note and update index entry incrementally.
                self.vault_port.save_atomic_note(note)
                self.vault_port.update_index_entry(note)
                synthesized_notes.append(note)

        # Step 3: Return list of all synthesized AtomicNote entities.
        return synthesized_notes
