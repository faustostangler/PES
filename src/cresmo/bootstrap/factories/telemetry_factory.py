"""Telemetry and observability client factory for Cresmo.

Conforms to:
- ADR-014: Fail-Fast Preflight Probing & Telemetry Circuit Breaking
- ADR-017: Langfuse Otel Span Masking and Scrubbing
- ADR-027: Unified Telemetry Vocabulary and Langfuse Conventions
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from typing import Any

import structlog

from cresmo.application.ports import (
    AnonymizerPort,
    MetricsPort,
    NoOpTelemetryPort,
    TelemetryPort,
)
from cresmo.bootstrap.factories.settings_factory import resolve_shared_settings
from cresmo.infrastructure.adapters.anonymization.anonymizer_adapter import (
    NoOpAnonymizerAdapter,
    RegexAnonymizerAdapter,
)
from cresmo.infrastructure.adapters.metrics.noop_metrics_adapter import NoOpMetricsAdapter
from cresmo.infrastructure.adapters.metrics.prometheus_metrics_adapter import (
    PrometheusMetricsAdapter,
)
from cresmo.infrastructure.adapters.system.preflight_probe_adapter import probe_http_endpoint
from cresmo.infrastructure.adapters.telemetry.opentelemetry_adapter import (
    OpenTelemetryAdapter,
    name_telemetry_threads,
)
from cresmo.infrastructure.config import ObservabilitySettings

logger = structlog.get_logger(__name__)


def probe_langfuse_ready(host: str, timeout_seconds: float = 2.0) -> bool:
    """Active preflight probe verifying whether the Langfuse server is responding to health pings.

    Args:
        host: Root Langfuse endpoint URL (e.g. 'http://localhost:3000').
        timeout_seconds: Probe socket timeout in seconds (default: 2.0s).

    Returns:
        True if the server responded with HTTP < 500, False if unreachable or timed out.
    """
    normalized_host = host.rstrip("/")
    probe_url = f"{normalized_host}/api/public/health"
    if probe_http_endpoint(probe_url, timeout_seconds=timeout_seconds):
        return True
    if "localhost" in normalized_host:
        fallback_url = probe_url.replace("localhost", "127.0.0.1")
        return probe_http_endpoint(fallback_url, timeout_seconds=timeout_seconds)
    return False


def _clean_langfuse_env() -> None:
    """Clean Langfuse environment variables to prevent spurious autoinstrumentation retries."""
    os.environ.pop("LANGFUSE_PUBLIC_KEY", None)
    os.environ.pop("LANGFUSE_SECRET_KEY", None)
    os.environ.pop("LANGFUSE_HOST", None)
    os.environ.pop("LANGFUSE_TRACING_ENVIRONMENT", None)
    os.environ.pop("OTEL_EXPORTER_OTLP_TIMEOUT", None)


def is_default_export_span(span: Any) -> bool:
    """Evaluate default Langfuse span export criteria lazily (ADR-055)."""
    from langfuse.span_filter import is_default_export_span as _real_is_default_export_span

    return _real_is_default_export_span(span)


def _build_should_export_span() -> Callable[[Any], bool]:
    """Build filter predicate checking default spans and cresmo.* scopes."""

    def should_export_cresmo_span(span: Any) -> bool:
        scope = getattr(span, "instrumentation_scope", None)
        scope_name = getattr(scope, "name", None)
        span_name = getattr(span, "name", None)
        is_default = is_default_export_span(span)
        is_cresmo = scope is not None and scope.name.startswith("cresmo.")
        export = is_default or is_cresmo
        # TEMPORARY: Keep span export debug output during ADR-070 OTel verification; remove once stabilized.
        print(
            f"[SPAN DEBUG] name={span_name!r} scope={scope_name!r} "
            f"default={is_default} cresmo={is_cresmo} -> export={export}"
        )
        return export

    return should_export_cresmo_span


def _build_mask_hook(
    anonymizer: AnonymizerPort | None,
) -> Callable[..., Any] | None:
    """Construct export-stage span attribute masking hook if anonymizer is provided."""
    if anonymizer is None:
        return None

    def mask_otel_spans(*, params: Any) -> Any:
        from langfuse.types import MaskOtelSpansResult, OtelSpanPatch

        span_patches = {}
        for identifier, span in params.spans.items():
            raw_attrs = span.attributes or {}
            sanitized = anonymizer.mask_span_attributes(raw_attrs)
            if sanitized != raw_attrs:
                delete_attrs = [k for k in raw_attrs if k not in sanitized]
                set_attributes = {k: v for k, v in sanitized.items() if raw_attrs.get(k) != v}
                span_patches[identifier] = OtelSpanPatch(
                    delete_attributes=tuple(delete_attrs),
                    set_attributes=set_attributes,
                )
        return MaskOtelSpansResult(span_patches=span_patches) if span_patches else None

    return mask_otel_spans


def _resolve_langfuse_class() -> Any:
    """Resolve active Langfuse class lazily, supporting test mocks and patches (ADR-055)."""
    cur = globals().get("Langfuse")
    if cur is not None and cur is not _LAZY_LANGFUSE_SENTINEL:
        return cur
    mod = sys.modules.get("langfuse")
    if mod is not None and hasattr(mod, "Langfuse"):
        return mod.Langfuse
    from langfuse import Langfuse as _RealLangfuse

    return _RealLangfuse


class _LazyLangfuse:
    """Lazy callable proxy for Langfuse client instantiation (ADR-055)."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        cls = _resolve_langfuse_class()
        if cls is self or cls is _LAZY_LANGFUSE_SENTINEL:
            from langfuse import Langfuse as _RealLangfuse

            return _RealLangfuse(*args, **kwargs)
        return cls(*args, **kwargs)


