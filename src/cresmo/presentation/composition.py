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

import logging
import os
import sys
from collections.abc import Callable
from typing import Any

from langfuse import Langfuse
from langfuse.span_filter import is_default_export_span
from langfuse.types import MaskOtelSpansParams, MaskOtelSpansResult, OtelSpanPatch

from cresmo.application.pipeline import (
    CresmoPipeline,
    PipelineDependencies,
    PipelineStageRunner,
    StageFactory,
)
from cresmo.application.ports import (
    AnonymizerPort,
)
from cresmo.application.services.preflight import (
    PreflightHealthChecker,
    probe_http_endpoint,
)
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.infrastructure.adapters.ollama_critique_adapter import OllamaCritiqueAdapter
from cresmo.infrastructure.adapters.opentelemetry_adapter import (
    name_telemetry_threads,
)
from cresmo.infrastructure.adapters.sqlite_ledger_adapter import SqliteLedgerAdapter
from cresmo.infrastructure.config import CresmoSettings
from cresmo.infrastructure.logging_config import configure_logging
from cresmo.presentation.factories.adapter_factory import (
    _resolve_cookie_file,
    build_gemini_synthesis_adapter,
    build_indexing_adapter,
    build_media_ingestion_adapter,
    build_preflight_checker,
    build_prompt_provider,
    build_vault_adapter,
)
from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter
from cresmo.presentation.factories.settings_factory import (
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)
from cresmo.presentation.factories.telemetry_factory import (
    build_anonymizer_adapter,
    build_metrics_adapter,
    build_telemetry_adapter,
)
from cresmo.presentation.factories.use_case_factory import (
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_index_raw_use_case,
    build_unify_duplicates_use_case,
)

logger = logging.getLogger(__name__)


def probe_langfuse_ready(host: str, timeout_seconds: float = 1.0) -> bool:
    """Active preflight probe verifying whether the Langfuse server is responding to health pings.

    Args:
        host: Root Langfuse endpoint URL (e.g. 'http://localhost:3000').
        timeout_seconds: Probe socket timeout in seconds (default: 1.0s).

    Returns:
        True if the server responded with HTTP < 500, False if unreachable or timed out.
    """
    normalized_host = host.rstrip("/")
    probe_url = f"{normalized_host}/api/public/health"
    return probe_http_endpoint(probe_url, timeout_seconds=timeout_seconds)


def _clean_langfuse_env() -> None:
    """Clean Langfuse environment variables to prevent spurious autoinstrumentation retries."""
    os.environ.pop("LANGFUSE_PUBLIC_KEY", None)
    os.environ.pop("LANGFUSE_SECRET_KEY", None)
    os.environ.pop("LANGFUSE_HOST", None)
    os.environ.pop("OTEL_EXPORTER_OTLP_TIMEOUT", None)


def _build_should_export_span() -> Callable[[Any], bool]:
    """Build filter predicate checking default spans and cresmo.* scopes."""

    def should_export_cresmo_span(span: Any) -> bool:
        if is_default_export_span(span):
            return True
        scope = getattr(span, "instrumentation_scope", None)
        return scope is not None and scope.name.startswith("cresmo.")

    return should_export_cresmo_span


def _build_mask_hook(
    anonymizer: AnonymizerPort | None,
) -> Callable[..., MaskOtelSpansResult | None] | None:
    """Construct export-stage span attribute masking hook if anonymizer is provided."""
    if anonymizer is None:
        return None

    def mask_otel_spans(*, params: MaskOtelSpansParams) -> MaskOtelSpansResult | None:
        patches = {}
        for identifier, span in params.spans.items():
            raw_attrs = span.attributes or {}
            sanitized = anonymizer.mask_span_attributes(raw_attrs)
            if sanitized != raw_attrs:
                delete_attrs = [k for k in raw_attrs if k not in sanitized]
                set_attrs = {k: v for k, v in sanitized.items() if raw_attrs.get(k) != v}
                patches[identifier] = OtelSpanPatch(
                    delete_attributes=tuple(delete_attrs),
                    set_attributes=set_attrs,
                )
        return MaskOtelSpansResult(span_patches=patches) if patches else None

    return mask_otel_spans


