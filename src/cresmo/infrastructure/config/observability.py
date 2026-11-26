"""Observability, tracing, metrics, and logging sub-models for Cresmo.

Conforms to:
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-063: Dynamic Pipeline Versioning via importlib.metadata
    - ADR-072: Langfuse Tracing Environment Governance
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

import re
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from cresmo.infrastructure.config.catalog import (
    DEFAULT_LANGFUSE_ENVIRONMENT,
    DEFAULT_LANGFUSE_PROMPT_LABEL,
    LANGFUSE_ENVIRONMENT_PATTERN,
    normalize_str_choice,
    resolve_default_pipeline_version,
)

_LANGFUSE_ENVIRONMENT_REGEX = re.compile(LANGFUSE_ENVIRONMENT_PATTERN)
DEFAULT_LANGFUSE_HOST: Final[str] = "https://cloud.langfuse.com"
DEFAULT_LANGFUSE_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_PROMETHEUS_ENDPOINT: Final[str] = "http://localhost:9090"
DEFAULT_LOGGING_LEVEL: Final[str] = "WARNING"
DEFAULT_PREFLIGHT_PROBE_TIMEOUT_SECONDS: Final[float] = 2.0


class LangfuseSettings(BaseModel):
    """Immutable Langfuse tracing and prompt registry settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    secret_key: SecretStr = Field(
        default=SecretStr(""),
        description="Langfuse secret key for evaluation and observability.",
    )
    public_key: str = Field(
        default="",
        description="Langfuse public key for evaluation and observability.",
    )
    host: str = Field(
        default=DEFAULT_LANGFUSE_HOST,
        description="Langfuse telemetry endpoint URL.",
    )
    environment: str = Field(
        default=DEFAULT_LANGFUSE_ENVIRONMENT,
        description="Langfuse telemetry environment (e.g. 'production', 'staging', 'development').",
    )
    prompt_label: str = Field(
        default=DEFAULT_LANGFUSE_PROMPT_LABEL,
        description="Active prompt label tag in Langfuse (e.g. 'production', 'staging').",
    )
    timeout_seconds: int = Field(
        default=DEFAULT_LANGFUSE_TIMEOUT_SECONDS,
        ge=1,
        description="Read and connect timeout in seconds for Langfuse client and OTel exporter.",
    )

    @field_validator("environment", mode="before")
    @classmethod
    def _validate_environment(cls, value: Any) -> str:
        """Normalize and validate Langfuse environment name against official regex (ADR-072)."""
        normalized = normalize_str_choice(value)
        if not isinstance(normalized, str) or not _LANGFUSE_ENVIRONMENT_REGEX.fullmatch(normalized):
            msg = (
                "langfuse.environment must match '^(?!langfuse)[a-z0-9-_]{1,40}$' "
                "(lowercase letters, digits, hyphens, underscores; max 40 chars; "
                "cannot start with 'langfuse')."
            )
            raise ValueError(msg)
        return normalized


class PrometheusSettings(BaseModel):
    """Immutable Prometheus v3 native OTLP HTTP metrics settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(
        default=True,
        description="Whether Prometheus SRE Golden Signals and DORA OTLP push collection is enabled.",
    )
    endpoint: str = Field(
        default=DEFAULT_PROMETHEUS_ENDPOINT,
        description="Prometheus v3 server base URL hosting /api/v1/otlp/v1/metrics and /-/ready.",
    )


class LoggingSettings(BaseModel):
    """Immutable structlog output configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    level: str = Field(
        default=DEFAULT_LOGGING_LEVEL,
        description="Root logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format: 'json' for Loki structured ingestion, 'text' for local dev.",
    )

    @field_validator("format", mode="before")
    @classmethod
    def _normalize_format(cls, value: Any) -> Any:
        return normalize_str_choice(value)


class RuntimeTelemetrySettings(BaseModel):
    """Immutable release identity, anonymization, and preflight probe controls."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pipeline_version: str = Field(
        default_factory=resolve_default_pipeline_version,
        description="Canonical pipeline version tag emitted to OpenTelemetry spans and Langfuse traces.",
    )
    git_sha: str | None = Field(
        default=None,
        description="Optional Git commit SHA propagated from runtime or CI environment.",
    )
    anonymization_enabled: bool = Field(
        default=True,
        description="Enable PII and credential masking in telemetry, span attributes, and exports.",
    )
    enable_preflight_probes: bool = Field(
        default=True,
        description="Enable active HTTP preflight probes before initializing telemetry or remote services.",
    )
    preflight_probe_timeout_seconds: float = Field(
        default=DEFAULT_PREFLIGHT_PROBE_TIMEOUT_SECONDS,
        gt=0.0,
        description="Socket timeout in seconds for active preflight probes (Langfuse, Ollama).",
    )


class ObservabilitySettings(BaseModel):
    """Composed observability configuration for Langfuse, Prometheus, logging, and runtime controls."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    langfuse: LangfuseSettings = Field(default_factory=LangfuseSettings)
    prometheus: PrometheusSettings = Field(default_factory=PrometheusSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    runtime: RuntimeTelemetrySettings = Field(default_factory=RuntimeTelemetrySettings)


__all__ = [
    "LangfuseSettings",
    "LoggingSettings",
    "ObservabilitySettings",
    "PrometheusSettings",
    "RuntimeTelemetrySettings",
]
