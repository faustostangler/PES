"""Composition Root for the Cresmo Knowledge Synthesis Engine.

Centralizes pure Dependency Injection assembly, translating validated hierarchical
CresmoSettings into domain policies for Use Cases and narrow sub-configs for adapters.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-002: Presentation CLI & Humble Object
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
    - SPEC-002: CLI Controller & Exit Codes
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

from cresmo.application.pipeline.coordinator import CresmoPipeline
from cresmo.application.pipeline.models import PipelineDependencies
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.ports import MediaIngestionPort, VaultRepositoryPort
from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discovery.discover_batch_sources import (
    DiscoverBatchSourcesUseCase,
)
from cresmo.application.use_cases.run_synthesis import RunSynthesisUseCase
from cresmo.application.use_cases.sync_batch import SyncBatchUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.bootstrap.factories.adapter_factory import (
    build_embedding_adapter,
    build_gemini_credential_pool,
    build_gemini_synthesis_adapter,
    build_indexing_adapter,
    build_local_prompt_provider,
    build_media_ingestion_adapter,
    build_preflight_checker,
    build_process_runtime_adapter,
    build_prompt_provider,
    build_taxonomy_adapter,
    build_vault_adapter,
    load_local_prompt_catalog,
)
from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
from cresmo.bootstrap.factories.telemetry_factory import (
    build_anonymizer_adapter,
    build_metrics_adapter,
    build_telemetry_adapter,
    resolve_langfuse_client,
)
from cresmo.bootstrap.factories.use_case_factory import (
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_index_raw_use_case,
    build_unify_duplicates_use_case,
)
from cresmo.infrastructure.adapters.scrapers.cookie_extractor import (
    export_cookies_from_browser,
    has_valid_auth_cookies,
)
from cresmo.infrastructure.config import CresmoSettings, resolve_shared_settings
from cresmo.infrastructure.environment import ensure_runtime_directories
from cresmo.infrastructure.logging_config import configure_logging
from cresmo.infrastructure.persistence.sqlite_ledger_adapter import SqliteLedgerAdapter

_SETTINGS_KEY_INGESTION: Final[str] = "ingestion"
_SETTINGS_KEY_DAYS_LOOKBACK: Final[str] = "days_lookback"


def load_fresh_settings() -> CresmoSettings:
    """Instantiate fresh validated CresmoSettings directly from environment and .env."""
    return CresmoSettings()


def build_pipeline(
    settings: CresmoSettings | None = None,
    web_index: bool = False,
) -> CresmoPipeline:
    """Instantiate and wire production infrastructure adapters into CresmoPipeline."""
    resolved = resolve_shared_settings(settings)
    resolved.ensure_directories()

    # 0. Structured Logging Configuration (ADR-025)
    configure_logging(
        level=resolved.observability.logging.level,
        fmt=resolved.observability.logging.format,
    )

    # 1. Observability & Security
    anonymizer = build_anonymizer_adapter(resolved.observability)
    langfuse_client = resolve_langfuse_client(resolved.observability, anonymizer=anonymizer)
    telemetry_port = build_telemetry_adapter(
        resolved.observability, langfuse_client=langfuse_client
    )

    # 2. Metrics, Ingestion, Persistence & Idempotency
    metrics_port = build_metrics_adapter(resolved.observability)
    media_ingestion_port = build_media_ingestion_adapter(resolved, metrics_port=metrics_port)
    vault_port = build_vault_adapter(resolved.storage)
    ledger_port = SqliteLedgerAdapter(db_path=resolved.storage.sqlite_ledger_path)

    # 3. Prompt Governance, Cognitive & Judge LLM Engines
    prompt_provider = build_prompt_provider(resolved, langfuse_client=langfuse_client)
    gemini_pool = build_gemini_credential_pool(resolved.llm.gemini)
    synthesis_adapter = build_gemini_synthesis_adapter(
        resolved.llm.gemini,
        telemetry_port=telemetry_port,
        credential_pool=gemini_pool,
        metrics_port=metrics_port,
    )
    llm_indexing_port = build_indexing_adapter(
        resolved.llm,
        synthesis_adapter=synthesis_adapter,
        web_index=web_index,
        telemetry_port=telemetry_port,
        credential_pool=gemini_pool,
        metrics_port=metrics_port,
    )
    llm_judge = build_llm_judge_adapter(
        resolved,
        telemetry_port=telemetry_port,
        prompt_provider=prompt_provider,
        credential_pool=gemini_pool,
    )
    from cresmo.infrastructure.adapters.llm.ollama_critique_adapter import (
        OllamaCritiqueAdapter,
    )

    critique_synthesizer = OllamaCritiqueAdapter(
        llm_transformation_port=llm_indexing_port,
        prompt_provider=prompt_provider,
    )

    # 5. Pipeline Stage Runner & Closed-Loop Verifier (ADR-030, ADR-031, ADR-074)
    stage_policy = resolved.to_stage_execution_policy()
    embedding_port = build_embedding_adapter(resolved, credential_pool=gemini_pool)
    stage_factory = StageFactory(policy=stage_policy, embedding_port=embedding_port)
    stage_runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=telemetry_port,
            metrics_port=metrics_port,
            llm_judge=llm_judge,
            judge_blocking=resolved.judge.blocking,
            judge_max_attempts=resolved.judge.max_attempts,
            prompt_provider=prompt_provider,
            llm_transformation_port=synthesis_adapter,
            stage_factory=stage_factory,
            critique_synthesizer=critique_synthesizer,
            ledger_port=ledger_port,
        )
    )

    # 6. Pipeline Assembly
    taxonomy_port = build_taxonomy_adapter(resolved.storage)

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        vault_port=vault_port,
        stage_runner=stage_runner,
        ledger_port=ledger_port,
        taxonomy_port=taxonomy_port,
    )


def build_sync_channel_use_case(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired."""
    resolved = resolve_shared_settings(settings)
    pipeline = build_pipeline(resolved)
    preflight_checker = build_preflight_checker(resolved, check_ffmpeg=check_ffmpeg)

    if pipeline.ledger_port is None:
        raise RuntimeError("Ledger port must be wired for channel sync.")

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def build_run_synthesis_use_case(
    settings: CresmoSettings | None = None,
    *,
    lookback_override: int | None = None,
    web_index: bool = False,
    check_ffmpeg: bool = True,
) -> RunSynthesisUseCase:
    """Construct RunSynthesisUseCase with fail-fast preflight and lazy pipeline factories."""
    resolved = load_fresh_settings() if settings is None else settings
    if lookback_override is not None:
        resolved = resolved.model_copy(
            update={
                _SETTINGS_KEY_INGESTION: resolved.ingestion.model_copy(
                    update={_SETTINGS_KEY_DAYS_LOOKBACK: lookback_override}
                )
            }
        )

    preflight_checker = build_preflight_checker(settings=resolved, check_ffmpeg=check_ffmpeg)
    metrics_port = build_metrics_adapter(resolved.observability)

    def _discover_factory(
        media_port: MediaIngestionPort,
        progress_callback: Callable[[str], object] | None,
    ) -> DiscoverBatchSourcesUseCase:
        return build_discover_batch_sources_use_case(
            settings=resolved,
            media_ingestion_port=media_port,
            progress_callback=progress_callback,
            metrics_port=metrics_port,
        )

    def _concat_factory(vault_port: VaultRepositoryPort) -> ConcatMasterUseCase:
        return build_concat_master_use_case(settings=resolved, vault_port=vault_port)

    return RunSynthesisUseCase(
        discovery_policy=resolved.to_discovery_policy(),
        preflight_checker=preflight_checker,
        pipeline_factory=lambda: build_pipeline(
            settings=resolved,
            web_index=web_index,
        ),
        discover_sources_factory=_discover_factory,
        concat_master_factory=_concat_factory,
        runtime_port=build_process_runtime_adapter(),
        default_manifest_path=resolved.storage.playlist_path,
    )


