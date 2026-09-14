"""Command handler for cresmo sync."""

from __future__ import annotations

import argparse
import sys

from pydantic import ValidationError

from cresmo.domain.exceptions import (
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
    SecurityViolationError,
)
from cresmo.domain.value_objects import ChannelFeedQuery, PipelineStatus
from cresmo.presentation.composition import build_sync_channel_use_case
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
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_orig(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_1(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = None
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_2(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        None,
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_3(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help=None,
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_4(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_5(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_6(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "XXsyncXX",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_7(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "SYNC",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_8(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="XXPoll and synchronize video feeds from a YouTube channel or playlistXX",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_9(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="poll and synchronize video feeds from a youtube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_10(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="POLL AND SYNCHRONIZE VIDEO FEEDS FROM A YOUTUBE CHANNEL OR PLAYLIST",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_11(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        None,
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_12(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=None,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_13(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help=None,
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_14(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_15(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_16(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_17(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "XX--channelXX",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_18(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--CHANNEL",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_19(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=False,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_20(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="XXTarget YouTube channel or playlist URLXX",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_21(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="target youtube channel or playlist url",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_22(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="TARGET YOUTUBE CHANNEL OR PLAYLIST URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_23(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        None,
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_24(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=None,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_25(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=None,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_26(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help=None,
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_27(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_28(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_29(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_30(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_31(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "XX--lookbackXX",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_32(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--LOOKBACK",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_33(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 / 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_34(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 / 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_35(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=8 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_36(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 53 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_37(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 3,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_38(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="XXDays lookback window for new uploads (default: 2 years)XX",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_39(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_40(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="DAYS LOOKBACK WINDOW FOR NEW UPLOADS (DEFAULT: 2 YEARS)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_41(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        None,
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_42(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=None,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_43(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_44(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help=None,
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_45(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_46(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_47(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_48(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_49(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "XX--max-videosXX",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_50(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--MAX-VIDEOS",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_51(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=251,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_52(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="XXMaximum videos to discover and process in this run (default: 250)XX",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_53(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_54(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="MAXIMUM VIDEOS TO DISCOVER AND PROCESS IN THIS RUN (DEFAULT: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_55(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        None,
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_56(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=None,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_57(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=None,
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_58(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_59(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_60(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_61(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_62(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "XX--batch-sizeXX",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_63(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--BATCH-SIZE",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_64(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="XXBatch size override for atomic note synthesisXX",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_65(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_66(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="BATCH SIZE OVERRIDE FOR ATOMIC NOTE SYNTHESIS",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_67(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        None,
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_68(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action=None,
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_69(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help=None,
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_70(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_71(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_72(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_73(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "XX--dry-runXX",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_74(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--DRY-RUN",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_75(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="XXstore_trueXX",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_76(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="STORE_TRUE",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_77(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="XXDiscover and filter feed without executing LLM synthesis or ledger updatesXX",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_78(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="discover and filter feed without executing llm synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_79(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DISCOVER AND FILTER FEED WITHOUT EXECUTING LLM SYNTHESIS OR LEDGER UPDATES",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_80(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        None,
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_81(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action=None,
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_82(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help=None,
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_83(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_84(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_85(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_86(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "XX--force-refreshXX",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_87(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--FORCE-REFRESH",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_88(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="XXstore_trueXX",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_89(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="STORE_TRUE",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_90(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="XXForce re-synthesis even if content is already marked completed in ledgerXX",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_91(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_92(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="FORCE RE-SYNTHESIS EVEN IF CONTENT IS ALREADY MARKED COMPLETED IN LEDGER",
    )
    sync_parser.set_defaults(handler=handle_sync)


def x_register_subparser__mutmut_93(subparsers: argparse._SubParsersAction) -> None:
    """Register 'sync' subcommand parser with argument options."""
    sync_parser = subparsers.add_parser(
        "sync",
        help="Poll and synchronize video feeds from a YouTube channel or playlist",
    )
    sync_parser.add_argument(
        "--channel",
        required=True,
        help="Target YouTube channel or playlist URL",
    )
    sync_parser.add_argument(
        "--lookback",
        type=int,
        default=7 * 52 * 2,  # 2 years
        help="Days lookback window for new uploads (default: 2 years)",
    )
    sync_parser.add_argument(
        "--max-videos",
        type=int,
        default=250,
        help="Maximum videos to discover and process in this run (default: 250)",
    )
    sync_parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size override for atomic note synthesis",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and filter feed without executing LLM synthesis or ledger updates",
    )
    sync_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force re-synthesis even if content is already marked completed in ledger",
    )
    sync_parser.set_defaults(handler=None)

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
mutants_x_handle_sync__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_handle_sync__mutmut)
def handle_sync(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_orig(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_1(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = None
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_2(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=None)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_3(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = None
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_4(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=None,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_5(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=None,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_6(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=None,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_7(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_8(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_9(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_10(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = None

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_11(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=None,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_12(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=None,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_13(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=None,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_14(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_15(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_16(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_17(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write(None)
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_18(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("XXChannel Synchronization Summary:\nXX")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_19(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("channel synchronization summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_20(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("CHANNEL SYNCHRONIZATION SUMMARY:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_21(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_22(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_23(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_24(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_25(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_26(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(None)
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_27(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(None)

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_28(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED and summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_29(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status != PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_30(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count >= 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_31(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 1:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_32(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count >= 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_33(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 1:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_34(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(None)
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_35(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(None)
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_36(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(None)
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_37(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(None)
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_38(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(None)
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_39(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(None)
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected sync error: {exc}\n")
        return EXIT_INTERNAL_ERROR


def x_handle_sync__mutmut_40(args: argparse.Namespace) -> int:
    """Synchronize recent video uploads from a YouTube channel feed."""
    try:
        use_case = build_sync_channel_use_case(batch_size_override=args.batch_size)
        query = ChannelFeedQuery(
            channel_url=args.channel,
            lookback_days=args.lookback,
            max_videos=args.max_videos,
        )
        summary = use_case.execute(
            query=query,
            dry_run=args.dry_run,
            force_refresh=args.force_refresh,
        )

        sys.stdout.write("Channel Synchronization Summary:\n")
        sys.stdout.write(f"- Channel: {summary.channel_url}\n")
        sys.stdout.write(f"- Total in Window: {summary.total_discovered}\n")
        sys.stdout.write(f"- Processed: {summary.processed_count}\n")
        sys.stdout.write(f"- Skipped (Idempotent): {summary.skipped_count}\n")
        sys.stdout.write(f"- Failed: {summary.failed_count}\n")
        sys.stdout.write(f"- Duration: {summary.duration_seconds}s\n")
        sys.stdout.write(f"- Status: {summary.status.value}\n")

        if summary.status == PipelineStatus.COMPLETED or summary.processed_count > 0:
            return EXIT_SUCCESS
        if summary.failed_count > 0:
            return EXIT_INTERNAL_ERROR
        return EXIT_SUCCESS
    except RateLimitExceededError as exc:
        sys.stderr.write(f"Rate limit exceeded: {exc}\n")
        return EXIT_RATE_LIMIT_EXCEEDED
    except IngestionNetworkError as exc:
        sys.stderr.write(f"Ingestion network error: {exc}\n")
        return EXIT_INGESTION_ERROR
    except PreflightError as exc:
        sys.stderr.write(f"Preflight error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except DomainValidationError as exc:
        sys.stderr.write(f"Domain validation error: {exc}\n")
        return EXIT_DOMAIN_VALIDATION_ERROR
    except SecurityViolationError as exc:
        sys.stderr.write(f"Security boundary violation: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except ValidationError as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return EXIT_CONFIG_OR_USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(None)
        return EXIT_INTERNAL_ERROR

mutants_x_handle_sync__mutmut['_mutmut_orig'] = x_handle_sync__mutmut_orig # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_1'] = x_handle_sync__mutmut_1 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_2'] = x_handle_sync__mutmut_2 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_3'] = x_handle_sync__mutmut_3 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_4'] = x_handle_sync__mutmut_4 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_5'] = x_handle_sync__mutmut_5 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_6'] = x_handle_sync__mutmut_6 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_7'] = x_handle_sync__mutmut_7 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_8'] = x_handle_sync__mutmut_8 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_9'] = x_handle_sync__mutmut_9 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_10'] = x_handle_sync__mutmut_10 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_11'] = x_handle_sync__mutmut_11 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_12'] = x_handle_sync__mutmut_12 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_13'] = x_handle_sync__mutmut_13 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_14'] = x_handle_sync__mutmut_14 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_15'] = x_handle_sync__mutmut_15 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_16'] = x_handle_sync__mutmut_16 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_17'] = x_handle_sync__mutmut_17 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_18'] = x_handle_sync__mutmut_18 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_19'] = x_handle_sync__mutmut_19 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_20'] = x_handle_sync__mutmut_20 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_21'] = x_handle_sync__mutmut_21 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_22'] = x_handle_sync__mutmut_22 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_23'] = x_handle_sync__mutmut_23 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_24'] = x_handle_sync__mutmut_24 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_25'] = x_handle_sync__mutmut_25 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_26'] = x_handle_sync__mutmut_26 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_27'] = x_handle_sync__mutmut_27 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_28'] = x_handle_sync__mutmut_28 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_29'] = x_handle_sync__mutmut_29 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_30'] = x_handle_sync__mutmut_30 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_31'] = x_handle_sync__mutmut_31 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_32'] = x_handle_sync__mutmut_32 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_33'] = x_handle_sync__mutmut_33 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_34'] = x_handle_sync__mutmut_34 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_35'] = x_handle_sync__mutmut_35 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_36'] = x_handle_sync__mutmut_36 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_37'] = x_handle_sync__mutmut_37 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_38'] = x_handle_sync__mutmut_38 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_39'] = x_handle_sync__mutmut_39 # type: ignore # mutmut generated
mutants_x_handle_sync__mutmut['x_handle_sync__mutmut_40'] = x_handle_sync__mutmut_40 # type: ignore # mutmut generated
