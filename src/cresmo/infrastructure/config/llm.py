"""LLM provider, credential, and generation sub-models for Cresmo.

Conforms to:
    - ADR-064: Gemini Free-Tier Catalog & Thinking Level Governance
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from typing import Annotated, Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from pydantic_settings import NoDecode

from cresmo.infrastructure.config.catalog import (
    DEFAULT_GEMINI_FALLBACK_MODEL,
    DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_GEMINI_TIMEOUT_SECONDS,
    GEMINI_FREE_TIER_MODELS,
    GeminiThinkingLevel,
    normalize_str_choice,
    parse_comma_separated_strings,
)

MIN_GEMINI_MAX_OUTPUT_TOKENS: Final[int] = 256
MAX_GEMINI_MAX_OUTPUT_TOKENS: Final[int] = 1_048_576
MIN_GEMINI_TIMEOUT_SECONDS: Final[float] = 1.0
DEFAULT_OLLAMA_BASE_URL: Final[str] = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL: Final[str] = "qwen2.5:7b"
DEFAULT_OLLAMA_TIMEOUT_SECONDS: Final[float] = 300.0
DEFAULT_OLLAMA_WARMUP_TIMEOUT_SECONDS: Final[float] = 300.0
DEFAULT_OLLAMA_KEEP_ALIVE: Final[str] = "1h"
DEFAULT_OLLAMA_NUM_PREDICT: Final[int] = 0
DEFAULT_OLLAMA_INDEXING_TEMPERATURE: Final[float] = 0.2
MAX_OLLAMA_TEMPERATURE: Final[float] = 2.0


class GeminiSettings(BaseModel):
    """Immutable Google Gemini credentials, model selection, and inference limits."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    api_keys: Annotated[tuple[SecretStr, ...], NoDecode] = Field(
        default=(),
        description="Google Gemini API Keys for quota-aware failover and rotation.",
    )
    model: str = Field(
        default=DEFAULT_GEMINI_MODEL,
        description=(
            "Default Gemini model variant for pipeline stages. "
            f"Free-tier catalog (GEMINI_FREE_TIER_MODELS): {', '.join(GEMINI_FREE_TIER_MODELS)}."
        ),
    )
    fallback_model: str = Field(
        default=DEFAULT_GEMINI_FALLBACK_MODEL,
        description="Fallback Gemini model variant if primary hits demand spikes or errors.",
    )
    thinking_level: GeminiThinkingLevel = Field(
        default=DEFAULT_GEMINI_THINKING_LEVEL,
        description="Reasoning effort level ('minimal', 'low', 'medium', 'high', 'xhigh').",
    )
    max_output_tokens: int = Field(
        default=DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
        ge=MIN_GEMINI_MAX_OUTPUT_TOKENS,
        le=MAX_GEMINI_MAX_OUTPUT_TOKENS,
        description="Maximum output token ceiling (thinking + response tokens) for Gemini requests.",
    )
    timeout_seconds: float = Field(
        default=DEFAULT_GEMINI_TIMEOUT_SECONDS,
        ge=MIN_GEMINI_TIMEOUT_SECONDS,
        description="HTTP/TCP socket timeout in seconds for Google Gemini API inference requests.",
    )

    @field_validator("api_keys", mode="before")
    @classmethod
    def _parse_api_keys(cls, value: Any) -> Any:
        """Normalize comma/JSON string, SecretStr, or sequence into tuple[SecretStr, ...]."""
        if isinstance(value, SecretStr):
            return (value,) if value.get_secret_value().strip() else ()
        if isinstance(value, str):
            return tuple(SecretStr(part) for part in parse_comma_separated_strings(value))
        if isinstance(value, (list, tuple)):
            secrets: list[SecretStr] = []
            for item in value:
                if isinstance(item, SecretStr):
                    if item.get_secret_value().strip():
                        secrets.append(item)
                elif isinstance(item, str) and item.strip():
                    secrets.append(SecretStr(item.strip()))
                else:
                    raise ValueError(f"Invalid Gemini API key entry: {item!r}")
            return tuple(secrets)
        return value

    @field_validator("thinking_level", mode="before")
    @classmethod
    def _normalize_thinking_level(cls, value: Any) -> Any:
        return normalize_str_choice(value)

    def primary_api_key(self) -> SecretStr:
        """Return primary Gemini API key or empty SecretStr when unconfigured."""
        return self.api_keys[0] if self.api_keys else SecretStr("")


class OllamaSettings(BaseModel):
    """Immutable local Ollama server connection and sampling settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    base_url: str = Field(
        default=DEFAULT_OLLAMA_BASE_URL,
        description="Local Ollama endpoint URL.",
    )
    model: str = Field(
        default=DEFAULT_OLLAMA_MODEL,
        description="Local Ollama model variant for conceptual indexing and fallback judging.",
    )
    timeout_seconds: float = Field(
        default=DEFAULT_OLLAMA_TIMEOUT_SECONDS,
        ge=MIN_GEMINI_TIMEOUT_SECONDS,
        description="HTTP timeout in seconds for local Ollama inference requests.",
    )
    warmup_timeout_seconds: float = Field(
        default=DEFAULT_OLLAMA_WARMUP_TIMEOUT_SECONDS,
        ge=MIN_GEMINI_TIMEOUT_SECONDS,
        description="Extended HTTP timeout in seconds for initial Ollama model preload into VRAM.",
    )
    keep_alive: str = Field(
        default=DEFAULT_OLLAMA_KEEP_ALIVE,
        description="Duration to keep the model loaded in Ollama VRAM/RAM (e.g. '1h', '60m', '-1').",
    )
    num_predict: int = Field(
        default=DEFAULT_OLLAMA_NUM_PREDICT,
        ge=0,
        description="Maximum tokens predicted by local Ollama model (0 means unconstrained).",
    )
    indexing_temperature: float = Field(
        default=DEFAULT_OLLAMA_INDEXING_TEMPERATURE,
        ge=0.0,
        le=MAX_OLLAMA_TEMPERATURE,
        description="Sampling temperature for conceptual indexing.",
    )


class LlmSettings(BaseModel):
    """Composed LLM provider configuration combining Gemini, Ollama, and provider routing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    indexing_provider: Literal["ollama", "gemini"] = Field(
        default="ollama",
        description="Provider for raw transcript conceptual indexing ('ollama' or 'gemini').",
    )

    @field_validator("indexing_provider", mode="before")
    @classmethod
    def _normalize_indexing_provider(cls, value: Any) -> Any:
        return normalize_str_choice(value)


__all__ = [
    "GeminiSettings",
    "LlmSettings",
    "OllamaSettings",
]