def build_sync_batch_use_case(
    settings: CresmoSettings | None = None,
    *,
    check_ffmpeg: bool = True,
) -> SyncBatchUseCase:
    """Construct SyncBatchUseCase with ensured runtime directories, channel sync, and taxonomy."""
    resolved = resolve_shared_settings(settings)
    ensure_runtime_directories(resolved.storage)
    sync_channel_use_case = build_sync_channel_use_case(
        settings=resolved,
        check_ffmpeg=check_ffmpeg,
    )
    taxonomy_port = build_taxonomy_adapter(resolved.storage)
    return SyncBatchUseCase(
        sync_channel_use_case=sync_channel_use_case,
        default_manifest_path=resolved.storage.playlist_path,
        taxonomy_port=taxonomy_port,
    )


__all__ = [
    "build_concat_master_use_case",
    "build_index_raw_use_case",
    "build_local_prompt_provider",
    "build_pipeline",
    "build_preflight_checker",
    "build_prompt_provider",
    "build_run_synthesis_use_case",
    "build_sync_batch_use_case",
    "build_sync_channel_use_case",
    "build_unify_duplicates_use_case",
    "export_cookies_from_browser",
    "has_valid_auth_cookies",
    "load_fresh_settings",
    "load_local_prompt_catalog",
    "resolve_langfuse_client",
    "resolve_shared_settings",
]
