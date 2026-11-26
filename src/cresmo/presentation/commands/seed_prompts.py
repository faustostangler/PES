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
from typing import Annotated, Any, Final

import typer

from cresmo import __version__
from cresmo.presentation.exit_codes import (
    EXIT_CONFIG_OR_USAGE_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)

_PROMPT_MAPPINGS_ATTR: Final[str] = "PROMPT_MAPPINGS"
_GIT_SHA_SHORT_LENGTH: Final[int] = 8
_GIT_REV_PARSE_CMD: Final[tuple[str, ...]] = ("git", "rev-parse", "--short=8", "HEAD")
_UNKNOWN_GIT_SHA: Final[str] = "unknown"
DEFAULT_LANGFUSE_PROMPT_LABEL: Final[str] = "production"
_PROMPT_PREVIEW_MAX_CHARS: Final[int] = 50
_CRESMO_TAG: Final[str] = "cresmo"
_VERSION_TAG_PREFIX: Final[str] = "v"
_GIT_TAG_PREFIX: Final[str] = "git:"
_KEY_GIT_SHA: Final[str] = "git_sha"
_KEY_VERSION: Final[str] = "version"
_KEY_ROLE: Final[str] = "role"
_KEY_CONTENT: Final[str] = "content"
_ROLE_SYSTEM: Final[str] = "system"
_ROLE_USER: Final[str] = "user"
_PROMPT_TYPE_CHAT: Final[str] = "chat"


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
    cached = globals().get(_PROMPT_MAPPINGS_ATTR)
    if isinstance(cached, dict):
        return cached
    mappings: dict[str, str] = {
        spec.langfuse_name: spec.key.value for spec in load_local_prompt_catalog().values()
    }
    globals()[_PROMPT_MAPPINGS_ATTR] = mappings
    return mappings


def __getattr__(name: str) -> Any:
    """Expose PROMPT_MAPPINGS lazily via PEP 562 for test patching and callers."""
    if name == _PROMPT_MAPPINGS_ATTR:
        return _get_prompt_mappings()
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


def _resolve_git_sha(configured_sha: str | None = None) -> str:
    """Resolve current Git commit short SHA from injected config or git CLI."""
    if configured_sha and configured_sha.strip():
        return configured_sha.strip()[:_GIT_SHA_SHORT_LENGTH]
    try:
        out = subprocess.check_output(
            list(_GIT_REV_PARSE_CMD),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except Exception:  # noqa: BLE001
        pass
    return _UNKNOWN_GIT_SHA


def seed_prompts(
    label: Annotated[
        str,
        typer.Option("--label", help="Target Langfuse prompt label (default: production)"),
    ] = DEFAULT_LANGFUSE_PROMPT_LABEL,
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
    label: str = DEFAULT_LANGFUSE_PROMPT_LABEL,
    dry_run: bool = False,
) -> int:
    """Synchronize local prompt definitions to the active Langfuse server.

    Args:
        label: Target prompt label string.
        dry_run: Whether to simulate prompt rendering.

    Returns:
        Process exit code conforming to exit_codes.py.
    """
    label = label or DEFAULT_LANGFUSE_PROMPT_LABEL

    settings = resolve_shared_settings()
    provider = build_local_prompt_provider()
    prompt_mappings = _get_prompt_mappings()

    if dry_run:
        sys.stdout.write(
            f"[dry-run] Rendering {len(prompt_mappings)} Chat-Native prompt templates:\n"
        )
        for name, key in prompt_mappings.items():
            system_prompt, user_prompt = provider.get_chat_prompt_template(key)
            preview_sys = system_prompt[:_PROMPT_PREVIEW_MAX_CHARS].replace("\n", " ")
            preview_usr = user_prompt[:_PROMPT_PREVIEW_MAX_CHARS].replace("\n", " ")
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
    tags = [_CRESMO_TAG, f"{_VERSION_TAG_PREFIX}{__version__}", f"{_GIT_TAG_PREFIX}{git_sha}"]
    prompt_config = {_KEY_GIT_SHA: git_sha, _KEY_VERSION: __version__}

    for name, key in prompt_mappings.items():
        system_prompt, user_prompt = provider.get_chat_prompt_template(key)
        chat_prompt = [
            {_KEY_ROLE: _ROLE_SYSTEM, _KEY_CONTENT: system_prompt},
            {_KEY_ROLE: _ROLE_USER, _KEY_CONTENT: user_prompt},
        ]
        try:
            client.create_prompt(
                name=name,
                prompt=chat_prompt,
                labels=[label],
                tags=tags,
                config=prompt_config,
                type=_PROMPT_TYPE_CHAT,
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
