"""Use case factory functions for assembling domain use cases with injected policies and adapters.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-002: Presentation CLI & Humble Object
- ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from collections.abc import Callable

from cresmo.application.ports import MediaIngestionPort, MetricsPort, VaultRepositoryPort
from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discovery.discover_batch_sources import (
    DiscoverBatchSourcesUseCase,
)
from cresmo.application.use_cases.discovery.models import DiscoveryPaths
from cresmo.application.use_cases.indexing.index_raw_transcripts import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.bootstrap.factories.adapter_factory import (
    build_gemini_credential_pool,
    build_indexing_adapter,
    build_media_ingestion_adapter,
    build_prompt_provider,
    build_taxonomy_adapter,
    build_vault_adapter,
)
from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
from cresmo.bootstrap.factories.telemetry_factory import (
    build_anonymizer_adapter,
    build_telemetry_adapter,
    resolve_langfuse_client,
)
from cresmo.infrastructure.config import CresmoSettings, resolve_shared_settings


def build_unify_duplicates_use_case(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired."""
    resolved = resolve_shared_settings(settings)
    vault_port = build_vault_adapter(resolved.storage)
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def build_discover_batch_sources_use_case(
    settings: CresmoSettings | None = None,
    media_ingestion_port: MediaIngestionPort | None = None,
    progress_callback: Callable[[str], object] | None = None,
    metrics_port: MetricsPort | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with domain DiscoveryPolicy and DiscoveryPaths."""
    resolved = resolve_shared_settings(settings)
    media_ingestion_port = media_ingestion_port or build_media_ingestion_adapter(
        resolved, metrics_port=metrics_port
    )
    taxonomy_port = build_taxonomy_adapter(resolved.storage)
    storage = resolved.storage
    discovery_paths = DiscoveryPaths(
        raw_dir=storage.raw_dir,
        playlist_path=storage.playlist_path,
        playlist_priority_path=storage.playlist_priority_path,
        priority_texts_dir=storage.priority_texts_dir,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        discovery_policy=resolved.to_discovery_policy(),
        discovery_paths=discovery_paths,
        progress_callback=progress_callback,
        taxonomy_port=taxonomy_port,
        metrics_port=metrics_port,
    )


def build_concat_master_use_case(
    settings: CresmoSettings | None = None,
    vault_port: VaultRepositoryPort | None = None,
) -> ConcatMasterUseCase:
    """Instantiate ConcatMasterUseCase with domain CompendiumRolloverPolicy."""
    resolved = resolve_shared_settings(settings)
    vault_port = vault_port or build_vault_adapter(resolved.storage)
    taxonomy_port = build_taxonomy_adapter(resolved.storage)
    return ConcatMasterUseCase(
        vault_port=vault_port,
        rollover_policy=resolved.to_compendium_rollover_policy(),
        taxonomy_port=taxonomy_port,
    )


def build_index_raw_use_case(
    settings: CresmoSettings | None = None,
    web_index: bool = False,
    model_override: str | None = None,
) -> IndexRawTranscriptsUseCase:
    """Instantiate IndexRawTranscriptsUseCase selecting between local Ollama and Gemini Web API."""
    resolved = resolve_shared_settings(settings)
    vault_port = build_vault_adapter(resolved.storage)
    anonymizer = build_anonymizer_adapter(resolved.observability)
    langfuse_client = resolve_langfuse_client(resolved.observability, anonymizer=anonymizer)
    telemetry_port = build_telemetry_adapter(
        resolved.observability, langfuse_client=langfuse_client
    )
    prompt_provider = build_prompt_provider(resolved, langfuse_client=langfuse_client)
    uses_gemini = (
        web_index
        or resolved.llm.indexing_provider == "gemini"
        or resolved.judge.provider == "gemini"
    )
    gemini_pool = build_gemini_credential_pool(resolved.llm.gemini) if uses_gemini else None
    llm_indexing_port = build_indexing_adapter(
        resolved.llm,
        web_index=web_index,
        model_override=model_override,
        telemetry_port=telemetry_port,
        credential_pool=gemini_pool,
    )
    llm_judge_port = build_llm_judge_adapter(
        resolved,
        telemetry_port=telemetry_port,
        prompt_provider=prompt_provider,
        credential_pool=gemini_pool,
    )

    taxonomy_port = build_taxonomy_adapter(resolved.storage)

    return IndexRawTranscriptsUseCase(
        vault_port=vault_port,
        llm_indexing_port=llm_indexing_port,
        prompt_provider=prompt_provider,
        max_chars=resolved.pipeline.raw_index_max_chars,
        temperature=resolved.llm.ollama.indexing_temperature,
        language=resolved.pipeline.language,
        max_rewrites=resolved.pipeline.stages.raw_index_max_attempts,
        llm_judge_port=llm_judge_port,
        taxonomy_port=taxonomy_port,
    )
