"""Hermetic unit tests for ReconcileMOCsUseCase.

Verifies thematic Map of Content reconciliation, zero orphaned notes governance,
prompt templating with unicode preservation, and session/user identity routing.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from cresmo.application.ports import PromptProviderPort
from cresmo.application.use_cases.reconcile_mocs import ReconcileMOCsUseCase
from cresmo.domain.entities import AtomicNote, PipelineSessionId, UserIdentity
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import NoteTitle, NoteType
from tests.doubles.mock_adapters import InMemoryVaultAdapter, MockLLMAdapter


class TestReconcileMOCsUseCase:
    """Hermetic unit tests for ReconcileMOCsUseCase."""

    def test_init_validation_and_attributes(self) -> None:
        """Verify fail-fast parameter validation and attributes initialization."""
        llm = MockLLMAdapter()
        vault = InMemoryVaultAdapter()

        with pytest.raises(ValueError) as exc1:
            ReconcileMOCsUseCase(llm_synthesis_port=None, vault_port=vault)  # type: ignore[arg-type]
        assert str(exc1.value) == "llm_synthesis_port must be provided"

        with pytest.raises(ValueError) as exc2:
            ReconcileMOCsUseCase(llm_synthesis_port=llm, vault_port=None)  # type: ignore[arg-type]
        assert str(exc2.value) == "vault_port must be provided"

        use_case = ReconcileMOCsUseCase(
            llm_synthesis_port=llm,
            vault_port=vault,
            temperature=0.35,
        )
        assert use_case.llm_synthesis_port is llm
        assert use_case.vault_port is vault
        assert use_case.temperature == 0.35
        assert isinstance(use_case.prompt_provider, PromptProviderPort)

        custom_prompt_provider = MagicMock(spec=PromptProviderPort)
        use_case_custom = ReconcileMOCsUseCase(
            llm_synthesis_port=llm,
            vault_port=vault,
            prompt_provider=custom_prompt_provider,
        )
        assert use_case_custom.prompt_provider is custom_prompt_provider

    def test_reconcile_mocs_success_with_unicode_and_telemetry_defaults(self) -> None:
        """Verify successful clustering, non-ascii prompt serialization, and default telemetry."""
        vault_port = InMemoryVaultAdapter()
        note = AtomicNote(
            title=NoteTitle("Vilfredo Pareto"),
            note_type=NoteType.ENTITY,
            domain="Ciência Política",
            definition="Sociólogo italiano formulador do conceito de circulação das elites.",
        )
        vault_port.save_atomic_note(note)

        moc_payload = json.dumps(
            [
                {
                    "title": "MOC Teoria Política",
                    "theme": "Ciência Política",
                    "overview": "Mapeamento das teorias de liderança.",
                    "associated_notes": ["Vilfredo Pareto"],
                }
            ],
            ensure_ascii=False,
        )
        llm_port = MockLLMAdapter(responses=[moc_payload])

        use_case = ReconcileMOCsUseCase(
            llm_synthesis_port=llm_port,
            vault_port=vault_port,
            temperature=0.25,
        )
        from unittest.mock import patch

        with patch("json.dumps", wraps=json.dumps) as mock_dumps:
            mocs = use_case.execute()
            assert mock_dumps.call_args[1].get("ensure_ascii") is False

        assert len(mocs) == 1
        moc = mocs[0]
        assert moc.title.value == "MOC Teoria Política"
        assert moc.theme == "Ciência Política"
        assert moc.overview == "Mapeamento das teorias de liderança."
        assert moc.associated_notes == (NoteTitle("Vilfredo Pareto"),)
        assert vault_port.mocs.get("moc teoria política") == moc

        assert len(llm_port.call_history) == 1
        call = llm_port.call_history[0]
        assert call["temperature"] == 0.25
        assert call["trace_id"] == "mocs_reconciliation"
        assert call["session_id"] == "system:mocs"
        assert call["user_id"] == UserIdentity.worker().value

        prompt_str = call["prompt"].get_last_user_content()
        # Verify ensure_ascii=False preserves literal unicode
        assert "Ciência Política" in prompt_str
        assert '"title": "Vilfredo Pareto"' in prompt_str
        assert '"type": "entity"' in prompt_str
        assert '"domain": "Ciência Política"' in prompt_str

    def test_reconcile_mocs_telemetry_routing_and_overrides(self) -> None:
        """Verify session_id and user_id VO vs str routing."""
        vault_port = InMemoryVaultAdapter()
        llm_port = MockLLMAdapter(
            responses=[
                "[]",
                "[]",
                "[]",
            ]
        )
        use_case = ReconcileMOCsUseCase(
            llm_synthesis_port=llm_port,
            vault_port=vault_port,
        )

        # 1. PipelineSessionId VO and UserIdentity VO
        session_vo = PipelineSessionId("chan123:content456")
        user_vo = UserIdentity("user_alice")
        use_case.execute(session_id=session_vo, user_id=user_vo)
        assert llm_port.call_history[0]["session_id"] == "chan123:content456"
        assert llm_port.call_history[0]["user_id"] == "user_alice"

        # 2. String session and stripped string user
        use_case.execute(session_id="custom_sess_789", user_id="  user_bob  ")
        assert llm_port.call_history[1]["session_id"] == "custom_sess_789"
        assert llm_port.call_history[1]["user_id"] == "user_bob"

        # 3. None session and blank whitespace user fallback
        use_case.execute(session_id=None, user_id="   ")
        assert llm_port.call_history[2]["session_id"] == "system:mocs"
        assert llm_port.call_history[2]["user_id"] == UserIdentity.worker().value

    def test_reconcile_mocs_raises_on_non_list_json(self) -> None:
        """Verify DomainValidationError when extracted JSON is not a list."""
        vault_port = InMemoryVaultAdapter()
        llm_port = MockLLMAdapter(responses=['{"not": "a list"}', '"just a string"'])
        use_case = ReconcileMOCsUseCase(llm_synthesis_port=llm_port, vault_port=vault_port)

        with pytest.raises(DomainValidationError) as exc1:
            use_case.execute()
        assert str(exc1.value) == "MOC reconciliation expected JSON array, got: dict"

        with pytest.raises(DomainValidationError) as exc2:
            use_case.execute()
        assert str(exc2.value) == "MOC reconciliation expected JSON array, got: str"

    def test_reconcile_mocs_skips_malformed_entries_and_deduplicates_notes(self) -> None:
        """Verify filtering of non-dict, missing title, empty title, empty notes, and note case deduplication."""
        vault_port = InMemoryVaultAdapter()
        moc_json = json.dumps(
            [
                "non_dict_primitive",
                12345,
                {"missing_title": True},
                {"title": ""},
                {"title": 123},
                {"title": "MOC Missing Associated Notes Key"},
                {"title": "MOC Empty Notes", "associated_notes": []},
                {"title": "MOC Empty Strings Only", "associated_notes": ["", "   ", 456]},
                {
                    "title": "MOC Missing Theme And Overview",
                    "associated_notes": ["Standalone Note"],
                },
                {
                    "title": "MOC Valid",
                    "theme": "  Sociologia  ",
                    "overview": "  Overview text.  ",
                    "associated_notes": [
                        "Vilfredo Pareto",
                        "vilfredo pareto",  # Duplicate case-insensitive
                        "",  # Empty string skipped
                        "   ",  # Whitespace skipped
                        123,  # Non-string skipped
                        "Gaetano Mosca",
                        "ß",
                        "ss",  # Sharp s vs ss test: lower() treats them as distinct, upper() aliases them to SS
                    ],
                },
            ]
        )
        llm_port = MockLLMAdapter(responses=[moc_json])
        use_case = ReconcileMOCsUseCase(llm_synthesis_port=llm_port, vault_port=vault_port)
        mocs = use_case.execute()

        assert len(mocs) == 2

        # Verify default fallback for missing theme and overview
        moc_minimal = mocs[0]
        assert moc_minimal.title.value == "MOC Missing Theme And Overview"
        assert moc_minimal.theme == ""
        assert moc_minimal.overview == ""
        assert moc_minimal.associated_notes == (NoteTitle("Standalone Note"),)

        # Verify second valid MOC
        moc = mocs[1]
        assert moc.title.value == "MOC Valid"
        assert moc.theme == "Sociologia"
        assert moc.overview == "Overview text."
        assert len(moc.associated_notes) == 4
        assert moc.associated_notes[0].value == "Vilfredo Pareto"
        assert moc.associated_notes[1].value == "Gaetano Mosca"
        assert moc.associated_notes[2].value == "ß"
        assert moc.associated_notes[3].value == "ss"
        assert vault_port.mocs.get("moc valid") == moc
