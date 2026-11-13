"""Composition Root for the Cresmo Knowledge Synthesis Engine.

Centralizes pure Dependency Injection assembly, binding validated configuration
from CresmoSettings to concrete infrastructure adapters and instantiating CresmoPipeline
and Application Use Cases per Clean/Hexagonal Architecture.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-002: Presentation CLI & Humble Object
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - SPEC-002: CLI Controller & Exit Codes
    - ADR-014: Fail-Fast Preflight Probing & Telemetry Circuit Breaking
    - ADR-017: Langfuse Otel Span Masking and Scrubbing
    - ADR-026: Clean Code Anti-Patterns & Code Smell Governance (Modularization)
"""

from __future__ import annotations

from cresmo.application.pipeline import (
    CresmoPipeline,  # slow import
    PipelineDependencies,
    PipelineStageRunner,
    StageFactory,
)
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.bootstrap.factories.adapter_factory import (
    build_gemini_synthesis_adapter,
    build_indexing_adapter,
    build_media_ingestion_adapter,
    build_preflight_checker,
    build_prompt_provider,
    build_taxonomy_adapter,
    build_vault_adapter,
)
from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
from cresmo.bootstrap.factories.settings_factory import (
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)
from cresmo.bootstrap.factories.telemetry_factory import (
    build_anonymizer_adapter,
    build_metrics_adapter,
    build_telemetry_adapter,
    probe_langfuse_ready,
    resolve_langfuse_client,
)
from cresmo.bootstrap.factories.use_case_factory import (
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_index_raw_use_case,
    build_unify_duplicates_use_case,
)
from cresmo.infrastructure.adapters.system.preflight_probe_adapter import probe_http_endpoint
from cresmo.infrastructure.config import CresmoSettings
from cresmo.infrastructure.logging_config import configure_logging
from cresmo.infrastructure.persistence.sqlite_ledger_adapter import SqliteLedgerAdapter


def build_pipeline(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    web_index: bool = False,
) -> CresmoPipeline:
    """Instantiate and wire production infrastructure adapters into CresmoPipeline.

    Args:
        settings: Validated application settings. If None, loaded fail-fast from environment.
        batch_size_override: Optional operational override for note batch size.
        web_index: If True, uses Gemini API for raw transcript indexing instead of local Ollama.

    Returns:
        Configured and wired CresmoPipeline ready for execution.
    """
    settings = resolve_shared_settings(settings)
    settings.ensure_directories()

    # 0. Structured Logging Configuration (ADR-025)
    configure_logging(
        level=settings.log_level,
        fmt=settings.log_format,
    )

    # 1. Observability & Security
    anonymizer = build_anonymizer_adapter(settings)
    langfuse_client = resolve_langfuse_client(settings, anonymizer=anonymizer)
    telemetry_port = build_telemetry_adapter(settings, langfuse_client=langfuse_client)

    # 2. Ingestion, Persistence & Idempotency
    media_ingestion_port = build_media_ingestion_adapter(settings)
    vault_port = build_vault_adapter(settings)
    ledger_port = SqliteLedgerAdapter(db_path=settings.sqlite_ledger_path)

    # 3. SRE & DORA Metrics Telemetry
    metrics_port = build_metrics_adapter(settings)

    # 4. Prompt Governance, Cognitive & Judge LLM Engines
    prompt_provider = build_prompt_provider(settings, langfuse_client=langfuse_client)
    synthesis_adapter = build_gemini_synthesis_adapter(settings, langfuse_client=langfuse_client)
    llm_indexing_port = build_indexing_adapter(
        settings,
        synthesis_adapter=synthesis_adapter,
        web_index=web_index,
        langfuse_client=langfuse_client,
    )
    llm_judge = build_llm_judge_adapter(
        settings,
        langfuse_client=langfuse_client,
        prompt_provider=prompt_provider,
    )
    from cresmo.infrastructure.adapters.llm.ollama_critique_adapter import (
        OllamaCritiqueAdapter,
    )

    critique_synthesizer = OllamaCritiqueAdapter(
        llm_transformation_port=llm_indexing_port,
        prompt_provider=prompt_provider,
    )

    # 5. Pipeline Stage Runner & Closed-Loop Verifier (ADR-030, ADR-031)
    stage_factory = StageFactory(settings=settings)
    stage_runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=telemetry_port,
            metrics_port=metrics_port,
            llm_judge=llm_judge,
            judge_blocking=getattr(settings, "judge_blocking", False),
            judge_max_attempts=getattr(settings, "judge_max_attempts", 2),
            prompt_provider=prompt_provider,
            llm_transformation_port=synthesis_adapter,
            stage_factory=stage_factory,
            critique_synthesizer=critique_synthesizer,
            ledger_port=ledger_port,
        )
    )

    # 6. Pipeline Assembly
    batch_size = batch_size_override if batch_size_override is not None else settings.batch_size
    taxonomy_port = build_taxonomy_adapter(settings)

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        vault_port=vault_port,
        stage_runner=stage_runner,
        ledger_port=ledger_port,
        batch_size=batch_size,
        settings=settings,
        llm_indexing_port=llm_indexing_port,
        taxonomy_port=taxonomy_port,
    )


def build_stage_runner(settings: CresmoSettings | None = None) -> PipelineStageRunner:
    """Build and wire an isolated PipelineStageRunner instance with resolved settings.

    Args:
        settings: Optional custom or partial application settings.

    Returns:
        Fully wired PipelineStageRunner with LLM transformation and telemetry adapters.
    """
    settings = resolve_shared_settings(settings)
    pipeline = build_pipeline(settings)
    return pipeline.stage_runner


def build_sync_channel_use_case(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired."""
    settings = resolve_shared_settings(settings)
    pipeline = build_pipeline(settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(settings, check_ffmpeg=check_ffmpeg)

    if pipeline.ledger_port is None:
        raise RuntimeError("Ledger port must be wired for channel sync.")

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


__all__ = [
    "PreflightHealthChecker",
    "build_anonymizer_adapter",
    "build_concat_master_use_case",
    "build_discover_batch_sources_use_case",
    "build_gemini_synthesis_adapter",
    "build_index_raw_use_case",
    "build_indexing_adapter",
    "build_media_ingestion_adapter",
    "build_metrics_adapter",
    "build_pipeline",
    "build_preflight_checker",
    "build_prompt_provider",
    "build_stage_runner",
    "build_sync_channel_use_case",
    "build_taxonomy_adapter",
    "build_telemetry_adapter",
    "build_unify_duplicates_use_case",
    "build_vault_adapter",
    "get_shared_settings",
    "probe_http_endpoint",
    "probe_langfuse_ready",
    "reset_shared_settings",
    "resolve_langfuse_client",
    "resolve_shared_settings",
]
