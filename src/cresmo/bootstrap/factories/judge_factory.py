"""Factory for LLM Judge and Decision-Model Evaluator Adapters.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
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
    """Build a decorated LlmJudgePort instance based on application settings.

    Args:
        settings: Validated Cresmo application settings.
        telemetry_port: Optional Hexagonal TelemetryPort for criterion score ingestion.
        prompt_provider: Optional prompt provider port for externalized judge instructions.
        enable_fallback: Whether to wrap primary with fallback composite adapter (default: True).
            Set to False during calibration to maintain strict metrological benchmark isolation.
        credential_pool: Optional shared GeminiCredentialPool for cross-adapter cooldown sync.

    Returns:
        LlmJudgePort: Resilient multi-provider judge wrapped in telemetry decorator.
    """
    # 1. Instantiate Primary Provider
    primary: LlmJudgePort
    provider = settings.judge_provider.lower().strip()
    if provider == "gemini":
        from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter

        primary = GeminiJudgeAdapter(
            api_keys=[k.get_secret_value() for k in settings.gemini_api_keys],
            model=settings.judge_gemini_model,
            pass_threshold=settings.judge_pass_threshold,
            thinking_level=settings.judge_gemini_thinking_level,
            max_output_tokens=settings.gemini_max_output_tokens,
            prompt_provider=prompt_provider,
            credential_pool=credential_pool,
            timeout_seconds=settings.gemini_timeout_seconds,
        )
    elif provider == "ollama":
        from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter

        primary = OllamaJudgeAdapter(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
            pass_threshold=settings.judge_pass_threshold,
            prompt_provider=prompt_provider,
        )
    else:
        from cresmo.infrastructure.adapters.judges.typesafe_judge import TypeSafeJudgeAdapter

        primary = TypeSafeJudgeAdapter(
            api_key=settings.typesafe_api_key.get_secret_value(),
            model=settings.typesafe_model,
            base_url=settings.typesafe_base_url,
            pass_threshold=settings.judge_pass_threshold,
        )

    # 2. Instantiate Fallback Provider if enabled
    inner_judge: LlmJudgePort
    if enable_fallback:
        from cresmo.infrastructure.adapters.judges.composite_judge import (
            ResilientCompositeJudgeAdapter,
        )
        from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter

        fallback: LlmJudgePort = OllamaJudgeAdapter(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
            pass_threshold=settings.judge_pass_threshold,
            prompt_provider=prompt_provider,
        )
        inner_judge = ResilientCompositeJudgeAdapter(primary=primary, fallback=fallback)
    else:
        # Metrological isolation for calibration: no fallback failover
        inner_judge = primary

    # 3. Wrap in Mechanical Preflight Gate
    from cresmo.infrastructure.adapters.judges.preflight_decorator import (
        MechanicalPreflightJudgeDecorator,
    )
    from cresmo.infrastructure.adapters.judges.telemetry_decorator import TelemetryJudgeDecorator

    inner_judge = MechanicalPreflightJudgeDecorator(inner_judge=inner_judge)

    # 4. Decorate with Hexagonal Telemetry Emission
    return TelemetryJudgeDecorator(
        inner_judge=inner_judge,
        telemetry_port=telemetry_port,
    )
