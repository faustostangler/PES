"""Command handler for cresmo run."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.ports import MediaIngestionPort
from cresmo.application.use_cases.discover_batch_sources import (
    BatchDiscoveryQuery,
    BatchSource,
    DiscoverBatchSourcesUseCase,
)
from cresmo.domain.exceptions import (
    CresmoDomainError,
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import (
    build_discover_batch_sources_use_case,
    build_pipeline,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_register_subparser__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_register_subparser__mutmut)
def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_orig(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_1(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = None
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_2(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        None,
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_3(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help=None,
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_4(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_5(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_6(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "XXrunXX",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_7(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "RUN",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_8(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="XXRun end-to-end knowledge synthesis for a video or manifest playlistXX",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_9(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_10(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="RUN END-TO-END KNOWLEDGE SYNTHESIS FOR A VIDEO OR MANIFEST PLAYLIST",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_11(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        None,
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_12(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=None,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_13(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help=None,
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_14(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_15(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_16(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_17(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_18(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "XX--urlXX",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_19(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--URL",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_20(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=True,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_21(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="XXTarget YouTube or media video URLXX",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_22(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="target youtube or media video url",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_23(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="TARGET YOUTUBE OR MEDIA VIDEO URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_24(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        None,
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_25(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action=None,
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_26(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=None,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_27(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help=None,
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_28(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_29(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_30(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_31(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_32(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "XX--allXX",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_33(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--ALL",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_34(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="XXstore_trueXX",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_35(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="STORE_TRUE",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_36(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_37(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="XX(Default) Run full pipeline for all videos in the manifest playlistsXX",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_38(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(default) run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_39(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(DEFAULT) RUN FULL PIPELINE FOR ALL VIDEOS IN THE MANIFEST PLAYLISTS",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_40(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        None,
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_41(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        None,
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_42(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=None,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_43(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help=None,
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_44(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_45(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_46(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_47(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_48(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_49(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "XX--manifestXX",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_50(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--MANIFEST",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_51(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "XX--playlistXX",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_52(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--PLAYLIST",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_53(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="XXPath to manifest or playlist text file (default: data/playlist.txt)XX",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_54(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_55(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="PATH TO MANIFEST OR PLAYLIST TEXT FILE (DEFAULT: DATA/PLAYLIST.TXT)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_56(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        None,
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_57(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=None,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_58(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=None,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_59(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help=None,
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_60(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_61(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_62(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_63(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_64(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "XX--passesXX",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_65(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--PASSES",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_66(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=4,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_67(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="XXRefinement passes for gap filler (default: 3)XX",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_68(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_69(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="REFINEMENT PASSES FOR GAP FILLER (DEFAULT: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_70(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        None,
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_71(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=None,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_72(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=None,
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_73(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_74(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_75(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_76(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_77(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "XX--batch-sizeXX",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_78(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--BATCH-SIZE",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_79(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="XXBatch size override for atomic note synthesisXX",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_80(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_81(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="BATCH SIZE OVERRIDE FOR ATOMIC NOTE SYNTHESIS",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_82(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        None,
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_83(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action=None,
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_84(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help=None,
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_85(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_86(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_87(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_88(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "XX--dry-runXX",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_89(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--DRY-RUN",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_90(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="XXstore_trueXX",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_91(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="STORE_TRUE",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_92(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="XXIngest raw transcript without executing generative LLM synthesisXX",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_93(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ingest raw transcript without executing generative llm synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_94(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="INGEST RAW TRANSCRIPT WITHOUT EXECUTING GENERATIVE LLM SYNTHESIS",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_95(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        None,
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_96(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action=None,
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_97(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help=None,
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_98(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_99(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_100(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_101(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "XX--force-reprocessXX",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_102(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--FORCE-REPROCESS",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_103(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="XXstore_trueXX",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_104(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="STORE_TRUE",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_105(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="XXBypass ledger idempotency guard and re-synthesize even if already completedXX",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_106(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_107(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="BYPASS LEDGER IDEMPOTENCY GUARD AND RE-SYNTHESIZE EVEN IF ALREADY COMPLETED",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_108(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        None,
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_109(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=None,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_110(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help=None,
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_111(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_112(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_113(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_114(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_115(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "XX--lookbackXX",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_116(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--LOOKBACK",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_117(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="XXDays lookback window for channel uploads discovery (default: 365 days / 1 year)XX",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_118(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_119(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="DAYS LOOKBACK WINDOW FOR CHANNEL UPLOADS DISCOVERY (DEFAULT: 365 DAYS / 1 YEAR)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_120(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        None,
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_121(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=None,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_122(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=None,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_123(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help=None,
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_124(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_125(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_126(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_127(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_128(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "XX--channel-max-videosXX",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_129(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--CHANNEL-MAX-VIDEOS",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_130(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=51,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_131(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="XXMaximum candidate videos to inspect per channel feed (default: 50)XX",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_132(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_133(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="MAXIMUM CANDIDATE VIDEOS TO INSPECT PER CHANNEL FEED (DEFAULT: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_134(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        None,
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_135(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action=None,
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_136(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=None,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_137(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help=None,
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_138(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_139(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_140(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_141(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_142(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "XX--no-scan-rawXX",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_143(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--NO-SCAN-RAW",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_144(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="XXstore_trueXX",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_145(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="STORE_TRUE",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_146(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=True,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_147(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="XXSkip scanning existing local markdown transcripts in data/raw/XX",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_148(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_149(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="SKIP SCANNING EXISTING LOCAL MARKDOWN TRANSCRIPTS IN DATA/RAW/",
    )
    run_parser.set_defaults(handler=handle_run)


def x_register_subparser__mutmut_150(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video or manifest playlist",
    )
    run_parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="(Default) Run full pipeline for all videos in the manifest playlists",
    )
    run_parser.add_argument(
        "--manifest",
        "--playlist",
        type=Path,
        default=None,
        help="Path to manifest or playlist text file (default: data/playlist.txt)",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Refinement passes for gap filler (default: 3)",
    )
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest raw transcript without executing generative LLM synthesis",
    )
    run_parser.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Bypass ledger idempotency guard and re-synthesize even if already completed",
    )
    run_parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Days lookback window for channel uploads discovery (default: 365 days / 1 year)",
    )
    run_parser.add_argument(
        "--channel-max-videos",
        type=int,
        default=50,
        help="Maximum candidate videos to inspect per channel feed (default: 50)",
    )
    run_parser.add_argument(
        "--no-scan-raw",
        action="store_true",
        default=False,
        help="Skip scanning existing local markdown transcripts in data/raw/",
    )
    run_parser.set_defaults(handler=None)

mutants_x_register_subparser__mutmut['_mutmut_orig'] = x_register_subparser__mutmut_orig # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_1'] = x_register_subparser__mutmut_1 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_2'] = x_register_subparser__mutmut_2 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_3'] = x_register_subparser__mutmut_3 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_4'] = x_register_subparser__mutmut_4 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_5'] = x_register_subparser__mutmut_5 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_6'] = x_register_subparser__mutmut_6 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_7'] = x_register_subparser__mutmut_7 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_8'] = x_register_subparser__mutmut_8 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_9'] = x_register_subparser__mutmut_9 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_10'] = x_register_subparser__mutmut_10 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_11'] = x_register_subparser__mutmut_11 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_12'] = x_register_subparser__mutmut_12 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_13'] = x_register_subparser__mutmut_13 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_14'] = x_register_subparser__mutmut_14 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_15'] = x_register_subparser__mutmut_15 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_16'] = x_register_subparser__mutmut_16 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_17'] = x_register_subparser__mutmut_17 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_18'] = x_register_subparser__mutmut_18 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_19'] = x_register_subparser__mutmut_19 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_20'] = x_register_subparser__mutmut_20 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_21'] = x_register_subparser__mutmut_21 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_22'] = x_register_subparser__mutmut_22 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_23'] = x_register_subparser__mutmut_23 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_24'] = x_register_subparser__mutmut_24 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_25'] = x_register_subparser__mutmut_25 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_26'] = x_register_subparser__mutmut_26 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_27'] = x_register_subparser__mutmut_27 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_28'] = x_register_subparser__mutmut_28 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_29'] = x_register_subparser__mutmut_29 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_30'] = x_register_subparser__mutmut_30 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_31'] = x_register_subparser__mutmut_31 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_32'] = x_register_subparser__mutmut_32 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_33'] = x_register_subparser__mutmut_33 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_34'] = x_register_subparser__mutmut_34 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_35'] = x_register_subparser__mutmut_35 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_36'] = x_register_subparser__mutmut_36 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_37'] = x_register_subparser__mutmut_37 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_38'] = x_register_subparser__mutmut_38 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_39'] = x_register_subparser__mutmut_39 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_40'] = x_register_subparser__mutmut_40 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_41'] = x_register_subparser__mutmut_41 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_42'] = x_register_subparser__mutmut_42 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_43'] = x_register_subparser__mutmut_43 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_44'] = x_register_subparser__mutmut_44 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_45'] = x_register_subparser__mutmut_45 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_46'] = x_register_subparser__mutmut_46 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_47'] = x_register_subparser__mutmut_47 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_48'] = x_register_subparser__mutmut_48 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_49'] = x_register_subparser__mutmut_49 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_50'] = x_register_subparser__mutmut_50 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_51'] = x_register_subparser__mutmut_51 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_52'] = x_register_subparser__mutmut_52 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_53'] = x_register_subparser__mutmut_53 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_54'] = x_register_subparser__mutmut_54 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_55'] = x_register_subparser__mutmut_55 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_56'] = x_register_subparser__mutmut_56 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_57'] = x_register_subparser__mutmut_57 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_58'] = x_register_subparser__mutmut_58 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_59'] = x_register_subparser__mutmut_59 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_60'] = x_register_subparser__mutmut_60 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_61'] = x_register_subparser__mutmut_61 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_62'] = x_register_subparser__mutmut_62 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_63'] = x_register_subparser__mutmut_63 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_64'] = x_register_subparser__mutmut_64 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_65'] = x_register_subparser__mutmut_65 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_66'] = x_register_subparser__mutmut_66 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_67'] = x_register_subparser__mutmut_67 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_68'] = x_register_subparser__mutmut_68 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_69'] = x_register_subparser__mutmut_69 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_70'] = x_register_subparser__mutmut_70 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_71'] = x_register_subparser__mutmut_71 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_72'] = x_register_subparser__mutmut_72 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_73'] = x_register_subparser__mutmut_73 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_74'] = x_register_subparser__mutmut_74 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_75'] = x_register_subparser__mutmut_75 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_76'] = x_register_subparser__mutmut_76 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_77'] = x_register_subparser__mutmut_77 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_78'] = x_register_subparser__mutmut_78 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_79'] = x_register_subparser__mutmut_79 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_80'] = x_register_subparser__mutmut_80 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_81'] = x_register_subparser__mutmut_81 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_82'] = x_register_subparser__mutmut_82 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_83'] = x_register_subparser__mutmut_83 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_84'] = x_register_subparser__mutmut_84 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_85'] = x_register_subparser__mutmut_85 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_86'] = x_register_subparser__mutmut_86 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_87'] = x_register_subparser__mutmut_87 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_88'] = x_register_subparser__mutmut_88 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_89'] = x_register_subparser__mutmut_89 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_90'] = x_register_subparser__mutmut_90 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_91'] = x_register_subparser__mutmut_91 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_92'] = x_register_subparser__mutmut_92 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_93'] = x_register_subparser__mutmut_93 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_94'] = x_register_subparser__mutmut_94 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_95'] = x_register_subparser__mutmut_95 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_96'] = x_register_subparser__mutmut_96 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_97'] = x_register_subparser__mutmut_97 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_98'] = x_register_subparser__mutmut_98 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_99'] = x_register_subparser__mutmut_99 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_100'] = x_register_subparser__mutmut_100 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_101'] = x_register_subparser__mutmut_101 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_102'] = x_register_subparser__mutmut_102 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_103'] = x_register_subparser__mutmut_103 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_104'] = x_register_subparser__mutmut_104 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_105'] = x_register_subparser__mutmut_105 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_106'] = x_register_subparser__mutmut_106 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_107'] = x_register_subparser__mutmut_107 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_108'] = x_register_subparser__mutmut_108 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_109'] = x_register_subparser__mutmut_109 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_110'] = x_register_subparser__mutmut_110 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_111'] = x_register_subparser__mutmut_111 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_112'] = x_register_subparser__mutmut_112 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_113'] = x_register_subparser__mutmut_113 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_114'] = x_register_subparser__mutmut_114 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_115'] = x_register_subparser__mutmut_115 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_116'] = x_register_subparser__mutmut_116 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_117'] = x_register_subparser__mutmut_117 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_118'] = x_register_subparser__mutmut_118 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_119'] = x_register_subparser__mutmut_119 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_120'] = x_register_subparser__mutmut_120 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_121'] = x_register_subparser__mutmut_121 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_122'] = x_register_subparser__mutmut_122 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_123'] = x_register_subparser__mutmut_123 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_124'] = x_register_subparser__mutmut_124 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_125'] = x_register_subparser__mutmut_125 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_126'] = x_register_subparser__mutmut_126 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_127'] = x_register_subparser__mutmut_127 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_128'] = x_register_subparser__mutmut_128 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_129'] = x_register_subparser__mutmut_129 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_130'] = x_register_subparser__mutmut_130 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_131'] = x_register_subparser__mutmut_131 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_132'] = x_register_subparser__mutmut_132 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_133'] = x_register_subparser__mutmut_133 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_134'] = x_register_subparser__mutmut_134 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_135'] = x_register_subparser__mutmut_135 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_136'] = x_register_subparser__mutmut_136 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_137'] = x_register_subparser__mutmut_137 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_138'] = x_register_subparser__mutmut_138 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_139'] = x_register_subparser__mutmut_139 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_140'] = x_register_subparser__mutmut_140 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_141'] = x_register_subparser__mutmut_141 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_142'] = x_register_subparser__mutmut_142 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_143'] = x_register_subparser__mutmut_143 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_144'] = x_register_subparser__mutmut_144 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_145'] = x_register_subparser__mutmut_145 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_146'] = x_register_subparser__mutmut_146 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_147'] = x_register_subparser__mutmut_147 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_148'] = x_register_subparser__mutmut_148 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_149'] = x_register_subparser__mutmut_149 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_150'] = x_register_subparser__mutmut_150 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_execute_single_video_run__mutmut)
def execute_single_video_run(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_orig(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_1(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = None
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_2(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=None)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_3(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is not None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_4(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(None)
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_5(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            None
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_6(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = None
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_7(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=None,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_8(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=None,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_9(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=None,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_10(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_11(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_12(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_13(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            None
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_14(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            None
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_15(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video."""
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content_id.value}]: "
            f"Transcript length: {len(raw.body)} characters.\n"
        )
        return EXIT_SUCCESS

    result = pipeline.run_for_video(
        video_url=args.url,
        gap_filler_passes=args.passes,
        force_reprocess=args.force_reprocess,
    )
    if result.already_processed:
        sys.stdout.write(
            f"[SKIPPED] Content [{result.content_id.value}] was already marked as COMPLETED "
            f"in the ledger. Use --force-reprocess to bypass.\n"
        )
        return EXIT_SUCCESS
    if result.success:
        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(None)
    return EXIT_INTERNAL_ERROR

