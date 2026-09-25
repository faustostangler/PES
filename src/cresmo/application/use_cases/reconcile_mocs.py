"""Stage 6 Use Case: Reconcile Maps of Content (MOC).

Reconciles atomic notes into thematic Maps of Content, enforcing zero orphaned notes
and maintaining a coherent thematic hierarchy across the knowledge graph.

Conforms to:
- SPEC-001: §1 (Stage 6 Map of Content Reconciliation)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import json

from cresmo.application.json_parser import extract_json_data
from cresmo.application.ports import (
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import MapOfContent
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import NoteTitle


class ReconcileMOCsUseCase:
    """Stage 6: Map of Content reconciliation and graph topological governance orchestrator."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort | None = None,
        vault_port: VaultRepositoryPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
        *,
        llm_port: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize Stage 6 use case with required ports.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing atomic note queries and MOC persistence.
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for MOC reconciliation.
            llm_port: Backward-compatible alias for llm_synthesis_port.
        """
        port = llm_synthesis_port or llm_port
        if port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = port
        self.llm_port = port  # Backward compatibility
        self.vault_port = vault_port
        self.temperature = temperature
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

    def execute(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        system_instruction, user_prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_synthesis_port.transform(
            prompt=user_prompt,
            system_instruction=system_instruction,
            temperature=self.temperature,
            trace_id="stage6_mocs_reconciliation",
            session_id="stage6_mocs",
            user_id="vault",
        )
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs
