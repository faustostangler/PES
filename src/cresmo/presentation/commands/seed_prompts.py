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

import sys
from typing import Annotated, Any

import typer

from cresmo.infrastructure.adapters.prompts import (
    JsonPromptProvider,
    load_prompt_catalog,
)
from cresmo.presentation.composition import (
    resolve_langfuse_client,
    resolve_shared_settings,
)
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

PROMPT_MAPPINGS: dict[str, str] = {
    spec.langfuse_name: spec.key.value for spec in load_prompt_catalog().values()
}


def seed_prompts(
    label: Annotated[
        str,
        typer.Option("--label", help="Target Langfuse prompt label (default: production)"),
    ] = "production",
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Render prompts without transmitting to Langfuse server"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
) -> None:
    """Synchronize local prompt definitions to the active Langfuse server."""
    _ = verbose
    code = handle_seed_prompts(None, label=label, dry_run=dry_run)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_seed_prompts(
    args: Any = None,
    label: str = "production",
    dry_run: bool = False,
) -> int:
    """Synchronize local prompt definitions to the active Langfuse server.

    Args:
        args: Parsed CLI argument namespace or None.
        label: Target prompt label string.
        dry_run: Whether to simulate prompt rendering.

    Returns:
        Process exit code conforming to exit_codes.py.
    """
    label = (
        getattr(args, "label", label) or "production"
        if args is not None
        else (label or "production")
    )
    dry_run = getattr(args, "dry_run", dry_run) if args is not None else dry_run

    settings = resolve_shared_settings()
    provider = JsonPromptProvider()

    if dry_run:
        sys.stdout.write(
            f"[dry-run] Rendering {len(PROMPT_MAPPINGS)} Chat-Native prompt templates:\n"
        )
        for name, key in PROMPT_MAPPINGS.items():
            system_prompt, user_prompt = provider.get_chat_prompt_template(key)
            preview_sys = system_prompt[:50].replace("\n", " ")
            preview_usr = user_prompt[:50].replace("\n", " ")
            sys.stdout.write(
                f"- {name} (key={key}): [system] {preview_sys}... | [user] {preview_usr}...\n"
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
    for name, key in PROMPT_MAPPINGS.items():
        system_prompt, user_prompt = provider.get_chat_prompt_template(key)
        chat_prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        try:
            client.create_prompt(
                name=name,
                prompt=chat_prompt,
                labels=[label],
                tags=["cresmo", "v2"],
                type="chat",
            )
            sys.stdout.write(
                f"✔ Registered '{name}' in Langfuse [type=chat, label={label}]\n"
            )
            success_count += 1
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"✘ Failed to register '{name}': {exc}\n")
            failure_count += 1

    sys.stdout.write(
        f"\nCompleted: {success_count}/{len(PROMPT_MAPPINGS)} prompts synchronized to Langfuse.\n"
    )
    if failure_count > 0 and success_count == 0:
        return EXIT_INTERNAL_ERROR
    return EXIT_SUCCESS
