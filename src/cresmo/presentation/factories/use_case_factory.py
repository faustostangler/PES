"""Use case factory functions for assembling domain use cases with injected adapters.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-002: Presentation CLI & Humble Object
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from cresmo.application.ports import MediaIngestionPort
from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discover_batch_sources import DiscoverBatchSourcesUseCase
from cresmo.application.use_cases.index_raw_transcripts import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.adapter_factory import (
    build_indexing_adapter,
    build_media_ingestion_adapter,
    build_preflight_checker,
    build_prompt_provider,
    build_vault_adapter,
)
from cresmo.presentation.factories.judge_factory import build_quality_judge_adapter
from cresmo.presentation.factories.settings_factory import resolve_shared_settings
from cresmo.presentation.factories.telemetry_factory import (
    build_anonymizer_adapter,
    resolve_langfuse_client,
)

if TYPE_CHECKING:
    from cresmo.application.pipeline import CresmoPipeline


def build_sync_channel_use_case(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
    pipeline: CresmoPipeline | None = None,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired."""
    from cresmo.presentation.composition import build_pipeline

    resolved_settings = resolve_shared_settings(settings)
    active_pipeline = pipeline or build_pipeline(
        resolved_settings, batch_size_override=batch_size_override
    )
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    if active_pipeline.ledger_port is None:
        raise RuntimeError("Ledger port must be wired for channel sync.")

    return SyncChannelUseCase(
        media_ingestion_port=active_pipeline.media_ingestion_port,
        ledger_port=active_pipeline.ledger_port,
        pipeline=active_pipeline,
        preflight_checker=preflight_checker,
    )


def build_unify_duplicates_use_case(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired."""
    resolved_settings = resolve_shared_settings(settings)
    vault_port = build_vault_adapter(resolved_settings)
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def build_discover_batch_sources_use_case(
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with injected or default NativeMediaIngestionAdapter."""
    resolved_settings = resolve_shared_settings(settings)
    resolved_media_port = media_ingestion_port or build_media_ingestion_adapter(resolved_settings)
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=resolved_media_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def build_concat_master_use_case(
    settings: CresmoSettings | None = None,
    vault_port: ObsidianVaultAdapter | None = None,
) -> ConcatMasterUseCase:
    """Instantiate ConcatMasterUseCase with configured dependencies."""
    resolved_settings = resolve_shared_settings(settings)
    resolved_vault = vault_port or build_vault_adapter(resolved_settings)
    return ConcatMasterUseCase(
        vault_port=resolved_vault,
        settings=resolved_settings,
    )


def build_index_raw_use_case(
    settings: CresmoSettings | None = None,
    web_index: bool = False,
    model_override: str | None = None,
) -> IndexRawTranscriptsUseCase:
    """Instantiate IndexRawTranscriptsUseCase selecting between local Ollama and Gemini Web API."""
    resolved_settings = resolve_shared_settings(settings)
    vault_port = build_vault_adapter(resolved_settings)
    anonymizer = build_anonymizer_adapter(resolved_settings)
    langfuse_client = resolve_langfuse_client(resolved_settings, anonymizer=anonymizer)
    prompt_provider = build_prompt_provider(resolved_settings, langfuse_client=langfuse_client)
    llm = build_indexing_adapter(
        resolved_settings,
        web_index=web_index,
        model_override=model_override,
        langfuse_client=langfuse_client,
    )
    quality_judge_port = build_quality_judge_adapter(
        resolved_settings, langfuse_client=langfuse_client
    )

    return IndexRawTranscriptsUseCase(
        vault_port=vault_port,
        llm_indexing_port=llm,
        prompt_provider=prompt_provider,
        max_chars=resolved_settings.raw_index_max_chars,
        temperature=resolved_settings.llm_indexing_temperature,
        language=resolved_settings.language,
        max_rewrites=resolved_settings.raw_index_max_attempts,
        quality_judge_port=quality_judge_port,
    )
