"""Ollama-powered Directed Critique Synthesizer Adapter (ADR-031)."""

from __future__ import annotations

from typing import Final

import structlog

from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    LLMTransformationPort,
    PromptProviderPort,
)
from cresmo.domain.value_objects import PromptKey
from cresmo.domain.value_objects.quality import JudgeEvaluation
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider

logger = structlog.get_logger(__name__)

DEFAULT_OLLAMA_CRITIQUE_TEMPERATURE: Final[float] = 0.1


class OllamaCritiqueAdapter(CritiqueSynthesizerPort):
    """Adapter transforming structured evaluation verdicts into natural language reflection critiques via Ollama."""

    def __init__(
        self,
        llm_transformation_port: LLMTransformationPort | None = None,
        temperature: float = DEFAULT_OLLAMA_CRITIQUE_TEMPERATURE,
        *,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_transformation_port = llm_transformation_port
        self.temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def warmup(self) -> None:
        """Forward warmup to the wrapped LLM transformation adapter when configured."""
        if self.llm_transformation_port is not None:
            self.llm_transformation_port.warmup()

    def synthesize(
        self,
        evaluation: JudgeEvaluation,
        stage_name: str,
    ) -> str:
        """Convert structured JudgeEvaluation failures into directed natural language critique."""
        if evaluation.passed:
            return ""

        fallback_critique = evaluation.extract_critique()

        if self.llm_transformation_port is None:
            return fallback_critique

        chat_prompt = self._prompt_provider.get_prompt(
            PromptKey.OLLAMA_CRITIQUE,
            stage_name=stage_name,
            overall_score=f"{evaluation.overall_score:.2f}",
            criteria_failures=fallback_critique,
        )

        try:
            synthesized = self.llm_transformation_port.transform(
                prompt=chat_prompt,
                temperature=self.temperature,
            )
            clean = synthesized.strip()
            return clean if clean else fallback_critique
        except Exception as exc:  # noqa: BLE001 - Resilient fallback to evaluation.extract_critique()
            logger.warning(
                "Ollama critique synthesis failed for stage '%s': %s. Falling back to rule-based critique.",
                stage_name,
                exc,
            )
            return fallback_critique
