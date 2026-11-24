"""Quality judge, TypeSafe evaluator, and benchmark harness settings for Cresmo.

Conforms to:
    - ADR-029: Quality Judge & Decision-Model Evaluator Architecture
    - ADR-060: Gap Filler Judge Criteria v2
    - ADR-064: Gemini Free-Tier Catalog & Thinking Level Governance
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from pydantic_settings import NoDecode

from cresmo.infrastructure.config.catalog import (
    DEFAULT_BENCHMARK_MODELS,
    DEFAULT_GEMINI_THINKING_LEVEL,
    DEFAULT_JUDGE_GEMINI_MODEL,
    DEFAULT_JUDGE_PASS_THRESHOLD,
    GeminiThinkingLevel,
    normalize_str_choice,
    parse_comma_separated_strings,
)

JudgeProviderName = Literal["gemini", "typesafe", "ollama"]


def _default_gap_filler_weights() -> dict[str, float]:
    return {
        "epistemic_grounding_segregation": 0.20,
        "conceptual_mechanical_decomposition": 0.15,
        "braudelian_stratification": 0.15,
        "genealogy_hidden_agency": 0.15,
        "competing_hypotheses": 0.15,
        "extra_info_granularity": 0.10,
        "linear_style_naturalism": 0.10,
    }


class TypeSafeSettings(BaseModel):
    """Immutable TypeSafe AI System One Jev evaluator settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    api_key: SecretStr = Field(
        default=SecretStr(""),
        description="TypeSafe AI API Key for System One Jev decision evaluations.",
    )
    model: str = Field(
        default="jev-latest",
        description="Model identifier for TypeSafe AI System One decision evaluations.",
    )
    base_url: str = Field(
        default="https://api.typesafe.ai/v1",
        description="Base URL endpoint for TypeSafe AI API.",
    )


class JudgeGeminiSettings(BaseModel):
    """Immutable Gemini judge model and thinking configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model: str = Field(
        default=DEFAULT_JUDGE_GEMINI_MODEL,
        description="Gemini model variant for quality judge evaluations.",
    )
    thinking_level: GeminiThinkingLevel = Field(
        default=DEFAULT_GEMINI_THINKING_LEVEL,
        description="Reasoning effort level for Gemini quality judge evaluations.",
    )

    @field_validator("thinking_level", mode="before")
    @classmethod
    def _normalize_thinking_level(cls, value: Any) -> Any:
        return normalize_str_choice(value)


class GapFillerJudgeSettings(BaseModel):
    """Immutable gap_filler quality judge threshold and criterion weights."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    threshold: float = Field(
        default=DEFAULT_JUDGE_PASS_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Minimum score threshold required for gap_filler judge evaluations to pass.",
    )
    weights: dict[str, float] = Field(
        default_factory=_default_gap_filler_weights,
        description="Criterion weights for gap_filler stage judge evaluation.",
    )


class JudgeSettings(BaseModel):
    """Composed quality judge, evaluator provider, and benchmark settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: JudgeProviderName = Field(
        default="gemini",
        description="Primary quality judge provider ('gemini', 'typesafe', 'ollama').",
    )
    fallback_provider: JudgeProviderName = Field(
        default="ollama",
        description="Fallback quality judge provider when primary fails.",
    )
    blocking: bool = Field(
        default=False,
        description="Whether failed quality evaluations raise DomainValidationError or log warnings.",
    )
    max_attempts: int = Field(
        default=2,
        ge=1,
        description="Maximum execution attempts across pipeline stages when quality evaluation fails.",
    )
    pass_threshold: float = Field(
        default=DEFAULT_JUDGE_PASS_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Minimum score threshold required for quality judge evaluations to pass.",
    )
    benchmark_models: Annotated[tuple[str, ...], NoDecode] = Field(
        default=DEFAULT_BENCHMARK_MODELS,
        description="Canonical model specifications sequentially evaluated in calibration and benchmark harnesses.",
    )
    gemini: JudgeGeminiSettings = Field(default_factory=JudgeGeminiSettings)
    typesafe: TypeSafeSettings = Field(default_factory=TypeSafeSettings)
    gap_filler: GapFillerJudgeSettings = Field(default_factory=GapFillerJudgeSettings)

    @field_validator("provider", "fallback_provider", mode="before")
    @classmethod
    def _normalize_provider(cls, value: Any) -> Any:
        return normalize_str_choice(value)

    @field_validator("benchmark_models", mode="before")
    @classmethod
    def _parse_benchmark_models(cls, value: Any) -> Any:
        return parse_comma_separated_strings(value)


__all__ = [
    "GapFillerJudgeSettings",
    "JudgeGeminiSettings",
    "JudgeProviderName",
    "JudgeSettings",
    "TypeSafeSettings",
]
