"""Telemetry, observability, and structured logging settings for Cresmo.

Encapsulates Langfuse tracing credentials, anonymization controls, preflight
probe toggles, Prometheus Golden Signals exposition, and structured logging.

Conforms to:
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-063: Dynamic Pipeline Versioning via importlib.metadata
    - ADR-069: Modular Domain Settings Package
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from cresmo.infrastructure.config.catalog import (
    DEFAULT_LANGFUSE_ENVIRONMENT,
    DEFAULT_LANGFUSE_PROMPT_LABEL,
    LANGFUSE_ENVIRONMENT_PATTERN,
    _normalize_str_choice,
    resolve_default_pipeline_version,
)

_LANGFUSE_ENVIRONMENT_REGEX = re.compile(LANGFUSE_ENVIRONMENT_PATTERN)

__all__ = ["TelemetrySettings"]


class TelemetrySettings(BaseSettings):
    """Observability, tracing, metrics, and logging configuration settings."""

    model_config = SettingsConfigDict(extra="ignore")

    def __init__(
        self,
        *args: Any,
        _env_file: Path | str | None | Any = ...,
        **values: Any,
    ) -> None:
        """Initialize telemetry settings with optional env file and keyword alias handling."""
        if _env_file is not ...:
            values["_env_file"] = _env_file
        if "pipeline_version" in values and "CRESMO_PIPELINE_VERSION" not in values:
            values["CRESMO_PIPELINE_VERSION"] = values.pop("pipeline_version")
        super().__init__(*args, **values)

    langfuse_secret_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("langfuse_secret_key", "LANGFUSE_SECRET_KEY"),
        description="Langfuse secret key for evaluation and observability.",
    )
    langfuse_public_key: str = Field(
        default="",
        validation_alias=AliasChoices("langfuse_public_key", "LANGFUSE_PUBLIC_KEY"),
        description="Langfuse public key for evaluation and observability.",
    )
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        validation_alias=AliasChoices("langfuse_host", "LANGFUSE_HOST", "LANGFUSE_BASE_URL"),
        description="Langfuse telemetry endpoint URL.",
    )
    langfuse_environment: str = Field(
        default=DEFAULT_LANGFUSE_ENVIRONMENT,
        validation_alias=AliasChoices(
            "LANGFUSE_TRACING_ENVIRONMENT",
            "langfuse_environment",
            "LANGFUSE_ENVIRONMENT",
        ),
        description="Langfuse telemetry environment (e.g. 'production', 'staging', 'development').",
    )

    @field_validator("langfuse_environment", mode="before")
    @classmethod
    def _validate_langfuse_environment(cls, value: Any) -> str:
        """Normalize and validate Langfuse environment name against official regex (ADR-072)."""
        normalized = _normalize_str_choice(value)
        if not isinstance(normalized, str) or not _LANGFUSE_ENVIRONMENT_REGEX.fullmatch(normalized):
            msg = (
                "langfuse_environment must match '^(?!langfuse)[a-z0-9-_]{1,40}$' "
                "(lowercase letters, digits, hyphens, underscores; max 40 chars; "
                "cannot start with 'langfuse')."
            )
            raise ValueError(msg)
        return normalized

    langfuse_prompt_label: str = Field(
        default=DEFAULT_LANGFUSE_PROMPT_LABEL,
        description="Active prompt label tag in Langfuse (e.g. 'production', 'staging').",
    )
    langfuse_timeout_seconds: int = Field(
        default=30,
        description="Read and connect timeout in seconds for Langfuse client and OpenTelemetry exporter.",
    )
    anonymization_enabled: bool = Field(
        default=True,
        description="Enable PII and credential masking in telemetry, span attributes, and exports.",
    )
    preflight_probe_timeout_seconds: float = Field(
        default=2.0,
        description="Socket timeout in seconds for active preflight probes (Langfuse, Ollama).",
    )
    enable_preflight_probes: bool = Field(
        default=True,
        description="Enable active HTTP preflight probes before initializing telemetry or remote services.",
    )
    pipeline_version: str = Field(
        default_factory=resolve_default_pipeline_version,
        validation_alias="CRESMO_PIPELINE_VERSION",
        description="Canonical pipeline version tag emitted to OpenTelemetry spans and Langfuse traces.",
    )
    git_sha: str | None = Field(
        default=None,
        validation_alias=AliasChoices("git_sha", "GIT_SHA", "CRESMO_GIT_SHA"),
        description="Optional Git commit SHA propagated from runtime or CI environment.",
    )
    prometheus_enabled: bool = Field(
        default=True,
        description="Whether Prometheus SRE Golden Signals and DORA metrics collection is enabled.",
    )
    prometheus_port: int = Field(
        default=9090,
        description="Local Prometheus scraping and exposition port.",
    )
    log_level: str = Field(
        default="WARNING",
        validation_alias=AliasChoices("log_level", "LOG_LEVEL", "CRESMO_LOG_LEVEL"),
        description="Root logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    log_format: str = Field(
        default="json",
        validation_alias=AliasChoices("log_format", "LOG_FORMAT", "CRESMO_LOG_FORMAT"),
        description="Log output format: 'json' for Loki structured ingestion, 'text' for local dev.",
    )
