"""LLM provider, credential, and generation settings for Cresmo.

Conforms to:
    - ADR-064: Gemini Free-Tier Catalog & Thinking Level Governance
    - ADR-069: Modular Domain Settings Package
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from cresmo.application.ports.settings import DEFAULT_LANGUAGE
from cresmo.infrastructure.config.catalog import (
    DEFAULT_GEMINI_FALLBACK_MODEL,
    DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_GEMINI_TIMEOUT_SECONDS,
    GEMINI_FREE_TIER_MODELS,
    GeminiThinkingLevel,
    _customize_comma_list_sources,
    _normalize_str_choice,
)


class LlmSettings(BaseSettings):
    """LLM credentials, model selection, and inference tuning settings."""

    model_config = SettingsConfigDict(extra="ignore")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise settings sources to safely parse comma-separated credentials from env."""
        return _customize_comma_list_sources(
            ("gemini_api_keys",),
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    def __init__(
        self,
        *args: Any,
        _env_file: Path | str | None | Any = ...,
        **values: Any,
    ) -> None:
        """Initialize LLM settings with optional explicit environment file override."""
        if _env_file is not ...:
            values["_env_file"] = _env_file
        if "gemini_api_key" in values and "gemini_api_keys" not in values:
            values["gemini_api_keys"] = values["gemini_api_key"]
        super().__init__(*args, **values)

    gemini_api_keys: list[SecretStr] = Field(
        default_factory=list,
        description="Google Gemini API Keys for quota-aware failover and rotation.",
    )

    @property
    def gemini_api_key(self) -> SecretStr:
        """Primary Google Gemini API Key for backward compatibility."""
        if self.gemini_api_keys:
            return self.gemini_api_keys[0]
        return SecretStr("")

    @model_validator(mode="before")
    @classmethod
    def _normalize_gemini_credentials(cls, data: Any) -> Any:
        """Normalize comma-separated strings or legacy single key into gemini_api_keys."""
        if isinstance(data, dict):
            raw_keys = (
                data.get("gemini_api_keys")
                or data.get("GEMINI_API_KEYS")
                or data.get("gemini_api_key")
                or data.get("GEMINI_API_KEY")
            )
            if raw_keys is not None:
                if isinstance(raw_keys, str):
                    data["gemini_api_keys"] = [
                        SecretStr(p.strip()) for p in raw_keys.split(",") if p.strip()
                    ]
                elif isinstance(raw_keys, SecretStr):
                    data["gemini_api_keys"] = [raw_keys]
                elif isinstance(raw_keys, list):
                    data["gemini_api_keys"] = [
                        item if isinstance(item, SecretStr) else SecretStr(item.strip())
                        for item in raw_keys
                        if (isinstance(item, SecretStr) or (isinstance(item, str) and item.strip()))
                    ]
        return data

    gemini_model: str = Field(
        default=DEFAULT_GEMINI_MODEL,
        description=(
            "Default Gemini model variant for pipeline stages. "
            f"Free-tier catalog (GEMINI_FREE_TIER_MODELS): {', '.join(GEMINI_FREE_TIER_MODELS)}."
        ),
    )
    gemini_fallback_model: str = Field(
        default=DEFAULT_GEMINI_FALLBACK_MODEL,
        description=(
            "Fallback Gemini model variant if primary hits demand spikes or errors "
            "(distinct from gemini_model; see GEMINI_FREE_TIER_MODELS)."
        ),
    )
    gemini_thinking_level: GeminiThinkingLevel = Field(
        default=DEFAULT_GEMINI_THINKING_LEVEL,
        validation_alias=AliasChoices(
            "CRESMO_GEMINI_THINKING_LEVEL",
            "GEMINI_THINKING_LEVEL",
            "gemini_thinking_level",
        ),
        description=(
            "Reasoning effort level for Gemini generation ('minimal', 'low', 'medium', 'high', 'xhigh'; "
            "automatically clamped per target model)."
        ),
    )
    gemini_max_output_tokens: int = Field(
        default=DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
        ge=256,
        le=1_048_576,
        validation_alias=AliasChoices(
            "CRESMO_GEMINI_MAX_OUTPUT_TOKENS",
            "GEMINI_MAX_OUTPUT_TOKENS",
            "gemini_max_output_tokens",
        ),
        description=(
            "Maximum output token ceiling (thinking + response tokens) for Gemini requests "
            "(default: 32768, safe across Gemma 4 32K and Gemini 3.5+/4 64K sync caps)."
        ),
    )
    gemini_timeout_seconds: float = Field(
        default=DEFAULT_GEMINI_TIMEOUT_SECONDS,
        ge=1.0,
        validation_alias=AliasChoices(
            "gemini_timeout_seconds",
            "CRESMO_GEMINI_TIMEOUT_SECONDS",
            "GEMINI_TIMEOUT_SECONDS",
            "CRESMO_GEMINI_TIMEOUT",
            "GEMINI_TIMEOUT",
        ),
        description="HTTP/TCP socket timeout in seconds for Google Gemini API inference requests.",
    )

    @field_validator("gemini_thinking_level", mode="before")
    @classmethod
    def _normalize_gemini_thinking_level(cls, value: Any) -> Any:
        """Normalize thinking level string by stripping whitespace and lowercasing."""
        return _normalize_str_choice(value)

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        validation_alias=AliasChoices("ollama_base_url", "CRESMO_OLLAMA_URL", "OLLAMA_URL"),
        description="Local Ollama endpoint URL for raw transcript conceptual indexing.",
    )
    ollama_model: str = Field(
        default="qwen2.5:7b",
        validation_alias=AliasChoices("ollama_model", "CRESMO_OLLAMA_MODEL", "OLLAMA_MODEL"),
        description="Local Ollama model variant for raw transcript conceptual indexing.",
    )
    indexing_provider: str = Field(
        default="ollama",
        validation_alias=AliasChoices("indexing_provider", "CRESMO_INDEXING_PROVIDER"),
        description="Provider for raw transcript conceptual indexing: 'ollama' (default local) or 'gemini' (cloud API).",
    )
    ollama_timeout_seconds: float = Field(
        default=300.0,
        ge=1.0,
        validation_alias=AliasChoices(
            "ollama_timeout_seconds",
            "CRESMO_OLLAMA_TIMEOUT",
            "OLLAMA_TIMEOUT",
        ),
        description="HTTP timeout in seconds for local Ollama inference requests (CPU-only may need 300s+).",
    )
    ollama_warmup_timeout_seconds: float = Field(
        default=300.0,
        ge=1.0,
        validation_alias=AliasChoices(
            "ollama_warmup_timeout_seconds",
            "CRESMO_OLLAMA_WARMUP_TIMEOUT",
            "OLLAMA_WARMUP_TIMEOUT",
        ),
        description="Extended HTTP timeout in seconds for initial Ollama model preload into VRAM.",
    )
    ollama_keep_alive: str = Field(
        default="1h",
        validation_alias=AliasChoices(
            "ollama_keep_alive",
            "CRESMO_OLLAMA_KEEPALIVE",
            "OLLAMA_KEEPALIVE",
            "CRESMO_OLLAMA_KEEP_ALIVE",
        ),
        description="Duration to keep the model loaded in Ollama VRAM/RAM (e.g. '1h', '60m', '-1' for indefinite).",
    )
    ollama_num_predict: int = Field(
        default=0,
        ge=0,
        validation_alias=AliasChoices(
            "ollama_num_predict", "CRESMO_OLLAMA_NUM_PREDICT", "OLLAMA_NUM_PREDICT"
        ),
        description="Maximum tokens predicted by local Ollama model (0 means unconstrained / model default).",
    )
    language: str = Field(
        default=DEFAULT_LANGUAGE,
        validation_alias=AliasChoices("language", "CRESMO_LANGUAGE"),
        description="Target generation language for synthesis, compendiums, and conceptual indexing.",
    )
    llm_synthesis_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        validation_alias=AliasChoices(
            "llm_synthesis_temperature",
            "CRESMO_LLM_SYNTHESIS_TEMPERATURE",
        ),
        description="Sampling temperature for local Ollama generative synthesis (ignored on Gemini 3.5+/4).",
    )
    llm_indexing_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        validation_alias=AliasChoices(
            "llm_indexing_temperature",
            "CRESMO_LLM_INDEXING_TEMPERATURE",
        ),
        description="Sampling temperature for local Ollama conceptual indexing (ignored on Gemini 3.5+/4).",
    )


__all__ = ["LlmSettings"]
