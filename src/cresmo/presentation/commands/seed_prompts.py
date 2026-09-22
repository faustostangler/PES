"""Command handler for cresmo seed-prompts.

Synchronizes canonical prompt templates from prompts.json into Langfuse prompt management.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-014: Active Preflight Probes & Fail-Fast Observability
    - ADR-017: Langfuse v4 Prompt Management & Anonymizer Governance
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.composition import resolve_langfuse_client
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

logger = logging.getLogger(__name__)

PROMPT_MAPPINGS: dict[str, str] = {
    "cresmo-gap-filler-pass1": "gap_filler_pass1",
    "cresmo-gap-filler-pass2": "gap_filler_pass_subsequent",
    "cresmo-long-expander": "long_expander",
    "cresmo-wide-expander": "wide_expander",
    "cresmo-atomic-inventory": "atomic_inventory",
    "cresmo-atomic-batch": "atomic_batch",
    "cresmo-mocs-reconciliation": "reconcile_mocs",
}


def register_subparser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Register 'seed-prompts' subcommand parser.

    Args:
        subparsers: Root CLI subparsers action object.
    """
    seed_parser = subparsers.add_parser(
        "seed-prompts",
        help="Synchronize canonical prompt templates into Langfuse prompt management",
    )
    seed_parser.add_argument(
        "--label",
        default="production",
        help="Target Langfuse prompt label (default: production)",
    )
    seed_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render prompts without transmitting to Langfuse server",
    )
    seed_parser.set_defaults(handler=handle_seed_prompts)


def handle_seed_prompts(args: argparse.Namespace) -> int:
    """Synchronize local prompt definitions to the active Langfuse server.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code conforming to exit_codes.py.
    """
    label = getattr(args, "label", "production") or "production"
    dry_run = getattr(args, "dry_run", False)

    settings = CresmoSettings()
    provider = JsonPromptProvider()

    if dry_run:
        sys.stdout.write(f"[dry-run] Rendering {len(PROMPT_MAPPINGS)} prompt templates:\n")
        for lf_name, json_key in PROMPT_MAPPINGS.items():
            full_text = provider.get_raw_prompt_template(json_key)
            preview = full_text[:80].replace("\n", " ")
            sys.stdout.write(f"- {lf_name} (key={json_key}): {preview}...\n")
        sys.stdout.write(f"[dry-run] Completed preview of {len(PROMPT_MAPPINGS)} prompts.\n")
        return EXIT_SUCCESS

    client = resolve_langfuse_client(settings)
    if client is None:
        sys.stderr.write(
            "Langfuse client could not be initialized or server is unreachable.\n"
            "Ensure Langfuse is running (`make up`) and environment variables are set.\n"
        )
        return EXIT_CONFIG_OR_USAGE_ERROR

    success_count = 0
    failure_count = 0
    for lf_name, json_key in PROMPT_MAPPINGS.items():
        full_text = provider.get_raw_prompt_template(json_key)
        try:
            client.create_prompt(
                name=lf_name,
                prompt=full_text,
                labels=[label],
                tags=["cresmo", "v1"],
                type="text",
            )
            sys.stdout.write(f"✔ Registered '{lf_name}' in Langfuse [label={label}]\n")
            success_count += 1
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"✘ Failed to register '{lf_name}': {exc}\n")
            failure_count += 1

    sys.stdout.write(
        f"\nCompleted: {success_count}/{len(PROMPT_MAPPINGS)} prompts synchronized to Langfuse.\n"
    )
    if failure_count > 0 and success_count == 0:
        return EXIT_INTERNAL_ERROR
    return EXIT_SUCCESS
