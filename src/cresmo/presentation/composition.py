"""Composition Root for the Cresmo Knowledge Synthesis Engine.

Centralizes pure Dependency Injection assembly, binding validated configuration
from CresmoSettings to concrete infrastructure adapters and instantiating CresmoPipeline.
"""

from __future__ import annotations

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.services.preflight import PreflightHealthChecker
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    media_ingestion_port = NativeMediaIngestionAdapter(header_generator=header_generator)
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
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
