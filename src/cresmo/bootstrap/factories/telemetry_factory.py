"""Telemetry and observability client factory for Cresmo.

Conforms to:
- ADR-014: Fail-Fast Preflight Probing & Telemetry Circuit Breaking
- ADR-017: Langfuse Otel Span Masking and Scrubbing
- ADR-027: Unified Telemetry Vocabulary and Langfuse Conventions
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
    NoOpTelemetryAdapter,
    OpenTelemetryAdapter,
    name_telemetry_threads,
)
from cresmo.infrastructure.config import CresmoSettings

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
    os.environ.pop("OTEL_EXPORTER_OTLP_TIMEOUT", None)


def is_default_export_span(span: Any) -> bool:
    """Evaluate default Langfuse span export criteria lazily (ADR-055)."""
    from langfuse.span_filter import is_default_export_span as _real_is_default_export_span

    return _real_is_default_export_span(span)


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
        timeout_seconds = getattr(settings, "preflight_probe_timeout_seconds", 1.0)
        if not probe_langfuse_ready(settings.langfuse_host, timeout_seconds=timeout_seconds):
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

        client = Langfuse(**init_kwargs)
        name_telemetry_threads(client)
        return client
    except Exception as exc:  # noqa: BLE001
        logger.warning("[composition] Failed to initialize Langfuse client: %s", exc)
        _clean_langfuse_env()
        return None


def build_anonymizer_adapter(
    settings: CresmoSettings | None = None,
) -> AnonymizerPort:
    """Instantiate AnonymizerPort adapter based on settings configuration."""
    resolved_settings = resolve_shared_settings(settings)
    if getattr(resolved_settings, "anonymization_enabled", True):
        return RegexAnonymizerAdapter()
    return NoOpAnonymizerAdapter()


def build_telemetry_adapter(
    settings: CresmoSettings | None = None,
    langfuse_client: Any | None = None,
) -> TelemetryPort:
    """Instantiate TelemetryPort adapter choosing between OpenTelemetry and NoOp."""
    resolved_settings = resolve_shared_settings(settings)
    if langfuse_client is not None:
        return OpenTelemetryAdapter(
            langfuse_client=langfuse_client,
            pipeline_version=resolved_settings.pipeline_version,
        )
    return NoOpTelemetryAdapter()


def build_metrics_adapter(
    settings: CresmoSettings | None = None,
) -> MetricsPort:
    """Instantiate MetricsPort adapter choosing between Prometheus and NoOp."""
    resolved_settings = resolve_shared_settings(settings)
    if getattr(resolved_settings, "prometheus_enabled", True):
        return PrometheusMetricsAdapter()
    return NoOpMetricsAdapter()
