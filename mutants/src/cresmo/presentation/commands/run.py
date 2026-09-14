"""Command handler for cresmo run."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from cresmo.application.pipeline import CresmoPipeline
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
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_orig(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_1(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = None
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_2(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=None,
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_3(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        progress_callback=None,
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_4(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        progress_callback=lambda msg: sys.stdout.write(msg),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_5(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_6(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        progress_callback=lambda msg: None,
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_7(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
        progress_callback=lambda msg: sys.stdout.write(None),
    )
    return discovery_use_case.execute(query=query)


def x_load_batch_sources__mutmut_8(
    query: BatchDiscoveryQuery,
    settings: CresmoSettings,
) -> list[BatchSource]:
    """Execute batch source discovery via DiscoverBatchSourcesUseCase."""
    discovery_use_case = build_discover_batch_sources_use_case(
        settings=settings,
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
            explicit_manifest=args.manifest,
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
            scan_raw=not args.no_scan_raw,
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
            lookback_days=settings.days_lookback,
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
            scan_raw=args.no_scan_raw,
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
            scan_raw=not args.no_scan_raw,
            lookback_days=settings.days_lookback,
            channel_max_videos=args.channel_max_videos,
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
