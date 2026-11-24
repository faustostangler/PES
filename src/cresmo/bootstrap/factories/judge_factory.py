"""Factory for LLM Judge and Decision-Model Evaluator Adapters.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cresmo.application.ports import PromptProviderPort, TelemetryPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.infrastructure.config import CresmoSettings

if TYPE_CHECKING:
    from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool


def build_llm_judge_adapter(
    settings: CresmoSettings,
    telemetry_port: TelemetryPort | None = None,
    prompt_provider: PromptProviderPort | None = None,
    enable_fallback: bool = True,
    credential_pool: GeminiCredentialPool | None = None,
) -> LlmJudgePort:
    """Build a decorated LlmJudgePort instance based on hierarchical CresmoSettings."""
    judge_cfg = settings.judge
    gemini_cfg = settings.llm.gemini
    ollama_cfg = settings.llm.ollama

    primary: LlmJudgePort
    provider = judge_cfg.provider
    if provider == "gemini":
        from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter

        primary = GeminiJudgeAdapter(
            api_keys=[k.get_secret_value() for k in gemini_cfg.api_keys],
            model=judge_cfg.gemini.model,
            fallback_model=gemini_cfg.fallback_model if enable_fallback else None,
            pass_threshold=judge_cfg.pass_threshold,
            thinking_level=judge_cfg.gemini.thinking_level,
            max_output_tokens=gemini_cfg.max_output_tokens,
            prompt_provider=prompt_provider,
            credential_pool=credential_pool,
            timeout_seconds=gemini_cfg.timeout_seconds,
        )
    elif provider == "ollama":
        from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter

        primary = OllamaJudgeAdapter(
            base_url=ollama_cfg.base_url,
            model=ollama_cfg.model,
            timeout_seconds=ollama_cfg.timeout_seconds,
            pass_threshold=judge_cfg.pass_threshold,
            prompt_provider=prompt_provider,
        )
    else:
        from cresmo.infrastructure.adapters.judges.typesafe_judge import TypeSafeJudgeAdapter

        ts_cfg = judge_cfg.typesafe
        primary = TypeSafeJudgeAdapter(
            api_key=ts_cfg.api_key.get_secret_value(),
            model=ts_cfg.model,
            base_url=ts_cfg.base_url,
            pass_threshold=judge_cfg.pass_threshold,
        )

    inner_judge: LlmJudgePort
    if enable_fallback and provider != "ollama":
        from cresmo.infrastructure.adapters.judges.composite_judge import (
            ResilientCompositeJudgeAdapter,
        )
        from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter

        fallback: LlmJudgePort = OllamaJudgeAdapter(
            base_url=ollama_cfg.base_url,
            model=ollama_cfg.model,
            timeout_seconds=ollama_cfg.timeout_seconds,
            pass_threshold=judge_cfg.pass_threshold,
            prompt_provider=prompt_provider,
        )
        inner_judge = ResilientCompositeJudgeAdapter(primary=primary, fallback=fallback)
    else:
        inner_judge = primary

    from cresmo.infrastructure.adapters.judges.preflight_decorator import (
        MechanicalPreflightJudgeDecorator,
    )
    from cresmo.infrastructure.adapters.judges.telemetry_decorator import TelemetryJudgeDecorator

    inner_judge = MechanicalPreflightJudgeDecorator(inner_judge=inner_judge)
    return TelemetryJudgeDecorator(
        inner_judge=inner_judge,
        telemetry_port=telemetry_port,
    )
