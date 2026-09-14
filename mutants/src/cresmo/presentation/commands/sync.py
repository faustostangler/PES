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
