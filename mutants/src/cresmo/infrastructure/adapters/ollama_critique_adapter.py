"""Ollama-powered Directed Critique Synthesizer Adapter (ADR-031)."""

from __future__ import annotations

import logging

from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    LLMTransformationPort,
    PromptProviderPort,
)
from cresmo.domain.value_objects import ChatPrompt, PromptKey
from cresmo.domain.value_objects.quality import JudgeEvaluation
from cresmo.infrastructure.adapters.prompts import JsonPromptProvider

logger = logging.getLogger(__name__)


class OllamaCritiqueAdapter(CritiqueSynthesizerPort):
    """Adapter transforming structured evaluation verdicts into natural language reflection critiques via Ollama."""

    def __init__(
        self,
        llm_transformation_port: LLMTransformationPort | None = None,
        system_instruction: str | None = None,
        temperature: float = 0.1,
        *,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_transformation_port = llm_transformation_port
        self.system_instruction = system_instruction
        self.temperature = temperature
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def synthesize(
        self,
        evaluation: JudgeEvaluation,
        stage_name: str,
        *,
        trace_id: str | None = None,
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

        effective_prompt = (
            ChatPrompt(
                messages=chat_prompt.messages,
                system_instruction=self.system_instruction,
            )
            if self.system_instruction is not None
            else chat_prompt
        )

        try:
            synthesized = self.llm_transformation_port.transform(
                prompt=effective_prompt,
                temperature=self.temperature,
                trace_id=trace_id,
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
