"""Unit tests for 'cresmo concat-master' presentation command.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-001: Core Knowledge Synthesis Specifications (Master RAG Consolidation)
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.domain.value_objects import ChannelName
from cresmo.presentation.cli import main
from cresmo.presentation.commands.concat_master import (
    handle_concat_master,
    register_subparser,
)
from cresmo.presentation.exit_codes import (
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


class TestConcatMasterCommand:
    """Test suite for cresmo concat-master command."""

    def test_register_subparser_arguments_and_metadata(self) -> None:
        """Verify concat-master subparser configuration, flags, aliases, defaults, and helps."""
        mock_subparsers = MagicMock()
        mock_parser = MagicMock()
        mock_subparsers.add_parser.return_value = mock_parser

        register_subparser(mock_subparsers)

        mock_subparsers.add_parser.assert_called_once_with(
            "concat-master",
            help="Consolidate enriched compendiums in ascending chronological order into master RAG files",
        )

        assert mock_parser.add_argument.call_count == 2
        mock_parser.add_argument.assert_any_call(
            "--channel",
            "-c",
            type=str,
            default=None,
            help="Target specific channel name to consolidate (default: all channels in enriched/)",
        )
        mock_parser.add_argument.assert_any_call(
            "--max-words",
            "-w",
            type=int,
            default=None,
            help="Maximum word count per master document (default: 500,000, never splitting files in the middle)",
        )
        mock_parser.set_defaults.assert_called_once_with(handler=handle_concat_master)

    def test_handle_concat_master_specific_channel_success(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify consolidating single channel displays parts, word counts, and returns EXIT_SUCCESS."""
        mock_settings = MagicMock()
        mock_use_case = MagicMock()

        part1 = MagicMock(
            part_number=1,
            output_path=Path("Fabio_Akita_001.md"),
            word_count=12000,
            document_count=5,
        )
        part2 = MagicMock(
            part_number=2,
            output_path=Path("Fabio_Akita_002.md"),
            word_count=8500,
            document_count=3,
        )
        mock_use_case.execute.return_value = [part1, part2]

        args = argparse.Namespace(channel="Fabio Akita", max_words=300000)

        with (
            patch(
                "cresmo.presentation.commands.concat_master.resolve_shared_settings",
                return_value=mock_settings,
            ) as mock_resolve_settings,
            patch(
                "cresmo.presentation.commands.concat_master.build_concat_master_use_case",
                return_value=mock_use_case,
            ) as mock_build_uc,
        ):
            code = handle_concat_master(args)
            assert code == EXIT_SUCCESS
            mock_resolve_settings.assert_called_once()
            mock_build_uc.assert_called_once_with(settings=mock_settings)
            mock_use_case.execute.assert_called_once_with(
                channel_name=ChannelName("Fabio Akita"), max_words=300000
            )

            captured = capsys.readouterr()
            expected_output = (
                "Consolidating master documents for channel: 'Fabio Akita'...\n"
                "Generated 2 master document(s) for 'Fabio Akita' (20,500 words):\n"
                "  • Part 001 -> Fabio_Akita_001.md (12,000 words, 5 documents)\n"
                "  • Part 002 -> Fabio_Akita_002.md (8,500 words, 3 documents)\n"
            )
            assert captured.out == expected_output
            assert captured.err == ""

    def test_handle_concat_master_specific_channel_empty(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify consolidating single channel with no documents logs informative notice and returns EXIT_SUCCESS."""
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = []

        args = argparse.Namespace(channel="UnknownChannel", max_words=None)

        with patch(
            "cresmo.presentation.commands.concat_master.build_concat_master_use_case",
            return_value=mock_use_case,
        ):
            code = handle_concat_master(args)
            assert code == EXIT_SUCCESS

            captured = capsys.readouterr()
            assert captured.out == (
                "Consolidating master documents for channel: 'UnknownChannel'...\n"
                "No enriched documents found for channel 'UnknownChannel'.\n"
            )
            assert captured.err == ""

    def test_handle_concat_master_all_channels_success(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify consolidating all channels aggregates summaries, prints part details, and returns EXIT_SUCCESS."""
        mock_use_case = MagicMock()

        part_a = MagicMock(
            channel_category="tech_ai",
            output_path=Path("ChannelA_001.md"),
            word_count=5000,
            document_count=2,
        )
        part_b1 = MagicMock(
            channel_category="philosophy",
            output_path=Path("ChannelB_001.md"),
            word_count=10000,
            document_count=4,
        )
        part_b2 = MagicMock(
            channel_category="philosophy",
            output_path=Path("ChannelB_002.md"),
            word_count=6000,
            document_count=3,
        )
        mock_use_case.execute_all.return_value = {
            "ChannelA": [part_a],
            "ChannelB": [part_b1, part_b2],
        }

        args = argparse.Namespace(channel=None, max_words=500000)

        with patch(
            "cresmo.presentation.commands.concat_master.build_concat_master_use_case",
            return_value=mock_use_case,
        ):
            code = handle_concat_master(args)
            assert code == EXIT_SUCCESS
            mock_use_case.execute_all.assert_called_once_with(max_words=500000)

            captured = capsys.readouterr()
            expected_output = (
                "Consolidating master documents across all channels in enriched/...\n"
                "\nMaster Consolidation Summary:\n"
                "- Total Channels Processed: 2\n"
                "- Master Documents Generated: 3\n"
                "- Total Words Aggregated: 21,000\n"
                "  ✓ [tech_ai] ChannelA_001.md (5,000 words, 2 docs)\n"
                "  ✓ [philosophy] ChannelB_001.md (10,000 words, 4 docs)\n"
                "  ✓ [philosophy] ChannelB_002.md (6,000 words, 3 docs)\n"
            )
            assert captured.out == expected_output
            assert captured.err == ""

    def test_handle_concat_master_all_channels_empty(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify consolidating all channels with empty directory logs notice and returns EXIT_SUCCESS."""
        mock_use_case = MagicMock()
        mock_use_case.execute_all.return_value = {}

        args = argparse.Namespace(channel=None, max_words=None)

        with patch(
            "cresmo.presentation.commands.concat_master.build_concat_master_use_case",
            return_value=mock_use_case,
        ):
            code = handle_concat_master(args)
            assert code == EXIT_SUCCESS

            captured = capsys.readouterr()
            assert captured.out == (
                "Consolidating master documents across all channels in enriched/...\n"
                "No enriched channel directories found to consolidate.\n"
            )
            assert captured.err == ""

    def test_handle_concat_master_error_handling(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify catastrophic failure writes formatted message to stderr and returns EXIT_INTERNAL_ERROR (1)."""
        args = argparse.Namespace(channel=None, max_words=None)

        with patch(
            "cresmo.presentation.commands.concat_master.resolve_shared_settings",
            side_effect=IOError("Permission denied writing to /data/master"),
        ):
            code = handle_concat_master(args)
            assert code == EXIT_INTERNAL_ERROR

            captured = capsys.readouterr()
            assert captured.out == ""
            assert captured.err == (
                "Master consolidation error: Permission denied writing to /data/master\n"
            )

    def test_concat_master_cli_main_dispatch(self) -> None:
        """Verify 'cresmo concat-master -c TestChannel -w 100000' executes via CLI main entrypoint."""
        mock_use_case = MagicMock()
        mock_use_case.execute.return_value = []

        with patch(
            "cresmo.presentation.commands.concat_master.build_concat_master_use_case",
            return_value=mock_use_case,
        ):
            exit_code = main(["concat-master", "-c", "TestChannel", "-w", "100000"])
            assert exit_code == EXIT_SUCCESS
            mock_use_case.execute.assert_called_once_with(
                channel_name=ChannelName("TestChannel"), max_words=100000
            )