def resolve_langfuse_client(
    settings: CresmoSettings,
    anonymizer: AnonymizerPort | None = None,
) -> Any | None:
    """Instantiate and return Langfuse client if configured and actively reachable.

    Performs an active preflight probe against the Langfuse health endpoint before client
    creation. If unreachable, logs a single-line warning with the remediation command
    and returns None, preventing uncatchable OpenTelemetry background retry storms per ADR-014.
    Also configures should_export_span allowlisting and export-stage masking per ADR-017.

    Args:
        settings: Validated application configuration.
        anonymizer: Optional AnonymizerPort adapter for export-stage PII scrubbing.

    Returns:
        Configured Langfuse client instance or None if not configured/unreachable.
    """
    if not (settings.langfuse_public_key and settings.langfuse_secret_key.get_secret_value()):
        return None

    # Active Preflight Probe
    if getattr(settings, "enable_preflight_probes", True):
        timeout = getattr(settings, "preflight_probe_timeout_seconds", 1.0)
        if not probe_langfuse_ready(settings.langfuse_host, timeout_seconds=timeout):
            sys.stderr.write(
                f"[preflight] Langfuse server at '{settings.langfuse_host}' is unreachable. "
                "Telemetry bypassed to prevent OpenTelemetry retry loops.\n"
                "            To enable observability: docker compose -f docker-compose.langfuse.yml up -d\n"
            )
            _clean_langfuse_env()
            return None

    try:
        timeout_sec = getattr(settings, "langfuse_timeout_seconds", 30)
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host
        os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] = str(timeout_sec)

        init_kwargs: dict[str, Any] = {
            "public_key": settings.langfuse_public_key,
            "secret_key": settings.langfuse_secret_key.get_secret_value(),
            "host": settings.langfuse_host,
            "timeout": timeout_sec,
            "should_export_span": _build_should_export_span(),
            "environment": getattr(settings, "langfuse_environment", "development"),
        }
        mask_hook = _build_mask_hook(anonymizer)
        if mask_hook is not None:
            init_kwargs["mask_otel_spans"] = mask_hook

        langfuse_module = sys.modules.get("langfuse")
        langfuse_cls = (
            getattr(langfuse_module, "Langfuse", Langfuse)
            if langfuse_module is not None
            else Langfuse
        )
        client = langfuse_cls(**init_kwargs)
        name_telemetry_threads(client)
        return client
    except Exception as exc:  # noqa: BLE001
        logger.warning("[composition] Failed to initialize Langfuse client: %s", exc)
        _clean_langfuse_env()
        return None


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
    resolved_settings = resolve_shared_settings(settings)
    resolved_settings.ensure_directories()

    # 0. Structured Logging Configuration (ADR-025)
    configure_logging(
        level=resolved_settings.log_level,
        fmt=resolved_settings.log_format,
    )

    # 1. Observability, Security & Prompt Governance
    anonymizer = build_anonymizer_adapter(resolved_settings)
    langfuse_client = resolve_langfuse_client(resolved_settings, anonymizer=anonymizer)
    telemetry_port = build_telemetry_adapter(resolved_settings, langfuse_client=langfuse_client)
    prompt_provider = build_prompt_provider(resolved_settings, langfuse_client=langfuse_client)

    # 2. Ingestion, Persistence & Idempotency
    media_ingestion_port = build_media_ingestion_adapter(resolved_settings)
    vault_port = build_vault_adapter(resolved_settings)
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    # 3. Cognitive LLM Engines (Synthesis & Fast Indexing)
    llm_synthesis_port = build_gemini_synthesis_adapter(
        resolved_settings, langfuse_client=langfuse_client
    )
    llm_indexing_port = build_indexing_adapter(
        resolved_settings,
        synthesis_adapter=llm_synthesis_port,
        web_index=web_index,
        langfuse_client=langfuse_client,
    )

    # 4. SRE & DORA Metrics Telemetry
    metrics_port = build_metrics_adapter(resolved_settings)

    # 5. LLM Judge & Decision-Model Evaluators (ADR-029)
    llm_judge_port = build_llm_judge_adapter(
        resolved_settings,
        langfuse_client=langfuse_client,
        prompt_provider=prompt_provider,
    )

    # 6. Directed Reflection Critique Synthesizer (ADR-031)
    critique_synthesizer = OllamaCritiqueAdapter(
        llm_transformation_port=llm_indexing_port,
        prompt_provider=prompt_provider,
    )

    # 7. Pipeline Stage Runner & Closed-Loop Verifier (ADR-030, ADR-031)
    stage_factory = StageFactory(settings=resolved_settings)
    stage_runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=telemetry_port,
            metrics_port=metrics_port,
            llm_judge=llm_judge_port,
            judge_blocking=getattr(resolved_settings, "judge_blocking", False),
            judge_max_attempts=getattr(resolved_settings, "judge_max_attempts", 1),
            prompt_provider=prompt_provider,
            llm_transformation_port=llm_synthesis_port,
            stage_factory=stage_factory,
            critique_synthesizer=critique_synthesizer,
            ledger_port=ledger_port,
        )
    )

    # 8. Pipeline Assembly
    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        vault_port=vault_port,
        stage_runner=stage_runner,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        settings=resolved_settings,
        llm_indexing_port=llm_indexing_port,
    )


def build_sync_channel_use_case(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired."""
    resolved_settings = resolve_shared_settings(settings)
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

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
    "_resolve_cookie_file",
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
    "build_sync_channel_use_case",
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
