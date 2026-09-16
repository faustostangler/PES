"""Composition Root for the Cresmo Knowledge Synthesis Engine.

Centralizes pure Dependency Injection assembly, binding validated configuration
from CresmoSettings to concrete infrastructure adapters and instantiating CresmoPipeline.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.discover_batch_sources import DiscoverBatchSourcesUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.header_generator import RandomHeaderGenerator
from cresmo.infrastructure.adapters.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.sqlite_ledger_adapter import SqliteLedgerAdapter
from cresmo.infrastructure.config import CresmoSettings


def _resolve_cookie_file(settings: CresmoSettings) -> Path | None:
    """Resolve active cookie file or attempt browser auto-extraction if enabled."""
    cookie_file = getattr(settings, "cookies_file", None)
    if (cookie_file is None or not cookie_file.exists()) and getattr(
        settings, "auto_extract_cookies", True
    ):
        from cresmo.infrastructure.adapters.cookie_extractor import ensure_cookies_file

        data_dir = getattr(settings, "data_dir", None) or Path("data")
        target_cookie_path = data_dir / "cookies.txt"
        cookie_file = ensure_cookies_file(
            output_file=target_cookie_path,
            browser=getattr(settings, "browser_cookies", "firefox"),
            verbose=False,
        )
    return cookie_file


def build_media_ingestion_adapter(
    settings: CresmoSettings | None = None,
) -> NativeMediaIngestionAdapter:
    """Instantiate and wire NativeMediaIngestionAdapter with resolved settings and active cookies.

    Acts as the Single Source of Truth (SSOT) factory for media ingestion, centralizing
    header rotation, active session cookie resolution, and concurrency limits.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    cookie_file = _resolve_cookie_file(resolved_settings)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)

    return NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
        cookie_file=cookie_file,
    )


def build_pipeline(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
) -> CresmoPipeline:
    """Instantiate and wire production infrastructure adapters into CresmoPipeline.

    Args:
        settings: Validated application settings. If None, loaded fail-fast from environment.
        batch_size_override: Optional operational override for note batch size.

    Returns:
        Configured and wired CresmoPipeline ready for execution.
    """
    resolved_settings = settings or CresmoSettings()

    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        try:
            os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
            os.environ["LANGFUSE_SECRET_KEY"] = (
                resolved_settings.langfuse_secret_key.get_secret_value()
            )
            os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None
            os.environ.pop("LANGFUSE_PUBLIC_KEY", None)
            os.environ.pop("LANGFUSE_SECRET_KEY", None)
            os.environ.pop("LANGFUSE_HOST", None)

    media_ingestion_port = build_media_ingestion_adapter(resolved_settings)
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def build_preflight_checker(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def build_sync_channel_use_case(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def build_unify_duplicates_use_case(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def build_discover_batch_sources_use_case(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    media_ingestion_port = build_media_ingestion_adapter(resolved_settings)
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )
