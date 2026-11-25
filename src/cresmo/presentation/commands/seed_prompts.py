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

import subprocess
import sys
from typing import Annotated, Any

import typer

from cresmo import __version__
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)


def build_local_prompt_provider(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import build_local_prompt_provider as _factory

    return _factory(*args, **kwargs)


def load_local_prompt_catalog(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition helper to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import load_local_prompt_catalog as _helper

    return _helper(*args, **kwargs)


def resolve_langfuse_client(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition helper to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import resolve_langfuse_client as _helper

    return _helper(*args, **kwargs)


def resolve_shared_settings(*args: Any, **kwargs: Any) -> Any:
    """Lazily import composition factory to keep --help and module load instant (ADR-055)."""
    from cresmo.bootstrap.composition import resolve_shared_settings as _factory

    return _factory(*args, **kwargs)


def _get_prompt_mappings() -> dict[str, str]:
    """Lazily materialize PROMPT_MAPPINGS on first access without eager composition import."""
    cached = globals().get("PROMPT_MAPPINGS")
    if isinstance(cached, dict):
        return cached
    mappings: dict[str, str] = {
        spec.langfuse_name: spec.key.value for spec in load_local_prompt_catalog().values()
    }
    globals()["PROMPT_MAPPINGS"] = mappings
    return mappings


def __getattr__(name: str) -> Any:
    """Expose PROMPT_MAPPINGS lazily via PEP 562 for test patching and callers."""
    if name == "PROMPT_MAPPINGS":
        return _get_prompt_mappings()
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


def _resolve_git_sha(configured_sha: str | None = None) -> str:
    """Resolve current Git commit short SHA from injected config or git CLI."""
    if configured_sha and configured_sha.strip():
        return configured_sha.strip()[:8]
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short=8", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except Exception:  # noqa: BLE001
        pass
    return "unknown"


def seed_prompts(
    label: Annotated[
        str,
        typer.Option("--label", help="Target Langfuse prompt label (default: production)"),
    ] = "production",
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Render prompts without transmitting to Langfuse server"),
    ] = False,
) -> None:
    """Synchronize local prompt definitions to the active Langfuse server."""
    code = handle_seed_prompts(label=label, dry_run=dry_run)
    if code != EXIT_SUCCESS:
        raise typer.Exit(code=code)


def handle_seed_prompts(
    label: str = "production",
    dry_run: bool = False,
) -> int:
    """Synchronize local prompt definitions to the active Langfuse server.

    Args:
        label: Target prompt label string.
        dry_run: Whether to simulate prompt rendering.

    Returns:
        Process exit code conforming to exit_codes.py.
    """
    label = label or "production"

    settings = resolve_shared_settings()
    provider = build_local_prompt_provider()
    prompt_mappings = _get_prompt_mappings()

    if dry_run:
        sys.stdout.write(
            f"[dry-run] Rendering {len(prompt_mappings)} Chat-Native prompt templates:\n"
        )
        for name, key in prompt_mappings.items():
            system_prompt, user_prompt = provider.get_chat_prompt_template(key)
            preview_sys = system_prompt[:50].replace("\n", " ")
            preview_usr = user_prompt[:50].replace("\n", " ")
            sys.stdout.write(
                f"- {name} (key={key}): [system] {preview_sys}... | [user] {preview_usr}...\n"
            )
        sys.stdout.write(f"[dry-run] Completed preview of {len(prompt_mappings)} chat prompts.\n")
        return EXIT_SUCCESS

    client = resolve_langfuse_client(settings.observability)
    if client is None:
        sys.stderr.write(
            "Langfuse client could not be initialized or server is unreachable.\n"
            "Ensure Langfuse is running (`make up`) and environment variables are set.\n"
        )
        return EXIT_CONFIG_OR_USAGE_ERROR

    success_count = 0
    failure_count = 0
    git_sha = _resolve_git_sha(settings.observability.runtime.git_sha)
    tags = ["cresmo", f"v{__version__}", f"git:{git_sha}"]
    prompt_config = {"git_sha": git_sha, "version": __version__}

    for name, key in prompt_mappings.items():
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
                tags=tags,
                config=prompt_config,
                type="chat",
            )
            sys.stdout.write(
                f"✔ Registered '{name}' in Langfuse [type=chat, label={label}, version={__version__}, git={git_sha}]\n"
            )
            success_count += 1
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"✘ Failed to register '{name}': {exc}\n")
            failure_count += 1

    sys.stdout.write(
        f"\nCompleted: {success_count}/{len(prompt_mappings)} prompts synchronized to Langfuse.\n"
    )
    if failure_count > 0 and success_count == 0:
        return EXIT_INTERNAL_ERROR
    return EXIT_SUCCESS
