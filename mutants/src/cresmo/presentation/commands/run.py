"""Command handler for cresmo run.

Orchestrates full knowledge synthesis for individual media items or prioritized
batch runs across playlists, priority texts, and channel upload feeds.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-007: Pipeline Template Method DRY
    - ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
    - SPEC-001: Core Knowledge Synthesis Specifications
    - SPEC-002: CLI Controller & Exit Codes
    - ADR-026: Clean Code Anti-Patterns & Code Smell Governance
"""

from __future__ import annotations

import argparse
import gc
import logging
import sys
from collections.abc import Iterable, Iterator, Sized
from pathlib import Path

from pydantic import ValidationError

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.ports import MediaIngestionPort
from cresmo.application.use_cases.discover_batch_sources import (
    BatchDiscoveryQuery,
    BatchSource,
)
from cresmo.domain.exceptions import (
    CresmoDomainError,
    DomainValidationError,
    IngestionNetworkError,
    PreflightError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import (
    BatchId,
    ChannelName,
    SourceModality,
    SyncFilterCriteria,
    is_processable_transcript_file,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.infrastructure.system import get_process_rss_bytes
from cresmo.presentation.commands.run_parser import register_run_subparser
from cresmo.presentation.composition import (
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_pipeline,
    build_preflight_checker,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_DOMAIN_VALIDATION_ERROR,
    EXIT_INGESTION_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_RATE_LIMIT_EXCEEDED,
    EXIT_SUCCESS,
)

logger = logging.getLogger(__name__)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_register_subparser__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_register_subparser__mutmut)
def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    register_run_subparser(subparsers, handler=handle_run)


def x_register_subparser__mutmut_orig(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    register_run_subparser(subparsers, handler=handle_run)


def x_register_subparser__mutmut_1(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    register_run_subparser(None, handler=handle_run)


def x_register_subparser__mutmut_2(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    register_run_subparser(subparsers, handler=None)


def x_register_subparser__mutmut_3(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    register_run_subparser(handler=handle_run)


def x_register_subparser__mutmut_4(subparsers: argparse._SubParsersAction) -> None:
    """Register 'run' subcommand parser with argument options."""
    register_run_subparser(subparsers, )

mutants_x_register_subparser__mutmut['_mutmut_orig'] = x_register_subparser__mutmut_orig # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_1'] = x_register_subparser__mutmut_1 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_2'] = x_register_subparser__mutmut_2 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_3'] = x_register_subparser__mutmut_3 # type: ignore # mutmut generated
mutants_x_register_subparser__mutmut['x_register_subparser__mutmut_4'] = x_register_subparser__mutmut_4 # type: ignore # mutmut generated
mutants_x_handle_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_handle_run__mutmut)
def handle_run(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = None
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = None

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = None
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=None, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=None)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, )
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=False)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = None
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(None)

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = None

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=None,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=None,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=None,
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(None, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, None, False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", None),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr("web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", ),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "XXweb_indexXX", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "WEB_INDEX", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", True),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(None, settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, None, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, None)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(settings, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, pipeline)
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, )
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
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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


def x_handle_run__mutmut_35(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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


def x_handle_run__mutmut_36(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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


def x_handle_run__mutmut_37(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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


def x_handle_run__mutmut_38(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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


def x_handle_run__mutmut_39(args: argparse.Namespace) -> int:
    """Orchestrate knowledge synthesis pipeline for single video or batch manifest.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    try:
        settings = CresmoSettings()
        if args.lookback is not None:
            settings.days_lookback = args.lookback

        settings.ensure_directories()

        # Active Preflight Validation
        preflight_checker = build_preflight_checker(settings=settings, check_ffmpeg=True)
        preflight_res = preflight_checker.check_all()
        preflight_res.assert_healthy()
        for warning in preflight_res.warnings:
            sys.stderr.write(f"[preflight warning] {warning}\n")

        pipeline = build_pipeline(
            settings=settings,
            batch_size_override=args.batch_size,
            web_index=getattr(args, "web_index", False),
        )

        return _execute_run_pipeline(args, settings, pipeline)
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
mutants_x__execute_run_pipeline__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__execute_run_pipeline__mutmut)
def _execute_run_pipeline(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_orig(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_1(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_2(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(None, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_3(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, None, False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_4(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", None):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_5(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr("web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_6(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_7(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", ):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_8(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "XXweb_indexXX", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_9(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "WEB_INDEX", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_10(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", True):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_11(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(None, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_12(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, None)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_13(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_14(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, )

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_15(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = None

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_16(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(None, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_17(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, None)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_18(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_19(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, )

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_20(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = None
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_21(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            None
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_22(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=None,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_23(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=None,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_24(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=None,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_25(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_26(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_27(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_28(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_29(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = None
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_30(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(None) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_31(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "XXdata/playlist.txtXX"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_32(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "DATA/PLAYLIST.TXT"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_33(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                None
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_34(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_35(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(None, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_36(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, None)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_37(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_38(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, )

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_39(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = None
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_40(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=None,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_41(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=None,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_42(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=None,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_43(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_44(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_45(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        )
    return execute_batch_run(pipeline, sources, args)


def x__execute_run_pipeline__mutmut_46(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(None, sources, args)


def x__execute_run_pipeline__mutmut_47(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, None, args)


def x__execute_run_pipeline__mutmut_48(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, None)


def x__execute_run_pipeline__mutmut_49(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(sources, args)


def x__execute_run_pipeline__mutmut_50(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, args)


def x__execute_run_pipeline__mutmut_51(
    args: argparse.Namespace,
    settings: CresmoSettings,
    pipeline: CresmoPipeline,
) -> int:
    """Execute the configured pipeline for single video or batch mode."""
    if not getattr(args, "web_index", False):
        pipeline.warmup()

    if args.url:
        return execute_single_video_run(pipeline, args)

    query = _build_batch_discovery_query(args, settings)

    if args.dry_run:
        sources = list(
            load_batch_sources(
                query=query,
                settings=settings,
                media_ingestion_port=pipeline.media_ingestion_port,
            )
        )
        if not sources:
            manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
            sys.stdout.write(
                f"No sources found to process (manifest: {manifest_display}, "
                f"raw lake scan: {not args.no_scan_raw}).\n"
            )
            return EXIT_SUCCESS
        return execute_batch_dry_run(pipeline, sources)

    sources = load_batch_sources(
        query=query,
        settings=settings,
        media_ingestion_port=pipeline.media_ingestion_port,
    )
    return execute_batch_run(pipeline, sources, )

mutants_x__execute_run_pipeline__mutmut['_mutmut_orig'] = x__execute_run_pipeline__mutmut_orig # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_1'] = x__execute_run_pipeline__mutmut_1 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_2'] = x__execute_run_pipeline__mutmut_2 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_3'] = x__execute_run_pipeline__mutmut_3 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_4'] = x__execute_run_pipeline__mutmut_4 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_5'] = x__execute_run_pipeline__mutmut_5 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_6'] = x__execute_run_pipeline__mutmut_6 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_7'] = x__execute_run_pipeline__mutmut_7 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_8'] = x__execute_run_pipeline__mutmut_8 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_9'] = x__execute_run_pipeline__mutmut_9 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_10'] = x__execute_run_pipeline__mutmut_10 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_11'] = x__execute_run_pipeline__mutmut_11 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_12'] = x__execute_run_pipeline__mutmut_12 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_13'] = x__execute_run_pipeline__mutmut_13 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_14'] = x__execute_run_pipeline__mutmut_14 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_15'] = x__execute_run_pipeline__mutmut_15 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_16'] = x__execute_run_pipeline__mutmut_16 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_17'] = x__execute_run_pipeline__mutmut_17 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_18'] = x__execute_run_pipeline__mutmut_18 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_19'] = x__execute_run_pipeline__mutmut_19 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_20'] = x__execute_run_pipeline__mutmut_20 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_21'] = x__execute_run_pipeline__mutmut_21 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_22'] = x__execute_run_pipeline__mutmut_22 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_23'] = x__execute_run_pipeline__mutmut_23 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_24'] = x__execute_run_pipeline__mutmut_24 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_25'] = x__execute_run_pipeline__mutmut_25 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_26'] = x__execute_run_pipeline__mutmut_26 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_27'] = x__execute_run_pipeline__mutmut_27 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_28'] = x__execute_run_pipeline__mutmut_28 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_29'] = x__execute_run_pipeline__mutmut_29 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_30'] = x__execute_run_pipeline__mutmut_30 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_31'] = x__execute_run_pipeline__mutmut_31 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_32'] = x__execute_run_pipeline__mutmut_32 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_33'] = x__execute_run_pipeline__mutmut_33 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_34'] = x__execute_run_pipeline__mutmut_34 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_35'] = x__execute_run_pipeline__mutmut_35 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_36'] = x__execute_run_pipeline__mutmut_36 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_37'] = x__execute_run_pipeline__mutmut_37 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_38'] = x__execute_run_pipeline__mutmut_38 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_39'] = x__execute_run_pipeline__mutmut_39 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_40'] = x__execute_run_pipeline__mutmut_40 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_41'] = x__execute_run_pipeline__mutmut_41 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_42'] = x__execute_run_pipeline__mutmut_42 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_43'] = x__execute_run_pipeline__mutmut_43 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_44'] = x__execute_run_pipeline__mutmut_44 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_45'] = x__execute_run_pipeline__mutmut_45 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_46'] = x__execute_run_pipeline__mutmut_46 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_47'] = x__execute_run_pipeline__mutmut_47 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_48'] = x__execute_run_pipeline__mutmut_48 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_49'] = x__execute_run_pipeline__mutmut_49 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_50'] = x__execute_run_pipeline__mutmut_50 # type: ignore # mutmut generated
mutants_x__execute_run_pipeline__mutmut['x__execute_run_pipeline__mutmut_51'] = x__execute_run_pipeline__mutmut_51 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_execute_single_video_run__mutmut)
def execute_single_video_run(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = None
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=None)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is not None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(None)
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = None
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_15(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(None)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_16(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw or raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_17(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = None
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_18(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_19(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=None,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_20(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_21(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_22(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(None)
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_23(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(None))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_24(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(None)

        sys.stdout.write(
            f"Synthesis completed successfully for [{result.content_id.value}]: "
            f"{len(result.synthesized_notes)} atomic notes synthesized, "
            f"{len(result.reconciled_mocs)} MOCs reconciled, "
            f"{result.duplicates_unified} duplicate clusters unified.\n"
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_25(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

        sys.stdout.write(
            None
        )
        return EXIT_SUCCESS

    sys.stderr.write(f"Pipeline error: {result.error_message}\n")
    return EXIT_INTERNAL_ERROR


def x_execute_single_video_run__mutmut_26(pipeline: CresmoPipeline, args: argparse.Namespace) -> int:
    """Execute knowledge synthesis or dry run for a single target video.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        args: Parsed CLI argument namespace containing URL, passes, and flags.

    Returns:
        Process exit code integer.
    """
    if args.dry_run:
        raw = pipeline.ingest_raw_transcript.execute(video_url=args.url)
        if raw is None:
            sys.stderr.write(f"Dry-run ingestion returned no transcript for {args.url}\n")
            return EXIT_INGESTION_ERROR
        sys.stdout.write(
            f"Dry run successful for [{raw.content.id.value}]: "
            f"Transcript length: {len(raw.content.body)} characters.\n"
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
        try:
            raw = pipeline.vault_port.get_raw_transcript(result.content_id)
            if raw and raw.channel.name:
                concat_master = build_concat_master_use_case(
                    settings=pipeline.settings
                    if isinstance(pipeline.settings, CresmoSettings)
                    else None,
                    vault_port=pipeline.vault_port,
                )
                concat_master.execute(ChannelName(raw.channel.name))
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")

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
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_16'] = x_execute_single_video_run__mutmut_16 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_17'] = x_execute_single_video_run__mutmut_17 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_18'] = x_execute_single_video_run__mutmut_18 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_19'] = x_execute_single_video_run__mutmut_19 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_20'] = x_execute_single_video_run__mutmut_20 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_21'] = x_execute_single_video_run__mutmut_21 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_22'] = x_execute_single_video_run__mutmut_22 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_23'] = x_execute_single_video_run__mutmut_23 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_24'] = x_execute_single_video_run__mutmut_24 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_25'] = x_execute_single_video_run__mutmut_25 # type: ignore # mutmut generated
mutants_x_execute_single_video_run__mutmut['x_execute_single_video_run__mutmut_26'] = x_execute_single_video_run__mutmut_26 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_execute_batch_run__mutmut)
def execute_batch_run(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_orig(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_1(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = None
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_2(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 1
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_3(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = None
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_4(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 1
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_5(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = None
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_6(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 1
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_7(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = None

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_8(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = None

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_9(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else "XXXX"

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_10(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(None, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_11(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, None):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_12(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_13(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, ):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_14(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 2):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_15(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = None
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_16(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = None
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_17(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=None,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_18(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=None,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_19(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=None,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_20(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=None,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_21(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=None,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_22(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_23(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_24(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_25(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_26(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_27(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status != "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_28(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "XXcompletedXX":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_29(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "COMPLETED":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_30(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed = 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_31(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed -= 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_32(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 2
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_33(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status != "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_34(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "XXskippedXX":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_35(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "SKIPPED":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_36(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped = 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_37(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped -= 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_38(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 2
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_39(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed = 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_40(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed -= 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_41(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 2
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_42(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(None)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_43(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = None

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_44(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped - failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_45(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed - skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_46(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items != 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_47(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 1:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_48(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = None
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_49(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(None) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_50(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "XXdata/playlist.txtXX"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_51(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "DATA/PLAYLIST.TXT"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_52(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            None
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_53(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_54(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        None
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_55(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(None, completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_56(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, None)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_57(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(completed)
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_58(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, )
    return EXIT_SUCCESS if failed == 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_59(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
    return EXIT_SUCCESS if failed != 0 else EXIT_INTERNAL_ERROR


def x_execute_batch_run__mutmut_60(
    pipeline: CresmoPipeline,
    sources: Iterable[BatchSource],
    args: argparse.Namespace,
) -> int:
    """Execute end-to-end multi-pass synthesis over prioritized batch sources.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: Iterable stream of prioritized BatchSource items.
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code integer.
    """
    completed = 0
    skipped = 0
    failed = 0
    batch_id = BatchId.generate()

    total_count_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

    for source_index, source in enumerate(sources, 1):
        item_prefix = f"[{source_index}{total_count_suffix}]"
        try:
            status = _process_single_batch_item(
                pipeline=pipeline,
                source=source,
                args=args,
                item_prefix=item_prefix,
                batch_id=batch_id,
            )
            if status == "completed":
                completed += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1
        finally:
            _drain_telemetry_and_memory(pipeline)

    total_items = completed + skipped + failed

    if total_items == 0:
        manifest_display = str(args.manifest) if args.manifest else "data/playlist.txt"
        sys.stdout.write(
            f"No sources found to process (manifest: {manifest_display}, "
            f"raw lake scan: {not args.no_scan_raw}).\n"
        )
        return EXIT_SUCCESS

    sys.stdout.write(
        f"\nBatch Synthesis Summary [Batch: {batch_id.value}]:\n"
        f"- Total Items: {total_items}\n"
        f"- Completed: {completed}\n"
        f"- Skipped (Idempotent): {skipped}\n"
        f"- Failed: {failed}\n"
    )

    _consolidate_master_if_needed(pipeline, completed)
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
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_58'] = x_execute_batch_run__mutmut_58 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_59'] = x_execute_batch_run__mutmut_59 # type: ignore # mutmut generated
mutants_x_execute_batch_run__mutmut['x_execute_batch_run__mutmut_60'] = x_execute_batch_run__mutmut_60 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_execute_batch_dry_run__mutmut)
def execute_batch_dry_run(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_orig(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_1(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = None
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_2(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 1
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_3(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(None, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_4(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, None):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_5(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_6(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, ):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_7(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 2):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_8(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is not SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_9(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = None
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_10(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(None)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_11(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_12(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(None):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_13(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    None
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_14(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                break
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_15(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested = 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_16(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested -= 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_17(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 2
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_18(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                None
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_19(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = None
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_20(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=None)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_21(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_22(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested = 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_23(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested -= 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_24(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 2
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_25(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    None
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_26(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    None
                )
    sys.stdout.write(f"Dry-run completed: {ingested}/{len(sources)} items validated.\n")
    return EXIT_SUCCESS


def x_execute_batch_dry_run__mutmut_27(pipeline: CresmoPipeline, sources: list[BatchSource]) -> int:
    """Inspect and validate batch sources without invoking generative LLM stages.

    Args:
        pipeline: Wired CresmoPipeline orchestrator.
        sources: List of discovered BatchSource items to test.

    Returns:
        Process exit code integer.
    """
    ingested = 0
    for source_index, source in enumerate(sources, 1):
        if source.kind is SourceModality.FILE:
            file_path = Path(source.target)
            if not is_processable_transcript_file(file_path):
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run skipped artifact: [{file_path.name}]\n"
                )
                continue
            ingested += 1
            sys.stdout.write(
                f"[{source_index}/{len(sources)}] Dry-run text: [{file_path.stem}] "
                f"({file_path.stat().st_size} bytes)\n"
            )
        else:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
            if raw_transcript is not None:
                ingested += 1
                sys.stdout.write(
                    f"[{source_index}/{len(sources)}] Dry-run ingested: [{raw_transcript.content.id.value}] "
                    f"({len(raw_transcript.content.body)} chars)\n"
                )
            else:
                sys.stderr.write(
                    f"[{source_index}/{len(sources)}] Ingestion failed for: {source.target}\n"
                )
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
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_26'] = x_execute_batch_dry_run__mutmut_26 # type: ignore # mutmut generated
mutants_x_execute_batch_dry_run__mutmut['x_execute_batch_dry_run__mutmut_27'] = x_execute_batch_dry_run__mutmut_27 # type: ignore # mutmut generated
mutants_x_load_batch_sources__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_load_batch_sources__mutmut)
def load_batch_sources(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=media_ingestion_port,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_orig(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=media_ingestion_port,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_1(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = None
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_2(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=None,
        media_ingestion_port=media_ingestion_port,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_3(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=None,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_4(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=media_ingestion_port,
        progress_callback=None,
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_5(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        media_ingestion_port=media_ingestion_port,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_6(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_7(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=media_ingestion_port,
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_8(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=media_ingestion_port,
        progress_callback=lambda msg: None,
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_9(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=media_ingestion_port,
        progress_callback=lambda msg: sys.stdout.write(None),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_10(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
    media_ingestion_port: MediaIngestionPort | None = None,
) -> Iterator[BatchSource]:
    """Execute streaming batch source discovery via DiscoverBatchSourcesUseCase.

    Conforms to ADR-010 (Streaming-First Unification), ADR-026 (Anti-Defensive Fallback),
    and ADR-026 (Rule 11: Anti-Bifurcated Construction).

    Args:
        query: BatchDiscoveryQuery constraints.
        settings: Validated application settings.
        media_ingestion_port: Ingestion adapter port instance.

    Returns:
        Streaming iterator of BatchSource records.
    """
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        media_ingestion_port=media_ingestion_port,
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
mutants_x__build_batch_discovery_query__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__build_batch_discovery_query__mutmut)
def _build_batch_discovery_query(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_orig(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_1(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = None

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_2(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        True
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_3(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(None, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_4(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, None, False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_5(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", None)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_6(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr("no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_7(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_8(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", )
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_9(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "XXno_crawlXX", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_10(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "NO_CRAWL", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_11(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", True)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_12(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(None, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_13(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, None, True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_14(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", None)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_15(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr("enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_16(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_17(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", )
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_18(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "XXenable_channel_crawlerXX", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_19(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "ENABLE_CHANNEL_CRAWLER", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_20(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", False)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_21(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = None

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_22(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=None,
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_23(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=None,
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_24(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=None,
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_25(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_26(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_27(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_28(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) and [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_29(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(None, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_30(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, None, None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_31(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr("channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_32(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_33(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", ) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_34(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "XXchannelsXX", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_35(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "CHANNELS", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_36(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) and [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_37(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(None, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_38(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, None, None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_39(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr("categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_40(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_41(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", ) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_42(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "XXcategoriesXX", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_43(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "CATEGORIES", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_44(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) and [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_45(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(None, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_46(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, None, None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_47(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr("video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_48(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_49(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", ) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_50(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "XXvideo_idsXX", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_51(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "VIDEO_IDS", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_52(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=None,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_53(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=None,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_54(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=None,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_55(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=None,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_56(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=None,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_57(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=None,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_58(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=None,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_59(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=None,
    )


def x__build_batch_discovery_query__mutmut_60(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_61(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_62(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_63(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_64(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_65(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_66(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        queue_maxsize=settings.discovery_queue_maxsize,
    )


def x__build_batch_discovery_query__mutmut_67(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=not args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        )


def x__build_batch_discovery_query__mutmut_68(
    args: argparse.Namespace,
    settings: CresmoSettings,
) -> BatchDiscoveryQuery:
    """Build strongly-typed discovery query from parsed CLI arguments and settings."""
    enable_crawl = (
        False
        if getattr(args, "no_crawl", False)
        else getattr(settings, "enable_channel_crawler", True)
    )

    filter_criteria = SyncFilterCriteria.from_strings(
        channels=getattr(args, "channels", None) or [],
        categories=getattr(args, "categories", None) or [],
        video_ids=getattr(args, "video_ids", None) or [],
    )

    return BatchDiscoveryQuery(
        explicit_manifest=args.manifest,
        scan_raw=args.no_scan_raw,
        lookback_days=settings.days_lookback,
        channel_max_videos=args.channel_max_videos,
        discovery_workers=settings.channel_discovery_workers,
        enable_channel_crawler=enable_crawl,
        filter_criteria=filter_criteria,
        queue_maxsize=settings.discovery_queue_maxsize,
    )

mutants_x__build_batch_discovery_query__mutmut['_mutmut_orig'] = x__build_batch_discovery_query__mutmut_orig # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_1'] = x__build_batch_discovery_query__mutmut_1 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_2'] = x__build_batch_discovery_query__mutmut_2 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_3'] = x__build_batch_discovery_query__mutmut_3 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_4'] = x__build_batch_discovery_query__mutmut_4 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_5'] = x__build_batch_discovery_query__mutmut_5 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_6'] = x__build_batch_discovery_query__mutmut_6 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_7'] = x__build_batch_discovery_query__mutmut_7 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_8'] = x__build_batch_discovery_query__mutmut_8 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_9'] = x__build_batch_discovery_query__mutmut_9 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_10'] = x__build_batch_discovery_query__mutmut_10 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_11'] = x__build_batch_discovery_query__mutmut_11 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_12'] = x__build_batch_discovery_query__mutmut_12 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_13'] = x__build_batch_discovery_query__mutmut_13 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_14'] = x__build_batch_discovery_query__mutmut_14 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_15'] = x__build_batch_discovery_query__mutmut_15 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_16'] = x__build_batch_discovery_query__mutmut_16 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_17'] = x__build_batch_discovery_query__mutmut_17 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_18'] = x__build_batch_discovery_query__mutmut_18 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_19'] = x__build_batch_discovery_query__mutmut_19 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_20'] = x__build_batch_discovery_query__mutmut_20 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_21'] = x__build_batch_discovery_query__mutmut_21 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_22'] = x__build_batch_discovery_query__mutmut_22 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_23'] = x__build_batch_discovery_query__mutmut_23 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_24'] = x__build_batch_discovery_query__mutmut_24 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_25'] = x__build_batch_discovery_query__mutmut_25 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_26'] = x__build_batch_discovery_query__mutmut_26 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_27'] = x__build_batch_discovery_query__mutmut_27 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_28'] = x__build_batch_discovery_query__mutmut_28 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_29'] = x__build_batch_discovery_query__mutmut_29 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_30'] = x__build_batch_discovery_query__mutmut_30 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_31'] = x__build_batch_discovery_query__mutmut_31 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_32'] = x__build_batch_discovery_query__mutmut_32 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_33'] = x__build_batch_discovery_query__mutmut_33 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_34'] = x__build_batch_discovery_query__mutmut_34 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_35'] = x__build_batch_discovery_query__mutmut_35 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_36'] = x__build_batch_discovery_query__mutmut_36 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_37'] = x__build_batch_discovery_query__mutmut_37 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_38'] = x__build_batch_discovery_query__mutmut_38 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_39'] = x__build_batch_discovery_query__mutmut_39 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_40'] = x__build_batch_discovery_query__mutmut_40 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_41'] = x__build_batch_discovery_query__mutmut_41 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_42'] = x__build_batch_discovery_query__mutmut_42 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_43'] = x__build_batch_discovery_query__mutmut_43 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_44'] = x__build_batch_discovery_query__mutmut_44 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_45'] = x__build_batch_discovery_query__mutmut_45 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_46'] = x__build_batch_discovery_query__mutmut_46 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_47'] = x__build_batch_discovery_query__mutmut_47 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_48'] = x__build_batch_discovery_query__mutmut_48 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_49'] = x__build_batch_discovery_query__mutmut_49 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_50'] = x__build_batch_discovery_query__mutmut_50 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_51'] = x__build_batch_discovery_query__mutmut_51 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_52'] = x__build_batch_discovery_query__mutmut_52 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_53'] = x__build_batch_discovery_query__mutmut_53 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_54'] = x__build_batch_discovery_query__mutmut_54 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_55'] = x__build_batch_discovery_query__mutmut_55 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_56'] = x__build_batch_discovery_query__mutmut_56 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_57'] = x__build_batch_discovery_query__mutmut_57 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_58'] = x__build_batch_discovery_query__mutmut_58 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_59'] = x__build_batch_discovery_query__mutmut_59 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_60'] = x__build_batch_discovery_query__mutmut_60 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_61'] = x__build_batch_discovery_query__mutmut_61 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_62'] = x__build_batch_discovery_query__mutmut_62 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_63'] = x__build_batch_discovery_query__mutmut_63 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_64'] = x__build_batch_discovery_query__mutmut_64 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_65'] = x__build_batch_discovery_query__mutmut_65 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_66'] = x__build_batch_discovery_query__mutmut_66 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_67'] = x__build_batch_discovery_query__mutmut_67 # type: ignore # mutmut generated
mutants_x__build_batch_discovery_query__mutmut['x__build_batch_discovery_query__mutmut_68'] = x__build_batch_discovery_query__mutmut_68 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__process_single_batch_item__mutmut)
def _process_single_batch_item(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_orig(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_1(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is not SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_2(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = None
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_3(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(None)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_4(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_5(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(None):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_6(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    None
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_7(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "XXIgnored internal Cresmo artifact or system index.\nXX"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_8(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "ignored internal cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_9(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "IGNORED INTERNAL CRESMO ARTIFACT OR SYSTEM INDEX.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_10(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "XXskippedXX"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_11(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "SKIPPED"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_12(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = None
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_13(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=None,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_14(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=None,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_15(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=None,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_16(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=None,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_17(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_18(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_19(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_20(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_21(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = None

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_22(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=None,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_23(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=None,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_24(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=None,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_25(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=None,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_26(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_27(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_28(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_29(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_30(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                None
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_31(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "XXAlready processed in ledger.\nXX"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_32(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_33(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "ALREADY PROCESSED IN LEDGER.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_34(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "XXskippedXX"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_35(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "SKIPPED"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_36(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                None
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_37(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "XXcompletedXX"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_38(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "COMPLETED"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_39(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(None)
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_40(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "XXfailedXX"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_41(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "FAILED"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_42(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(None)
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_43(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "XXfailedXX"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_44(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "FAILED"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_45(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(None)
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_46(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "XXfailedXX"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_47(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "FAILED"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "failed"


def x__process_single_batch_item__mutmut_48(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(None)
        return "failed"


def x__process_single_batch_item__mutmut_49(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "XXfailedXX"


def x__process_single_batch_item__mutmut_50(
    pipeline: CresmoPipeline,
    source: BatchSource,
    args: argparse.Namespace,
    item_prefix: str,
    batch_id: BatchId | None = None,
) -> str:
    """Execute pipeline for a single batch item and report console outcome.

    Returns:
        Status string: 'completed', 'skipped', or 'failed'.
    """
    try:
        if source.kind is SourceModality.FILE:
            target_path = Path(source.target)
            if not is_processable_transcript_file(target_path):
                sys.stdout.write(
                    f"{item_prefix} [SKIPPED] [{target_path.name}] "
                    "Ignored internal Cresmo artifact or system index.\n"
                )
                return "skipped"
            result = pipeline.run_for_text_file(
                file_path=target_path,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )
        else:
            result = pipeline.run_for_video(
                video_url=source.target,
                gap_filler_passes=args.passes,
                force_reprocess=args.force_reprocess,
                batch_id=batch_id,
            )

        if result.already_processed:
            sys.stdout.write(
                f"{item_prefix} [SKIPPED] [{result.content_id.value}] "
                "Already processed in ledger.\n"
            )
            return "skipped"
        if result.success:
            sys.stdout.write(
                f"{item_prefix} [DONE] [{result.content_id.value}]: "
                f"{len(result.synthesized_notes)} atomic notes synthesized, "
                f"{len(result.reconciled_mocs)} MOCs reconciled, "
                f"{result.duplicates_unified} duplicate clusters unified.\n"
            )
            return "completed"

        sys.stderr.write(f"{item_prefix} [ERROR] {source.target}: {result.error_message}\n")
        return "failed"
    except RateLimitExceededError as exc:
        sys.stderr.write(f"{item_prefix} [RATE LIMIT] {source.target}: {exc}\n")
        return "failed"
    except IngestionNetworkError as exc:
        sys.stderr.write(f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}\n")
        return "failed"
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"{item_prefix} [FAILED] {source.target}: {exc}\n")
        return "FAILED"

mutants_x__process_single_batch_item__mutmut['_mutmut_orig'] = x__process_single_batch_item__mutmut_orig # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_1'] = x__process_single_batch_item__mutmut_1 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_2'] = x__process_single_batch_item__mutmut_2 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_3'] = x__process_single_batch_item__mutmut_3 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_4'] = x__process_single_batch_item__mutmut_4 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_5'] = x__process_single_batch_item__mutmut_5 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_6'] = x__process_single_batch_item__mutmut_6 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_7'] = x__process_single_batch_item__mutmut_7 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_8'] = x__process_single_batch_item__mutmut_8 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_9'] = x__process_single_batch_item__mutmut_9 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_10'] = x__process_single_batch_item__mutmut_10 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_11'] = x__process_single_batch_item__mutmut_11 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_12'] = x__process_single_batch_item__mutmut_12 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_13'] = x__process_single_batch_item__mutmut_13 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_14'] = x__process_single_batch_item__mutmut_14 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_15'] = x__process_single_batch_item__mutmut_15 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_16'] = x__process_single_batch_item__mutmut_16 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_17'] = x__process_single_batch_item__mutmut_17 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_18'] = x__process_single_batch_item__mutmut_18 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_19'] = x__process_single_batch_item__mutmut_19 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_20'] = x__process_single_batch_item__mutmut_20 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_21'] = x__process_single_batch_item__mutmut_21 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_22'] = x__process_single_batch_item__mutmut_22 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_23'] = x__process_single_batch_item__mutmut_23 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_24'] = x__process_single_batch_item__mutmut_24 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_25'] = x__process_single_batch_item__mutmut_25 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_26'] = x__process_single_batch_item__mutmut_26 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_27'] = x__process_single_batch_item__mutmut_27 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_28'] = x__process_single_batch_item__mutmut_28 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_29'] = x__process_single_batch_item__mutmut_29 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_30'] = x__process_single_batch_item__mutmut_30 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_31'] = x__process_single_batch_item__mutmut_31 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_32'] = x__process_single_batch_item__mutmut_32 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_33'] = x__process_single_batch_item__mutmut_33 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_34'] = x__process_single_batch_item__mutmut_34 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_35'] = x__process_single_batch_item__mutmut_35 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_36'] = x__process_single_batch_item__mutmut_36 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_37'] = x__process_single_batch_item__mutmut_37 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_38'] = x__process_single_batch_item__mutmut_38 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_39'] = x__process_single_batch_item__mutmut_39 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_40'] = x__process_single_batch_item__mutmut_40 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_41'] = x__process_single_batch_item__mutmut_41 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_42'] = x__process_single_batch_item__mutmut_42 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_43'] = x__process_single_batch_item__mutmut_43 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_44'] = x__process_single_batch_item__mutmut_44 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_45'] = x__process_single_batch_item__mutmut_45 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_46'] = x__process_single_batch_item__mutmut_46 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_47'] = x__process_single_batch_item__mutmut_47 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_48'] = x__process_single_batch_item__mutmut_48 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_49'] = x__process_single_batch_item__mutmut_49 # type: ignore # mutmut generated
mutants_x__process_single_batch_item__mutmut['x__process_single_batch_item__mutmut_50'] = x__process_single_batch_item__mutmut_50 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__consolidate_master_if_needed__mutmut)
def _consolidate_master_if_needed(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_orig(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_1(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed < 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_2(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 1:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_3(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write(None)
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_4(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("XX\nConsolidating master compendiums for RAG...\nXX")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_5(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nconsolidating master compendiums for rag...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_6(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nCONSOLIDATING MASTER COMPENDIUMS FOR RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_7(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = None
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_8(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_9(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=None,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_10(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_11(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_12(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = None
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_13(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = None
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_14(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(None)
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_15(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            None
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Warning: Master consolidation failed: {exc}\n")


def x__consolidate_master_if_needed__mutmut_16(pipeline: CresmoPipeline, completed: int) -> None:
    """Trigger master document consolidation if at least one item was completed."""
    if completed <= 0:
        return
    try:
        sys.stdout.write("\nConsolidating master compendiums for RAG...\n")
        concat_master = build_concat_master_use_case(
            settings=pipeline.settings if isinstance(pipeline.settings, CresmoSettings) else None,
            vault_port=pipeline.vault_port,
        )
        master_results = concat_master.execute_all()
        total_parts = sum(len(parts) for parts in master_results.values())
        sys.stdout.write(
            f"Master consolidation complete: {total_parts} master document(s) generated "
            f"across {len(master_results)} channel(s).\n"
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(None)

mutants_x__consolidate_master_if_needed__mutmut['_mutmut_orig'] = x__consolidate_master_if_needed__mutmut_orig # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_1'] = x__consolidate_master_if_needed__mutmut_1 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_2'] = x__consolidate_master_if_needed__mutmut_2 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_3'] = x__consolidate_master_if_needed__mutmut_3 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_4'] = x__consolidate_master_if_needed__mutmut_4 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_5'] = x__consolidate_master_if_needed__mutmut_5 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_6'] = x__consolidate_master_if_needed__mutmut_6 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_7'] = x__consolidate_master_if_needed__mutmut_7 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_8'] = x__consolidate_master_if_needed__mutmut_8 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_9'] = x__consolidate_master_if_needed__mutmut_9 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_10'] = x__consolidate_master_if_needed__mutmut_10 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_11'] = x__consolidate_master_if_needed__mutmut_11 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_12'] = x__consolidate_master_if_needed__mutmut_12 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_13'] = x__consolidate_master_if_needed__mutmut_13 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_14'] = x__consolidate_master_if_needed__mutmut_14 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_15'] = x__consolidate_master_if_needed__mutmut_15 # type: ignore # mutmut generated
mutants_x__consolidate_master_if_needed__mutmut['x__consolidate_master_if_needed__mutmut_16'] = x__consolidate_master_if_needed__mutmut_16 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__drain_telemetry_and_memory__mutmut)
def _drain_telemetry_and_memory(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_orig(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_1(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug(None, exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_2(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", None)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_3(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug(exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_4(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", )
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_5(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("XX[run] Telemetry flush skipped or failed during cleanup: %sXX", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_6(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_7(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[RUN] TELEMETRY FLUSH SKIPPED OR FAILED DURING CLEANUP: %S", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_8(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = None
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_9(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            None,
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_10(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            None,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_11(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels=None,
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_12(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_13(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_14(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_15(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "XXcresmo_process_resident_memory_bytesXX",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_16(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "CRESMO_PROCESS_RESIDENT_MEMORY_BYTES",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_17(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"XXroleXX": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_18(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"ROLE": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_19(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "XXworkerXX"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_20(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "WORKER"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_21(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            None,
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_22(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            None,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_23(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels=None,
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_24(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_25(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_26(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_27(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "XXcresmo_gc_collections_totalXX",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_28(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "CRESMO_GC_COLLECTIONS_TOTAL",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_29(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            2.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_30(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"XXgenerationXX": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_31(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"GENERATION": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_32(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "XXallXX"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_33(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "ALL"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_34(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug(None, exc)


def x__drain_telemetry_and_memory__mutmut_35(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", None)


def x__drain_telemetry_and_memory__mutmut_36(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug(exc)


def x__drain_telemetry_and_memory__mutmut_37(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Process metrics emission failed during cleanup: %s", )


def x__drain_telemetry_and_memory__mutmut_38(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("XX[run] Process metrics emission failed during cleanup: %sXX", exc)


def x__drain_telemetry_and_memory__mutmut_39(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] process metrics emission failed during cleanup: %s", exc)


def x__drain_telemetry_and_memory__mutmut_40(pipeline: CresmoPipeline) -> None:
    """Drain telemetry queues and perform garbage collection per ADR-020 & SPEC-008."""
    try:
        pipeline.telemetry_port.flush()
    except Exception as exc:  # noqa: BLE001
        logger.debug("[run] Telemetry flush skipped or failed during cleanup: %s", exc)
    gc.collect()
    try:
        rss_bytes = get_process_rss_bytes()
        pipeline.metrics_port.set_gauge(
            "cresmo_process_resident_memory_bytes",
            rss_bytes,
            labels={"role": "worker"},
        )
        pipeline.metrics_port.increment_counter(
            "cresmo_gc_collections_total",
            1.0,
            labels={"generation": "all"},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("[RUN] PROCESS METRICS EMISSION FAILED DURING CLEANUP: %S", exc)

mutants_x__drain_telemetry_and_memory__mutmut['_mutmut_orig'] = x__drain_telemetry_and_memory__mutmut_orig # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_1'] = x__drain_telemetry_and_memory__mutmut_1 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_2'] = x__drain_telemetry_and_memory__mutmut_2 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_3'] = x__drain_telemetry_and_memory__mutmut_3 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_4'] = x__drain_telemetry_and_memory__mutmut_4 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_5'] = x__drain_telemetry_and_memory__mutmut_5 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_6'] = x__drain_telemetry_and_memory__mutmut_6 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_7'] = x__drain_telemetry_and_memory__mutmut_7 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_8'] = x__drain_telemetry_and_memory__mutmut_8 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_9'] = x__drain_telemetry_and_memory__mutmut_9 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_10'] = x__drain_telemetry_and_memory__mutmut_10 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_11'] = x__drain_telemetry_and_memory__mutmut_11 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_12'] = x__drain_telemetry_and_memory__mutmut_12 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_13'] = x__drain_telemetry_and_memory__mutmut_13 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_14'] = x__drain_telemetry_and_memory__mutmut_14 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_15'] = x__drain_telemetry_and_memory__mutmut_15 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_16'] = x__drain_telemetry_and_memory__mutmut_16 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_17'] = x__drain_telemetry_and_memory__mutmut_17 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_18'] = x__drain_telemetry_and_memory__mutmut_18 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_19'] = x__drain_telemetry_and_memory__mutmut_19 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_20'] = x__drain_telemetry_and_memory__mutmut_20 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_21'] = x__drain_telemetry_and_memory__mutmut_21 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_22'] = x__drain_telemetry_and_memory__mutmut_22 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_23'] = x__drain_telemetry_and_memory__mutmut_23 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_24'] = x__drain_telemetry_and_memory__mutmut_24 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_25'] = x__drain_telemetry_and_memory__mutmut_25 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_26'] = x__drain_telemetry_and_memory__mutmut_26 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_27'] = x__drain_telemetry_and_memory__mutmut_27 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_28'] = x__drain_telemetry_and_memory__mutmut_28 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_29'] = x__drain_telemetry_and_memory__mutmut_29 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_30'] = x__drain_telemetry_and_memory__mutmut_30 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_31'] = x__drain_telemetry_and_memory__mutmut_31 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_32'] = x__drain_telemetry_and_memory__mutmut_32 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_33'] = x__drain_telemetry_and_memory__mutmut_33 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_34'] = x__drain_telemetry_and_memory__mutmut_34 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_35'] = x__drain_telemetry_and_memory__mutmut_35 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_36'] = x__drain_telemetry_and_memory__mutmut_36 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_37'] = x__drain_telemetry_and_memory__mutmut_37 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_38'] = x__drain_telemetry_and_memory__mutmut_38 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_39'] = x__drain_telemetry_and_memory__mutmut_39 # type: ignore # mutmut generated
mutants_x__drain_telemetry_and_memory__mutmut['x__drain_telemetry_and_memory__mutmut_40'] = x__drain_telemetry_and_memory__mutmut_40 # type: ignore # mutmut generated
