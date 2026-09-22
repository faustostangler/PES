"""Unit tests for 'cresmo seed-prompts' CLI command and prompt seeding logic.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-014: Active Preflight Probes & Fail-Fast Observability
    - ADR-017: Langfuse v4 Prompt Management & Anonymizer Governance
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from cresmo.presentation.cli import main
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


class TestSeedPromptsCLI:
    """Test suite for the seed-prompts presentation command."""

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
        assert "[dry-run]" in captured.out
        assert "cresmo-gap-filler-pass1" in captured.out
        assert "Completed preview" in captured.out

    def test_seed_prompts_langfuse_client_unavailable_returns_code_2(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify unavailable Langfuse client exits with EXIT_CONFIG_OR_USAGE_ERROR (2)."""
        with patch(
            "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
            return_value=None,
        ):
            code = main(["seed-prompts"])
            assert code == EXIT_CONFIG_OR_USAGE_ERROR
            captured = capsys.readouterr()
            assert "Langfuse client could not be initialized" in captured.err

    def test_seed_prompts_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verify successful prompt registration in Langfuse returns EXIT_SUCCESS (0)."""
        mock_client = MagicMock()
        with patch(
            "cresmo.presentation.commands.seed_prompts.resolve_langfuse_client",
            return_value=mock_client,
        ):
            code = main(["seed-prompts"])
            assert code == EXIT_SUCCESS
            assert mock_client.create_prompt.call_count == 7
            captured = capsys.readouterr()
            assert "7/7 prompts synchronized to Langfuse" in captured.out
            assert "✔ Registered 'cresmo-gap-filler-pass1'" in captured.out

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
            assert "0/7 prompts synchronized" in captured.out
            assert "✘ Failed to register" in captured.err