_LAZY_LANGFUSE_SENTINEL = _LazyLangfuse()
Langfuse: Any = _LAZY_LANGFUSE_SENTINEL


def resolve_langfuse_client(
    settings: ObservabilitySettings,
    anonymizer: AnonymizerPort | None = None,
) -> Any | None:
    """Instantiate and return Langfuse client if configured and actively reachable.

    Performs an active preflight probe against the Langfuse health endpoint before client
    creation. If unreachable, logs a single-line warning with the remediation command
    and returns None, preventing uncatchable OpenTelemetry background retry storms per ADR-014.
    Also configures should_export_span allowlisting and export-stage masking per ADR-017.

    Args:
        settings: Validated observability configuration.
        anonymizer: Optional AnonymizerPort adapter for export-stage PII scrubbing.

    Returns:
        Configured Langfuse client instance or None if not configured/unreachable.
    """
    langfuse_cfg = settings.langfuse
    runtime_cfg = settings.runtime
    if not (langfuse_cfg.public_key and langfuse_cfg.secret_key.get_secret_value()):
        return None

    # Active Preflight Probe
    if runtime_cfg.enable_preflight_probes and not probe_langfuse_ready(
        langfuse_cfg.host, timeout_seconds=runtime_cfg.preflight_probe_timeout_seconds
    ):
        sys.stderr.write(
            f"[preflight] Langfuse server at '{langfuse_cfg.host}' is unreachable. "
            "Telemetry bypassed to prevent OpenTelemetry retry loops.\n"
            "            To enable observability: docker compose -f docker-compose.langfuse.yml up -d\n"
        )
        _clean_langfuse_env()
        return None

    try:
        timeout_sec = langfuse_cfg.timeout_seconds
        resolved_env = langfuse_cfg.environment
        os.environ["LANGFUSE_PUBLIC_KEY"] = langfuse_cfg.public_key
        os.environ["LANGFUSE_SECRET_KEY"] = langfuse_cfg.secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = langfuse_cfg.host
        os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = resolved_env
        os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] = str(timeout_sec)

        init_kwargs: dict[str, Any] = {
            "public_key": langfuse_cfg.public_key,
            "secret_key": langfuse_cfg.secret_key.get_secret_value(),
            "host": langfuse_cfg.host,
            "timeout": timeout_sec,
            "should_export_span": _build_should_export_span(),
            "environment": resolved_env,
        }
        mask_hook = _build_mask_hook(anonymizer)
        if mask_hook is not None:
            init_kwargs["mask_otel_spans"] = mask_hook

        client = Langfuse(**init_kwargs)
        name_telemetry_threads(client)
        return client
    except Exception as exc:  # noqa: BLE001
        logger.warning("[composition] Failed to initialize Langfuse client: %s", exc)
        _clean_langfuse_env()
        return None


def build_anonymizer_adapter(
    settings: ObservabilitySettings | None = None,
) -> AnonymizerPort:
    """Instantiate AnonymizerPort adapter based on observability configuration."""
    resolved = settings if settings is not None else resolve_shared_settings(None).observability
    if resolved.runtime.anonymization_enabled:
        return RegexAnonymizerAdapter()
    return NoOpAnonymizerAdapter()


def build_telemetry_adapter(
    settings: ObservabilitySettings | None = None,
    langfuse_client: Any | None = None,
) -> TelemetryPort:
    """Instantiate TelemetryPort choosing between OpenTelemetryAdapter and canonical NoOpTelemetryPort."""
    resolved = settings if settings is not None else resolve_shared_settings(None).observability
    if langfuse_client is not None:
        return OpenTelemetryAdapter(
            langfuse_client=langfuse_client,
            pipeline_version=resolved.runtime.pipeline_version,
            git_sha=resolved.runtime.git_sha,
        )
    return NoOpTelemetryPort()


def build_metrics_adapter(
    settings: ObservabilitySettings | None = None,
) -> MetricsPort:
    """Instantiate MetricsPort adapter choosing between Prometheus and NoOp."""
    resolved = settings if settings is not None else resolve_shared_settings(None).observability
    if resolved.prometheus.enabled:
        return PrometheusMetricsAdapter()
    return NoOpMetricsAdapter()
