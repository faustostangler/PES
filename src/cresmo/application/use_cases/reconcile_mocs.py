"""Use Case: Reconcile Maps of Content (MOC).

Reconciles atomic notes into thematic Maps of Content, enforcing zero orphaned notes
and maintaining a coherent thematic hierarchy across the knowledge graph.

Conforms to:
- SPEC-001: §1 (Map of Content Reconciliation)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import json
from typing import Final

from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpPromptProviderPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.application.services.json_parser import extract_json_data
from cresmo.domain.entities import MapOfContent, PipelineSessionId, UserIdentity
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import NoteTitle, PromptKey

DEFAULT_MOCS_SESSION_ID: Final[str] = "system:mocs"
TRACE_ID_MOCS_RECONCILIATION: Final[str] = "mocs_reconciliation"

_KEY_TITLE: Final[str] = "title"
_KEY_TYPE: Final[str] = "type"
_KEY_DOMAIN: Final[str] = "domain"
_KEY_THEME: Final[str] = "theme"
_KEY_OVERVIEW: Final[str] = "overview"
_KEY_ASSOCIATED_NOTES: Final[str] = "associated_notes"


class ReconcileMOCsUseCase:
    """Map of Content reconciliation and graph topological governance orchestrator."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with required ports.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing atomic note queries and MOC persistence.
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for MOC reconciliation.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def execute(
        self,
        session_id: PipelineSessionId | None = None,
        user_id: UserIdentity | None = None,
    ) -> list[MapOfContent]:
        """Execute MOC reconciliation.

        Args:
            session_id: Optional session identifier for telemetry (defaults to system:mocs).
            user_id: Optional executing user identity (defaults to system:worker).

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {_KEY_TITLE: n.title.value, _KEY_TYPE: n.note_type.value, _KEY_DOMAIN: n.domain}
            for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.RECONCILE_MOCS,
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        actual_session_id = session_id.value if session_id is not None else DEFAULT_MOCS_SESSION_ID
        actual_user_id = (
            user_id.value if user_id is not None else UserIdentity.worker().value
        )

        response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=TRACE_ID_MOCS_RECONCILIATION,
            session_id=actual_session_id,
            user_id=actual_user_id,
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
            title_str = entry.get(_KEY_TITLE)
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get(_KEY_THEME, "")).strip()
            overview = str(entry.get(_KEY_OVERVIEW, "")).strip()

            raw_associated = entry.get(_KEY_ASSOCIATED_NOTES, [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for raw_note in raw_associated:
                if isinstance(raw_note, str) and raw_note.strip():
                    note_title = NoteTitle(raw_note)
                    note_key = note_title.value.lower()
                    if note_key not in seen_associated:
                        seen_associated.add(note_key)
                        associated_notes.append(note_title)

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
