"""Unit tests for 'cresmo run' subparser registration and argument parsing.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock

from cresmo.presentation.commands.run_parser import register_run_subparser


class TestRunParser:
    """Test suite for register_run_subparser."""

    def test_register_run_subparser_calls(self) -> None:
        """Verify exact add_parser and add_argument calls, flags, options, defaults, and helps."""
        mock_subparsers = MagicMock()
        mock_run_parser = MagicMock()
        mock_subparsers.add_parser.return_value = mock_run_parser
        mock_handler = MagicMock()

        register_run_subparser(mock_subparsers, handler=mock_handler)

        mock_subparsers.add_parser.assert_called_once_with(
            "run",
            help="Run end-to-end knowledge synthesis for a video or manifest playlist",
        )

        # Verify all 15 add_argument calls with exact arguments and metadata
        expected_calls = [
            (
                ("--url",),
                {
                    "required": False,
                    "default": None,
                    "help": "Target YouTube or media video URL",
                },
            ),
            (
                ("--all",),
                {
                    "action": "store_true",
                    "default": True,
                    "help": "(Default) Run full pipeline for all videos in the manifest playlists",
                },
            ),
            (
                ("--manifest", "--playlist"),
                {
                    "type": Path,
                    "default": None,
                    "help": "Path to manifest or playlist text file (default: data/playlist.txt)",
                },
            ),
            (
                ("--passes",),
                {
                    "type": int,
                    "default": 3,
                    "help": "Refinement passes for gap filler (default: 3)",
                },
            ),
            (
                ("--batch-size",),
                {
                    "type": int,
                    "default": None,
                    "help": "Batch size override for atomic note synthesis",
                },
            ),
            (
                ("--dry-run",),
                {
                    "action": "store_true",
                    "help": "Ingest raw transcript without executing generative LLM synthesis",
                },
            ),
            (
                ("--force-reprocess",),
                {
                    "action": "store_true",
                    "help": "Bypass ledger idempotency guard and re-synthesize even if already completed",
                },
            ),
            (
                ("--lookback",),
                {
                    "type": int,
                    "default": None,
                    "help": "Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
                },
            ),
            (
                ("--channel-max-videos",),
                {
                    "type": int,
                    "default": 50,
                    "help": "Maximum candidate videos to inspect per channel feed (default: 50)",
                },
            ),
            (
                ("--no-scan-raw",),
                {
                    "action": "store_true",
                    "default": False,
                    "help": "Skip scanning existing local markdown transcripts in data/raw/",
                },
            ),
            (
                ("--no-crawl",),
                {
                    "action": "store_true",
                    "default": False,
                    "help": "Disable crawling channel feeds and strictly process manifest seed items",
                },
            ),
            (
                ("--web-index",),
                {
                    "action": "store_true",
                    "default": False,
                    "help": "Use Gemini API for raw transcript conceptual indexing instead of local Ollama",
                },
            ),
            (
                ("--channel",),
                {
                    "dest": "channels",
                    "nargs": "*",
                    "default": None,
                    "metavar": "CHANNEL",
                    "help": (
                        "Filter batch discovery to one or more channel names, handles, or URLs. "
                        "Accepts comma-separated values (e.g. --channel Ancapsu,Mises)."
                    ),
                },
            ),
            (
                ("--category", "-c"),
                {
                    "dest": "categories",
                    "nargs": "*",
                    "default": None,
                    "metavar": "CATEGORY",
                    "help": (
                        "Filter batch discovery by domain category or volatility type. "
                        "Domain names: politics_br, tech_ai, history, philosophy, finance, "
                        "engineering, architecture, health, entertainment, geopolitics. "
                        "Volatility: perennial, volatile. Accepts comma-separated values."
                    ),
                },
            ),
            (
                ("--video",),
                {
                    "dest": "video_ids",
                    "nargs": "*",
                    "default": None,
                    "metavar": "VIDEO_ID",
                    "help": (
                        "Restrict batch discovery to specific video IDs or YouTube watch URLs. "
                        "Accepts comma-separated values."
                    ),
                },
            ),
        ]

        assert mock_run_parser.add_argument.call_count == len(expected_calls)
        for args, kwargs in expected_calls:
            mock_run_parser.add_argument.assert_any_call(*args, **kwargs)

        mock_run_parser.set_defaults.assert_called_once_with(handler=mock_handler)

    def test_run_subparser_real_parsing_defaults(self) -> None:
        """Verify real ArgumentParser defaults for 'cresmo run'."""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="subcommand")
        handler = MagicMock()
        register_run_subparser(subparsers, handler=handler)

        args = parser.parse_args(["run"])
        assert args.url is None
        assert args.all is True
        assert args.manifest is None
        assert args.passes == 3
        assert args.batch_size is None
        assert args.dry_run is False
        assert args.force_reprocess is False
        assert args.lookback is None
        assert args.channel_max_videos == 50
        assert args.no_scan_raw is False
        assert args.no_crawl is False
        assert args.web_index is False
        assert args.channels is None
        assert args.categories is None
        assert args.video_ids is None
        assert args.handler is handler

    def test_run_subparser_real_parsing_custom_flags(self, tmp_path: Path) -> None:
        """Verify real ArgumentParser overrides for 'cresmo run' with custom flags."""
        manifest_path = tmp_path / "playlist.txt"
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="subcommand")
        handler = MagicMock()
        register_run_subparser(subparsers, handler=handler)

        args = parser.parse_args(
            [
                "run",
                "--url",
                "https://youtu.be/test1234",
                "--manifest",
                str(manifest_path),
                "--passes",
                "5",
                "--batch-size",
                "8",
                "--dry-run",
                "--force-reprocess",
                "--lookback",
                "180",
                "--channel-max-videos",
                "20",
                "--no-scan-raw",
                "--no-crawl",
                "--web-index",
                "--channel",
                "ChannelA",
                "ChannelB",
                "-c",
                "politics_br",
                "tech_ai",
                "--video",
                "vid1",
                "vid2",
            ]
        )

        assert args.url == "https://youtu.be/test1234"
        assert args.manifest == manifest_path
        assert args.passes == 5
        assert args.batch_size == 8
        assert args.dry_run is True
        assert args.force_reprocess is True
        assert args.lookback == 180
        assert args.channel_max_videos == 20
        assert args.no_scan_raw is True
        assert args.no_crawl is True
        assert args.web_index is True
        assert args.channels == ["ChannelA", "ChannelB"]
        assert args.categories == ["politics_br", "tech_ai"]
        assert args.video_ids == ["vid1", "vid2"]

    def test_run_subparser_playlist_alias_and_category_long_flag(self, tmp_path: Path) -> None:
        """Verify alias flags (--playlist, --category) parse correctly."""
        p_path = tmp_path / "alias.txt"
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="subcommand")
        handler = MagicMock()
        register_run_subparser(subparsers, handler=handler)

        args = parser.parse_args(
            [
                "run",
                "--playlist",
                str(p_path),
                "--category",
                "philosophy",
            ]
        )
        assert args.manifest == p_path
        assert args.categories == ["philosophy"]
