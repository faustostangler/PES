"""Factory for Quality Judge and Decision-Model Evaluator Adapters.

Conforms to:
    - ADR-029: Unified QualityJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: Quality Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import logging
from typing import Any

from cresmo.application.ports.quality_judge_port import QualityJudgePort
from cresmo.infrastructure.adapters.judges.composite_judge import ResilientCompositeJudgeAdapter
from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter
from cresmo.infrastructure.adapters.judges.langfuse_decorator import LangfuseJudgeDecorator
from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter
from cresmo.infrastructure.adapters.judges.typesafe_judge import TypeSafeJudgeAdapter
from cresmo.infrastructure.config import CresmoSettings

logger = logging.getLogger(__name__)


def build_quality_judge_adapter(
    settings: CresmoSettings,
    langfuse_client: Any | None = None,
) -> QualityJudgePort:
    """Build a resilient, decorated QualityJudgePort instance based on application settings.

    Args:
        settings: Validated Cresmo application settings.
        langfuse_client: Optional Langfuse client for direct score telemetry ingestion.

    Returns:
        QualityJudgePort: Resilient multi-provider judge wrapped in telemetry decorator.
    """
    # 1. Instantiate Primary Provider
    provider = settings.judge_provider.lower().strip()
    if provider == "gemini":
        primary: QualityJudgePort = GeminiJudgeAdapter(
            api_key=settings.gemini_api_key.get_secret_value(),
            model=settings.gemini_model,
        )
    elif provider == "typesafe":
        primary = TypeSafeJudgeAdapter(
            api_key=settings.typesafe_api_key.get_secret_value(),
            model=settings.typesafe_model,
            base_url=settings.typesafe_base_url,
        )
    elif provider == "ollama":
        primary = OllamaJudgeAdapter(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    else:
        logger.warning(
            "Unknown judge provider '%s'. Defaulting to Gemini.",
            provider,
        )
        primary = GeminiJudgeAdapter(
            api_key=settings.gemini_api_key.get_secret_value(),
            model=settings.gemini_model,
        )

    # 2. Instantiate Fallback Provider (Default is local Ollama)
    fallback: QualityJudgePort = OllamaJudgeAdapter(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )

    # 3. Wrap in Resilient Composite
    resilient_judge = ResilientCompositeJudgeAdapter(primary=primary, fallback=fallback)

    # 4. Decorate with Langfuse Telemetry Emission
    return LangfuseJudgeDecorator(
        inner_judge=resilient_judge,
        langfuse_client=langfuse_client,
    )
