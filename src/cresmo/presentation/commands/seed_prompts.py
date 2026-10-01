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
import re
import sys
from typing import Any

from cresmo.infrastructure.adapters.prompts import PROMPT_REGISTRY, JsonPromptProvider
from cresmo.presentation.composition import (
    resolve_langfuse_client,
    resolve_shared_settings,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

logger = logging.getLogger(__name__)

PROMPT_MAPPINGS: dict[str, str] = {
    meta.langfuse_name: meta.key.value for meta in PROMPT_REGISTRY.values()
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


def _to_mustache(text: str) -> str:
    """Convert Python single-brace template variables {var} to Langfuse Mustache {{var}}."""
    return re.sub(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})", r"{{\1}}", text)


def handle_seed_prompts(args: argparse.Namespace) -> int:
    """Synchronize local prompt definitions to the active Langfuse server.

    Args:
        args: Parsed CLI argument namespace.

    Returns:
        Process exit code conforming to exit_codes.py.
    """
    label = getattr(args, "label", "production") or "production"
    dry_run = getattr(args, "dry_run", False)

    settings = resolve_shared_settings()
    provider = JsonPromptProvider()

    if dry_run:
        sys.stdout.write(
            f"[dry-run] Rendering {len(PROMPT_MAPPINGS)} Chat-Native prompt templates:\n"
        )
        for lf_name, json_key in PROMPT_MAPPINGS.items():
            sys_inst, user_tpl = provider.get_chat_prompt_template(json_key)
            sys_mustache = _to_mustache(sys_inst)
            user_mustache = _to_mustache(user_tpl)
            preview_sys = sys_mustache[:50].replace("\n", " ")
            preview_usr = user_mustache[:50].replace("\n", " ")
            sys.stdout.write(
                f"- {lf_name} (key={json_key}): [system] {preview_sys}... | [user] {preview_usr}...\n"
            )
        sys.stdout.write(f"[dry-run] Completed preview of {len(PROMPT_MAPPINGS)} chat prompts.\n")
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
        sys_inst, user_tpl = provider.get_chat_prompt_template(json_key)
        chat_prompt = [
            {"role": "system", "content": _to_mustache(sys_inst)},
            {"role": "user", "content": _to_mustache(user_tpl)},
        ]
        try:
            client.create_prompt(
                name=lf_name,
                prompt=chat_prompt,
                labels=[label],
                tags=["cresmo", "v2"],
                type="chat",
            )
            sys.stdout.write(f"✔ Registered '{lf_name}' in Langfuse [type=chat, label={label}]\n")
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
