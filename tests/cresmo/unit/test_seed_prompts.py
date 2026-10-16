"""Unit tests for 'cresmo seed-prompts' CLI command and prompt seeding logic.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-014: Active Preflight Probes & Fail-Fast Observability
    - ADR-017: Langfuse v4 Prompt Management & Anonymizer Governance
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

from types import SimpleNamespace as Namespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from cresmo.presentation.cli import main
from cresmo.presentation.commands.seed_prompts import (
    PROMPT_MAPPINGS,
    _to_mustache,
    handle_seed_prompts,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


class TestSeedPromptsCLI:
    """Test suite for the seed-prompts presentation command."""

    def test_to_mustache_transformations(self) -> None:
        """Verify single brace {var} conversion to {{var}} without double-escaping."""
        assert (
            _to_mustache("Hello {name}, your ID is {id_num}")
            == "Hello {{name}}, your ID is {{id_num}}"
        )
        assert (
            _to_mustache("Already {{mustache}} stays {{mustache}}")
            == "Already {{mustache}} stays {{mustache}}"
        )
        assert _to_mustache("Plain text without variables") == "Plain text without variables"

    def test_seed_prompts_cli_help(self) -> None:
        """Verify seed-prompts CLI displays help and options."""
        assert main(["seed-prompts", "--help"]) == EXIT_SUCCESS

    def test_get_raw_prompt_template_returns_populated_template(self) -> None:
        """Verify get_raw_prompt_template on JsonPromptProvider returns non-empty template."""
        provider = JsonPromptProvider()
        tpl = provider.get_raw_prompt_template("gap_filler_pass1")
        assert isinstance(tpl, str)
        assert len(tpl) > 0
        assert "SKILL SPECIFICATION" in tpl or "Transcript" in tpl

    def test_seed_prompts_dry_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify --dry-run prints template previews and exits with SUCCESS without API calls."""
        code = main(["seed-prompts", "--dry-run"])
        assert code == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert (
            f"[dry-run] Rendering {len(PROMPT_MAPPINGS)} Chat-Native prompt templates:\n"
            in captured.out
        )
        provider = JsonPromptProvider()
        for lf_name, json_key in PROMPT_MAPPINGS.items():
            sys_inst, user_tpl = provider.get_chat_prompt_template(json_key)
            sys_mustache = _to_mustache(sys_inst)
            user_mustache = _to_mustache(user_tpl)
            preview_sys = sys_mustache[:50].replace("\n", " ")
            preview_usr = user_mustache[:50].replace("\n", " ")
            expected_line = f"- {lf_name} (key={json_key}): [system] {preview_sys}... | [user] {preview_usr}...\n"
            assert expected_line in captured.out
        assert (
            f"[dry-run] Completed preview of {len(PROMPT_MAPPINGS)} chat prompts.\n" in captured.out
        )

    def test_seed_prompts_langfuse_client_unavailable_returns_code_2(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify unavailable Langfuse client exits with EXIT_CONFIG_OR_USAGE_ERROR (2)."""
        mock_settings = MagicMock()
        with (
            patch(
                "cresmo.presentation.commands.seed_prompts.resolve_shared_settings",
                return_value=mock_settings,
            ) as mock_resolve_settings,
            patch(
                "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
                return_value=None,
            ) as mock_resolve_lf,
        ):
            code = main(["seed-prompts"])
            assert code == EXIT_CONFIG_OR_USAGE_ERROR
            mock_resolve_settings.assert_called_once()
            mock_resolve_lf.assert_called_once_with(mock_settings)
            captured = capsys.readouterr()
            assert captured.err == (
                "Langfuse client could not be initialized or server is unreachable.\n"
                "Ensure Langfuse is running (`make up`) and environment variables are set.\n"
            )

    def test_seed_prompts_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify successful prompt registration in Langfuse returns EXIT_SUCCESS (0) with exact payload."""
        mock_client = MagicMock()
        mock_settings = MagicMock()
        provider = JsonPromptProvider()
        with (
            patch(
                "cresmo.presentation.commands.seed_prompts.resolve_shared_settings",
                return_value=mock_settings,
            ),
            patch(
                "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
                return_value=mock_client,
            ) as mock_resolve_lf,
        ):
            code = main(["seed-prompts"])
            assert code == EXIT_SUCCESS
            mock_resolve_lf.assert_called_once_with(mock_settings)
            assert mock_client.create_prompt.call_count == len(PROMPT_MAPPINGS)

            for call in mock_client.create_prompt.call_args_list:
                name = call.kwargs["name"]
                assert name in PROMPT_MAPPINGS
                assert call.kwargs["labels"] == ["production"]
                assert call.kwargs["tags"] == ["cresmo", "v2"]
                assert call.kwargs["type"] == "chat"
                prompt = call.kwargs["prompt"]
                assert len(prompt) == 2
                assert prompt[0]["role"] == "system"
                assert prompt[1]["role"] == "user"
                expected_sys, expected_usr = provider.get_chat_prompt_template(
                    PROMPT_MAPPINGS[name]
                )
                assert prompt[0]["content"] == _to_mustache(expected_sys)
                assert prompt[1]["content"] == _to_mustache(expected_usr)
                assert len(prompt[0]["content"]) > 0
                assert len(prompt[1]["content"]) > 0

            captured = capsys.readouterr()
            assert (
                f"{len(PROMPT_MAPPINGS)}/{len(PROMPT_MAPPINGS)} prompts synchronized to Langfuse"
                in captured.out
            )
            assert (
                "✔ Registered 'cresmo-gap-filler-pass1' in Langfuse [type=chat, label=production]\n"
                in captured.out
            )

    def test_seed_prompts_custom_label(self) -> None:
        """Verify custom --label is passed to client.create_prompt."""
        mock_client = MagicMock()
        with patch(
            "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
            return_value=mock_client,
        ):
            code = main(["seed-prompts", "--label", "staging"])
            assert code == EXIT_SUCCESS
            _, kwargs = mock_client.create_prompt.call_args
            assert kwargs["labels"] == ["staging"]

    def test_seed_prompts_empty_or_none_label_defaults_to_production(self) -> None:
        """Verify empty or None label defaults strictly to 'production'."""
        mock_client = MagicMock()
        with patch(
            "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
            return_value=mock_client,
        ):
            assert handle_seed_prompts(Namespace(label="", dry_run=False)) == EXIT_SUCCESS
            assert mock_client.create_prompt.call_args.kwargs["labels"] == ["production"]

            mock_client.reset_mock()
            assert handle_seed_prompts(Namespace(label=None, dry_run=False)) == EXIT_SUCCESS
            assert mock_client.create_prompt.call_args.kwargs["labels"] == ["production"]

    def test_seed_prompts_partial_failure_returns_success(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that when some prompts succeed and some fail, exits with EXIT_SUCCESS (0)."""
        mock_client = MagicMock()
        call_counter = 0

        def flaky_create_prompt(**kwargs: Any) -> None:
            nonlocal call_counter
            call_counter += 1
            if call_counter == 1:
                raise RuntimeError("First prompt transient error")

        mock_client.create_prompt.side_effect = flaky_create_prompt
        with patch(
            "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
            return_value=mock_client,
        ):
            code = main(["seed-prompts"])
            assert code == EXIT_SUCCESS
            captured = capsys.readouterr()
            assert (
                f"Completed: {len(PROMPT_MAPPINGS) - 1}/{len(PROMPT_MAPPINGS)} prompts synchronized to Langfuse.\n"
                in captured.out
            )
            assert "✘ Failed to register" in captured.err

    def test_seed_prompts_all_failures_returns_internal_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that when all registrations fail, exits with EXIT_INTERNAL_ERROR (1)."""
        mock_client = MagicMock()
        mock_client.create_prompt.side_effect = RuntimeError("API down")
        with patch(
            "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
            return_value=mock_client,
        ):
            code = main(["seed-prompts"])
            assert code == EXIT_INTERNAL_ERROR
            captured = capsys.readouterr()
            assert (
                f"Completed: 0/{len(PROMPT_MAPPINGS)} prompts synchronized to Langfuse.\n"
                in captured.out
            )
            assert "✘ Failed to register" in captured.err

    def test_seed_prompts_empty_mappings_returns_success(self) -> None:
        """Verify that when no prompts are defined, success is 0, failure is 0, returning EXIT_SUCCESS."""
        mock_client = MagicMock()
        with (
            patch(
                "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
                return_value=mock_client,
            ),
            patch.dict("cresmo.presentation.commands.seed_prompts.PROMPT_MAPPINGS", {}, clear=True),
        ):
            assert handle_seed_prompts(Namespace(label="prod", dry_run=False)) == EXIT_SUCCESS

    def test_seed_prompts_single_prompt_failure_returns_internal_error(self) -> None:
        """Verify that when single configured prompt fails, exits with EXIT_INTERNAL_ERROR (1)."""
        mock_client = MagicMock()
        mock_client.create_prompt.side_effect = RuntimeError("failure")
        with (
            patch(
                "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
                return_value=mock_client,
            ),
            patch.dict(
                "cresmo.presentation.commands.seed_prompts.PROMPT_MAPPINGS",
                {"single": "gap_filler_pass1"},
                clear=True,
            ),
        ):
            assert (
                handle_seed_prompts(Namespace(label="prod", dry_run=False)) == EXIT_INTERNAL_ERROR
            )
