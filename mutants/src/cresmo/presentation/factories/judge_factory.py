"""Factory for LLM Judge and Decision-Model Evaluator Adapters.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import logging
from typing import Any

from cresmo.application.ports import PromptProviderPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.infrastructure.adapters.judges.composite_judge import ResilientCompositeJudgeAdapter
from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter
from cresmo.infrastructure.adapters.judges.langfuse_decorator import LangfuseJudgeDecorator
from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter
from cresmo.infrastructure.adapters.judges.preflight_decorator import (
    MechanicalPreflightJudgeDecorator,
)
from cresmo.infrastructure.adapters.judges.typesafe_judge import TypeSafeJudgeAdapter
from cresmo.infrastructure.config import CresmoSettings

logger = logging.getLogger(__name__)


def build_llm_judge_adapter(
    settings: CresmoSettings,
    langfuse_client: Any | None = None,
    prompt_provider: PromptProviderPort | None = None,
) -> LlmJudgePort:
    """Build a resilient, decorated LlmJudgePort instance based on application settings.

    Args:
        settings: Validated Cresmo application settings.
        langfuse_client: Optional Langfuse client for direct score telemetry ingestion.
        prompt_provider: Optional prompt provider port for externalized judge instructions.

    Returns:
        LlmJudgePort: Resilient multi-provider judge wrapped in telemetry decorator.
    """
    # 1. Instantiate Primary Provider
    primary: LlmJudgePort
    provider = settings.judge_provider.lower().strip()
    if provider == "gemini":
        primary = GeminiJudgeAdapter(
            api_key=settings.gemini_api_key.get_secret_value(),
            model=settings.judge_gemini_model,
            pass_threshold=settings.judge_pass_threshold,
            temperature=settings.judge_temperature,
            prompt_provider=prompt_provider,
        )
    elif provider == "ollama":
        primary = OllamaJudgeAdapter(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
            pass_threshold=settings.judge_pass_threshold,
            prompt_provider=prompt_provider,
        )
    else:
        primary = TypeSafeJudgeAdapter(
            api_key=settings.typesafe_api_key.get_secret_value(),
            model=settings.typesafe_model,
            base_url=settings.typesafe_base_url,
            pass_threshold=settings.judge_pass_threshold,
        )

    # 2. Instantiate Fallback Provider (Default is local Ollama)
    fallback: LlmJudgePort = OllamaJudgeAdapter(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
        pass_threshold=settings.judge_pass_threshold,
        prompt_provider=prompt_provider,
    )

    # 3. Wrap in Resilient Composite
    resilient_judge = ResilientCompositeJudgeAdapter(primary=primary, fallback=fallback)

    # 4. Wrap in Mechanical Preflight Gate
    preflight_judge = MechanicalPreflightJudgeDecorator(inner_judge=resilient_judge)

    # 5. Decorate with Langfuse Telemetry Emission
    return LangfuseJudgeDecorator(
        inner_judge=preflight_judge,
        langfuse_client=langfuse_client,
    )
