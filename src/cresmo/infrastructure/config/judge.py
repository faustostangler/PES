"""Quality judge, TypeSafe evaluator, and benchmark harness settings for Cresmo.

Conforms to:
    - ADR-029: Quality Judge & Decision-Model Evaluator Architecture
    - ADR-064: Gemini Free-Tier Catalog & Thinking Level Governance
    - ADR-069: Modular Domain Settings Package
"""

from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from cresmo.infrastructure.config.catalog import (
    DEFAULT_BENCHMARK_MODELS,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_JUDGE_PASS_THRESHOLD,
    GeminiThinkingLevel,
    _customize_comma_list_sources,
    _normalize_str_choice,
)


class JudgeSettings(BaseSettings):
    """Quality judge, TypeSafe AI evaluator, and benchmark settings."""

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
        """Customise settings sources to safely parse comma-separated model lists from env."""
        return _customize_comma_list_sources(
            (
                "benchmark_models",
                "judge_calibration_models",
                "generator_benchmark_models",
            ),
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    typesafe_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("typesafe_api_key", "TYPESAFE_API_KEY"),
        description="TypeSafe AI API Key for System One Jev decision evaluations.",
    )
    typesafe_model: str = Field(
        default="jev-latest",
        validation_alias=AliasChoices("typesafe_model", "TYPESAFE_MODEL"),
        description="Model identifier for TypeSafe AI System One decision evaluations.",
    )
    typesafe_base_url: str = Field(
        default="https://api.typesafe.ai/v1",
        validation_alias=AliasChoices("typesafe_base_url", "TYPESAFE_BASE_URL"),
        description="Base URL endpoint for TypeSafe AI API.",
    )
    judge_provider: str = Field(
        default="gemini",  # default original typesafe
        validation_alias=AliasChoices("judge_provider", "CRESMO_JUDGE_PROVIDER"),
        description="Primary quality judge provider ('gemini', 'typesafe', 'ollama').",
    )
    judge_fallback_provider: str = Field(
        default="ollama",
        validation_alias=AliasChoices("judge_fallback_provider", "CRESMO_JUDGE_FALLBACK_PROVIDER"),
        description="Fallback quality judge provider when primary fails.",
    )
    judge_blocking: bool = Field(
        default=False,
        validation_alias=AliasChoices("judge_blocking", "CRESMO_JUDGE_BLOCKING"),
        description="Whether failed quality evaluations raise DomainValidationError or log warning scores.",
    )
    judge_max_attempts: int = Field(
        default=2,
        ge=1,
        validation_alias=AliasChoices(
            "judge_max_attempts",
            "CRESMO_JUDGE_MAX_ATTEMPTS",
            "max_retries",
            "CRESMO_MAX_RETRIES",
        ),
        description="Maximum execution attempts (default: 2) across all pipeline stages when quality evaluation fails.",
    )

    @property
    def max_retries(self) -> int:
        """Backward-compatible property alias for judge_max_attempts."""
        return self.judge_max_attempts

    judge_pass_threshold: float = Field(
        default=DEFAULT_JUDGE_PASS_THRESHOLD,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "judge_pass_threshold",
            "CRESMO_JUDGE_PASS_THRESHOLD",
            "JUDGE_PASS_THRESHOLD",
        ),
        description="Minimum score threshold required for quality judge evaluations to pass.",
    )
    gap_filler_judge_threshold: float = Field(
        default=DEFAULT_JUDGE_PASS_THRESHOLD,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "gap_filler_judge_threshold",
            "CRESMO_GAP_FILLER_JUDGE_THRESHOLD",
            "GAP_FILLER_JUDGE_THRESHOLD",
        ),
        description="Minimum score threshold required for gap_filler judge evaluations to pass.",
    )
    gap_filler_judge_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "epistemic_grounding_segregation": 0.20,
            "conceptual_mechanical_decomposition": 0.15,
            "braudelian_stratification": 0.15,
            "genealogy_hidden_agency": 0.15,
            "competing_hypotheses": 0.15,
            "extra_info_granularity": 0.10,
            "linear_style_naturalism": 0.10,
        },
        validation_alias=AliasChoices(
            "gap_filler_judge_weights",
            "CRESMO_GAP_FILLER_JUDGE_WEIGHTS",
            "GAP_FILLER_JUDGE_WEIGHTS",
        ),
        description="Criterion weights for gap_filler stage judge evaluation.",
    )
    judge_gemini_model: str = Field(
        default=DEFAULT_GEMINI_MODEL,
        validation_alias=AliasChoices(
            "judge_gemini_model",
            "CRESMO_JUDGE_GEMINI_MODEL",
            "JUDGE_GEMINI_MODEL",
        ),
        description=(
            "Gemini model variant for quality judge evaluations "
            "(defaults to fast Free-Tier gemini-3.5-flash-lite)."
        ),
    )
    judge_gemini_thinking_level: GeminiThinkingLevel = Field(
        default=DEFAULT_GEMINI_THINKING_LEVEL,
        validation_alias=AliasChoices(
            "CRESMO_JUDGE_GEMINI_THINKING_LEVEL",
            "JUDGE_GEMINI_THINKING_LEVEL",
            "judge_gemini_thinking_level",
        ),
        description=(
            "Reasoning effort level for Gemini quality judge evaluations "
            "('minimal', 'low', 'medium', 'high', 'xhigh'; default: 'low')."
        ),
    )

    @field_validator("judge_gemini_thinking_level", mode="before")
    @classmethod
    def _normalize_judge_thinking_level(cls, value: Any) -> Any:
        """Normalize thinking level string by stripping whitespace and lowercasing."""
        return _normalize_str_choice(value)

    benchmark_models: list[str] = Field(
        default_factory=lambda: list(DEFAULT_BENCHMARK_MODELS),
        validation_alias=AliasChoices(
            "benchmark_models",
            "CRESMO_BENCHMARK_MODELS",
            "BENCHMARK_MODELS",
            "judge_calibration_models",
            "generator_benchmark_models",
            "CRESMO_JUDGE_CALIBRATION_MODELS",
            "JUDGE_CALIBRATION_MODELS",
            "CRESMO_GENERATOR_BENCHMARK_MODELS",
            "GENERATOR_BENCHMARK_MODELS",
        ),
        description="Canonical model specifications sequentially evaluated in judge calibration and generator benchmark harnesses.",
    )

    @property
    def judge_calibration_models(self) -> list[str]:
        """Backward-compatible alias for benchmark_models."""
        return self.benchmark_models

    @property
    def generator_benchmark_models(self) -> list[str]:
        """Backward-compatible alias for benchmark_models."""
        return self.benchmark_models


__all__ = ["JudgeSettings"]