mutants_x_execute_single_video_run__mutmut['_mutmut_orig'] = x_execute_single_video_run__mutmut_orig # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_1'] = x_execute_single_video_run__mutmut_1 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_2'] = x_execute_single_video_run__mutmut_2 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_3'] = x_execute_single_video_run__mutmut_3 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_4'] = x_execute_single_video_run__mutmut_4 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_5'] = x_execute_single_video_run__mutmut_5 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_6'] = x_execute_single_video_run__mutmut_6 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_7'] = x_execute_single_video_run__mutmut_7 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_8'] = x_execute_single_video_run__mutmut_8 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_9'] = x_execute_single_video_run__mutmut_9 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_10'] = x_execute_single_video_run__mutmut_10 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_11'] = x_execute_single_video_run__mutmut_11 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_12'] = x_execute_single_video_run__mutmut_12 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_13'] = x_execute_single_video_run__mutmut_13 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_14'] = x_execute_single_video_run__mutmut_14 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_15'] = x_execute_single_video_run__mutmut_15 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_execute_batch_dry_run__mutmut)
def execute_batch_dry_run(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_orig(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_1(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = None
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_2(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 1
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_3(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(None, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_4(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, None):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_5(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_6(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, ):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_7(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 2):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_8(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind != "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_9(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "XXfileXX":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_10(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "FILE":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_11(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = None
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_12(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(None)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_13(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested = 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_14(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested -= 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_15(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 2
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_16(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                None
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_17(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = None
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_18(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=None)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_19(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_20(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested = 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_21(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested -= 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_22(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 2
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_23(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    None
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_24(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(None)
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_25(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages."""
    ingested = 0
    for idx, src in enumerate(sources, 1):
        if src.kind == "file":
            fpath = Path(src.target)
            ingested += 1
            sys.stdout.write(
                f"[{idx}/{len(sources)}] Dry-run text: [{fpath.stem}] ({fpath.stat().st_size} bytes)\n"
            )
        else:
            raw = pipeline.ingest_raw_transcript.execute(video_url=src.target)
            if raw is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] Dry-run ingested: [{raw.content_id.value}] "
                    f"({len(raw.body)} chars)\n"
                )
            else:
                sys.stderr.write(f"[{idx}/{len(sources)}] Ingestion failed for: {src.target}\n")
    sys.stdout.write(None)
    return EXIT_SUCCESS

mutants_x_execute_batch_dry_run__mutmut['_mutmut_orig'] = x_execute_batch_dry_run__mutmut_orig # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_1'] = x_execute_batch_dry_run__mutmut_1 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_2'] = x_execute_batch_dry_run__mutmut_2 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_3'] = x_execute_batch_dry_run__mutmut_3 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_4'] = x_execute_batch_dry_run__mutmut_4 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_5'] = x_execute_batch_dry_run__mutmut_5 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_6'] = x_execute_batch_dry_run__mutmut_6 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_7'] = x_execute_batch_dry_run__mutmut_7 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_8'] = x_execute_batch_dry_run__mutmut_8 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_9'] = x_execute_batch_dry_run__mutmut_9 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_10'] = x_execute_batch_dry_run__mutmut_10 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_11'] = x_execute_batch_dry_run__mutmut_11 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_12'] = x_execute_batch_dry_run__mutmut_12 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_13'] = x_execute_batch_dry_run__mutmut_13 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_14'] = x_execute_batch_dry_run__mutmut_14 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_15'] = x_execute_batch_dry_run__mutmut_15 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_16'] = x_execute_batch_dry_run__mutmut_16 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_17'] = x_execute_batch_dry_run__mutmut_17 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_18'] = x_execute_batch_dry_run__mutmut_18 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_19'] = x_execute_batch_dry_run__mutmut_19 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_20'] = x_execute_batch_dry_run__mutmut_20 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_21'] = x_execute_batch_dry_run__mutmut_21 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_22'] = x_execute_batch_dry_run__mutmut_22 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_23'] = x_execute_batch_dry_run__mutmut_23 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_24'] = x_execute_batch_dry_run__mutmut_24 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_25'] = x_execute_batch_dry_run__mutmut_25 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_execute_batch_run__mutmut)
def execute_batch_run(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_orig(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_1(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = None
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_2(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 1
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_3(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = None
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_4(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 1
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_5(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = None

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_6(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 1

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_7(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(None, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_8(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, None):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_9(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_10(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, ):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_11(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 2):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_12(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind != "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_13(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "XXfileXX":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_14(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "FILE":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_15(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = None
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_16(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=None,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_17(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=None,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_18(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=None,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_19(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_20(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_21(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_22(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(None),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_23(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = None

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_24(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=None,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_25(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=None,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_26(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=None,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_27(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_28(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_29(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_30(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = None
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_31(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped = 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_32(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped -= 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_33(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 2
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_34(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    None
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_35(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed = 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_36(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed -= 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_37(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 2
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_38(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    None
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_39(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed = 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_40(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed -= 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_41(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 2
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_42(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    None
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_43(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed = 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_44(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed -= 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_45(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 2
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_46(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(None)
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_47(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed = 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_48(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed -= 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_49(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 2
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_50(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(None)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_51(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed = 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_52(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed -= 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_53(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 2
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_54(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(None)

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_55(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        None
    )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_56(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed != 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_57(
    pipeline: CresmoPipeline,
    sources: list[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources."""
    completed = 0
    skipped = 0
    failed = 0

    for idx, src in enumerate(sources, 1):
        try:
            if src.kind == "file":
                result = pipeline.run_for_text_file(
                    file_path=Path(src.target),
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=src.target,
                    gap_filler_passes=args.passes,
                    force_reprocess=args.force_reprocess,
                )

            display_target = src.target
            if result.already_processed:
                skipped += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [SKIPPED] [{result.content_id.value}] Already processed in ledger.\n"
                )
            elif result.success:
                completed += 1
                sys.stdout.write(
                    f"[{idx}/{len(sources)}] [DONE] [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled, "
                    f"{result.duplicates_unified} duplicate clusters unified.\n"
                )
            else:
                failed += 1
                sys.stderr.write(
                    f"[{idx}/{len(sources)}] [ERROR] {display_target}: {result.error_message}\n"
                )
        except RateLimitExceededError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [RATE LIMIT] {src.target}: {exc}\n")
        except IngestionNetworkError as exc:
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [NETWORK ERROR] {src.target}: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stderr.write(f"[{idx}/{len(sources)}] [FAILED] {src.target}: {exc}\n")

    sys.stdout.write(
        f"\nBatch Synthesis Summary:\n"
        f"- Total Items: {len(sources)}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )
    return EXIT_SUCCESS if failed == 1 else EXIT_INTERNAL_ERROR

mutants_x_execute_batch_run__mutmut['_mutmut_orig'] = x_execute_batch_run__mutmut_orig # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_1'] = x_execute_batch_run__mutmut_1 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_2'] = x_execute_batch_run__mutmut_2 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_3'] = x_execute_batch_run__mutmut_3 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_4'] = x_execute_batch_run__mutmut_4 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_5'] = x_execute_batch_run__mutmut_5 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_6'] = x_execute_batch_run__mutmut_6 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_7'] = x_execute_batch_run__mutmut_7 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_8'] = x_execute_batch_run__mutmut_8 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_9'] = x_execute_batch_run__mutmut_9 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_10'] = x_execute_batch_run__mutmut_10 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_11'] = x_execute_batch_run__mutmut_11 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_12'] = x_execute_batch_run__mutmut_12 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_13'] = x_execute_batch_run__mutmut_13 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_14'] = x_execute_batch_run__mutmut_14 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_15'] = x_execute_batch_run__mutmut_15 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_16'] = x_execute_batch_run__mutmut_16 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_17'] = x_execute_batch_run__mutmut_17 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_18'] = x_execute_batch_run__mutmut_18 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_19'] = x_execute_batch_run__mutmut_19 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_20'] = x_execute_batch_run__mutmut_20 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_21'] = x_execute_batch_run__mutmut_21 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_22'] = x_execute_batch_run__mutmut_22 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_23'] = x_execute_batch_run__mutmut_23 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_24'] = x_execute_batch_run__mutmut_24 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_25'] = x_execute_batch_run__mutmut_25 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_26'] = x_execute_batch_run__mutmut_26 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_27'] = x_execute_batch_run__mutmut_27 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_28'] = x_execute_batch_run__mutmut_28 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_29'] = x_execute_batch_run__mutmut_29 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_30'] = x_execute_batch_run__mutmut_30 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_31'] = x_execute_batch_run__mutmut_31 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_32'] = x_execute_batch_run__mutmut_32 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_33'] = x_execute_batch_run__mutmut_33 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_34'] = x_execute_batch_run__mutmut_34 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_35'] = x_execute_batch_run__mutmut_35 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_36'] = x_execute_batch_run__mutmut_36 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_37'] = x_execute_batch_run__mutmut_37 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_38'] = x_execute_batch_run__mutmut_38 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_39'] = x_execute_batch_run__mutmut_39 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_40'] = x_execute_batch_run__mutmut_40 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_41'] = x_execute_batch_run__mutmut_41 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_42'] = x_execute_batch_run__mutmut_42 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_43'] = x_execute_batch_run__mutmut_43 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_44'] = x_execute_batch_run__mutmut_44 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_45'] = x_execute_batch_run__mutmut_45 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_46'] = x_execute_batch_run__mutmut_46 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_47'] = x_execute_batch_run__mutmut_47 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_48'] = x_execute_batch_run__mutmut_48 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_49'] = x_execute_batch_run__mutmut_49 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_50'] = x_execute_batch_run__mutmut_50 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_51'] = x_execute_batch_run__mutmut_51 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_52'] = x_execute_batch_run__mutmut_52 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_53'] = x_execute_batch_run__mutmut_53 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_54'] = x_execute_batch_run__mutmut_54 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_55'] = x_execute_batch_run__mutmut_55 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_56'] = x_execute_batch_run__mutmut_56 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_57'] = x_execute_batch_run__mutmut_57 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_load_batch_sources__mutmut)
def load_batch_sources(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_orig(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_1(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = None
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_2(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings and CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_3(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is not None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_4(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = None
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_5(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=None,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_6(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=None,
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_7(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_8(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_9(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: None,
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_10(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(None),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_11(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = None
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_12(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=None,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_13(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=None,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_14(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=None,
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_15(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_16(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_17(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_18(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: None,
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_19(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(None),
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_20(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    resolved_settings = settings or CresmoSettings()
    if media_ingestion_port is None:
        discovery_use_case = build_discover_batch_sources_use_case(
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    else:
        discovery_use_case = DiscoverBatchSourcesUseCase(
            media_ingestion_port=media_ingestion_port,
            settings=resolved_settings,
            progress_callback=lambda msg: sys.stdout.write(msg),
        )
    return discovery_use_case.execute(query=None)

mutants_x_load_batch_sources__mutmut['_mutmut_orig'] = x_load_batch_sources__mutmut_orig # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_1'] = x_load_batch_sources__mutmut_1 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_2'] = x_load_batch_sources__mutmut_2 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_3'] = x_load_batch_sources__mutmut_3 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_4'] = x_load_batch_sources__mutmut_4 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_5'] = x_load_batch_sources__mutmut_5 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_6'] = x_load_batch_sources__mutmut_6 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_7'] = x_load_batch_sources__mutmut_7 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_8'] = x_load_batch_sources__mutmut_8 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_9'] = x_load_batch_sources__mutmut_9 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_10'] = x_load_batch_sources__mutmut_10 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_11'] = x_load_batch_sources__mutmut_11 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_12'] = x_load_batch_sources__mutmut_12 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_13'] = x_load_batch_sources__mutmut_13 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_14'] = x_load_batch_sources__mutmut_14 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_15'] = x_load_batch_sources__mutmut_15 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_16'] = x_load_batch_sources__mutmut_16 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_17'] = x_load_batch_sources__mutmut_17 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_18'] = x_load_batch_sources__mutmut_18 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_19'] = x_load_batch_sources__mutmut_19 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut['x_load_batch_sources__mutmut_20'] = x_load_batch_sources__mutmut_20 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_handle_run__mutmut)
def handle_run(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_orig(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_1(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = None

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_2(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=None)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_3(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_4(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(None, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_5(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, None)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_6(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_7(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, )

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_8(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = None
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_9(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_10(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = None

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_11(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = None
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_12(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=None,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_13(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=None,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_14(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=None,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_15(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=None,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_16(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=None,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_17(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_18(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_19(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_20(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_21(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_22(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_23(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = None

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_24(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=None, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_25(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=None)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_26(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_27(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, )

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_28(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_29(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = None
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_30(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(None) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_31(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "XXdata/playlist.txtXX"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_32(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "DATA/PLAYLIST.TXT"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_33(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                None
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_34(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_35(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(None, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_36(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, None)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_37(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_38(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, )

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_39(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(None, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_40(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, None, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_41(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, None)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_42(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_43(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_44(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, )
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_45(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(None)
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_46(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(None)
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_47(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(None)
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_48(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(None)
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_49(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(None)
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected internal error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_run__mutmut_50(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest."""
    try:
        pipeline = (
            build_pipeline(batch_size_override=args.batch_size)
            if args.batch_size is not None
            else build_pipeline()
        )

        if args.url:
            return execute_single_video_run(pipeline, args)

        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()
        query = BatchDiscoveryQuery(
            explicit_manifest=args.manifest,
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
            discovery_workers=settings.channel_discovery_workers,
        )
        sources = load_batch_sources(query=query, settings=settings)

        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS

        if args.dry_run:
            return execute_batch_dry_run(pipeline, sources)

        return execute_batch_run(pipeline, sources, args)
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except (DomainValidationError, CresmoDomainError) as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(None)
        return EXIT_INTERNAL_ERROR

mutants_x_handle_run__mutmut['_mutmut_orig'] = x_handle_run__mutmut_orig # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_1'] = x_handle_run__mutmut_1 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_2'] = x_handle_run__mutmut_2 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_3'] = x_handle_run__mutmut_3 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_4'] = x_handle_run__mutmut_4 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_5'] = x_handle_run__mutmut_5 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_6'] = x_handle_run__mutmut_6 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_7'] = x_handle_run__mutmut_7 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_8'] = x_handle_run__mutmut_8 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_9'] = x_handle_run__mutmut_9 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_10'] = x_handle_run__mutmut_10 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_11'] = x_handle_run__mutmut_11 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_12'] = x_handle_run__mutmut_12 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_13'] = x_handle_run__mutmut_13 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_14'] = x_handle_run__mutmut_14 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_15'] = x_handle_run__mutmut_15 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_16'] = x_handle_run__mutmut_16 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_17'] = x_handle_run__mutmut_17 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_18'] = x_handle_run__mutmut_18 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_19'] = x_handle_run__mutmut_19 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_20'] = x_handle_run__mutmut_20 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_21'] = x_handle_run__mutmut_21 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_22'] = x_handle_run__mutmut_22 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_23'] = x_handle_run__mutmut_23 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_24'] = x_handle_run__mutmut_24 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_25'] = x_handle_run__mutmut_25 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_26'] = x_handle_run__mutmut_26 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_27'] = x_handle_run__mutmut_27 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_28'] = x_handle_run__mutmut_28 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_29'] = x_handle_run__mutmut_29 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_30'] = x_handle_run__mutmut_30 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_31'] = x_handle_run__mutmut_31 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_32'] = x_handle_run__mutmut_32 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_33'] = x_handle_run__mutmut_33 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_34'] = x_handle_run__mutmut_34 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_35'] = x_handle_run__mutmut_35 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_36'] = x_handle_run__mutmut_36 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_37'] = x_handle_run__mutmut_37 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_38'] = x_handle_run__mutmut_38 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_39'] = x_handle_run__mutmut_39 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_40'] = x_handle_run__mutmut_40 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_41'] = x_handle_run__mutmut_41 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_42'] = x_handle_run__mutmut_42 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_43'] = x_handle_run__mutmut_43 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_44'] = x_handle_run__mutmut_44 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_45'] = x_handle_run__mutmut_45 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_46'] = x_handle_run__mutmut_46 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_47'] = x_handle_run__mutmut_47 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_48'] = x_handle_run__mutmut_48 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_49'] = x_handle_run__mutmut_49 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut['x_handle_run__mutmut_50'] = x_handle_run__mutmut_50 # type: ignore # mutmut generated
