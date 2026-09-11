"""Humble Object Command-Line Interface (CLI) Controller for Cresmo.

Translates CLI arguments and operating system process signals into application
pipeline invocations, mapping domain exceptions to standardized process exit codes.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from pydantic import ValidationError

from cresmo.domain.exceptions import (
    CresmoDomainError,
    DomainValidationError,
    IngestionNetworkError,
    RateLimitExceededError,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import build_pipeline

# Standardized Process Exit Codes (per ADR-002 and SPEC-002)
EXIT_SUCCESS: int = 0
EXIT_INTERNAL_ERROR: int = 1
EXIT_CONFIG_OR_USAGE_ERROR: int = 2
EXIT_DOMAIN_VALIDATION_ERROR: int = 3
EXIT_RATE_LIMIT_EXCEEDED: int = 4
EXIT_INGESTION_ERROR: int = 5


def _create_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="cresmo",
        description="Cresmo Knowledge Synthesis CLI (Hexagonal Modular Monolith)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Subcommand: run
    run_parser = subparsers.add_parser(
        "run",
        help="Run end-to-end knowledge synthesis for a video",
    )
    run_parser.add_argument(
        "--url",
        required=True,
        help="Target YouTube or media video URL",
    )
    run_parser.add_argument(
        "--passes",
        type=int,
        default=1,
        help="Refinement passes for gap filler (default: 1)",
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

    # Subcommand: check-config
    subparsers.add_parser(
        "check-config",
        help="Validate environment settings and vault access without calling LLMs",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint for Cresmo operations.

    Args:
        argv: Command-line arguments. If None, defaults to sys.argv[1:].

    Returns:
        Deterministic integer exit code matching the process exit taxonomy.
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = _create_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_SUCCESS
        return EXIT_CONFIG_OR_USAGE_ERROR

    if not args.subcommand:
        parser.print_usage(file=sys.stderr)
        return EXIT_CONFIG_OR_USAGE_ERROR

    if args.subcommand == "check-config":
        try:
            settings = CresmoSettings()
            sys.stdout.write("Configuration verified successfully:\n")
            sys.stdout.write(f"- Vault Root: {settings.vault_dir}\n")
            sys.stdout.write(f"- Gemini Model: {settings.gemini_model}\n")
            sys.stdout.write(f"- Batch Size: {settings.batch_size}\n")
            return EXIT_SUCCESS
        except ValidationError as exc:
            sys.stderr.write(f"Configuration validation error:\n{exc}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Unexpected configuration error: {exc}\n")
            return EXIT_INTERNAL_ERROR

    if args.subcommand == "run":
        try:
            if args.batch_size is not None:
                pipeline = build_pipeline(batch_size_override=args.batch_size)
            else:
                pipeline = build_pipeline()

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
            if result.success:
                sys.stdout.write(
                    f"Synthesis completed successfully for [{result.content_id.value}]: "
                    f"{len(result.synthesized_notes)} atomic notes synthesized, "
                    f"{len(result.reconciled_mocs)} MOCs reconciled.\n"
                )
                return EXIT_SUCCESS
            else:
                sys.stderr.write(f"Pipeline error: {result.error_message}\n")
                return EXIT_INTERNAL_ERROR

        except RateLimitExceededError as exc:
            sys.stderr.write(f"Rate limit exceeded: {exc}\n")
            return EXIT_RATE_LIMIT_EXCEEDED
        except IngestionNetworkError as exc:
            sys.stderr.write(f"Ingestion network error: {exc}\n")
            return EXIT_INGESTION_ERROR
        except (DomainValidationError, CresmoDomainError) as exc:
            sys.stderr.write(f"Domain validation error: {exc}\n")
            return EXIT_DOMAIN_VALIDATION_ERROR
        except ValidationError as exc:
            sys.stderr.write(f"Configuration error: {exc}\n")
            return EXIT_CONFIG_OR_USAGE_ERROR
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"Unexpected internal error: {exc}\n")
            return EXIT_INTERNAL_ERROR

    return EXIT_CONFIG_OR_USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())
