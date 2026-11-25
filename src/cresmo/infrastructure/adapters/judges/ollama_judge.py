"""Ollama Local LLM-as-a-Judge Adapter for Offline Fallback Quality Evaluation.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

from typing import Any

import httpx

from cresmo.application.ports import PromptProviderPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects import (
    ChatPrompt,
    EvaluationContext,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.judges.prompt_judge_runner import evaluate_prompt_judge
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.config import DEFAULT_JUDGE_PASS_THRESHOLD


class OllamaJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing local Ollama instance for offline fallback evaluation."""

    def __init__(
        self,
        http_client: Any | None = None,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b",
        timeout_seconds: float = 120.0,
        pass_threshold: float = DEFAULT_JUDGE_PASS_THRESHOLD,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        """Initialize Ollama judge adapter.

        Args:
            http_client: HTTP client instance (defaults to httpx.Client).
            base_url: Ollama API server base URL.
            model: Model variant running on Ollama.
            timeout_seconds: HTTP request timeout duration.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
            prompt_provider: Optional PromptProviderPort for externalized prompt templates.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._pass_threshold = pass_threshold
        self._client = http_client or httpx.Client(timeout=timeout_seconds)
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def _invoke_ollama(self, chat_prompt: ChatPrompt) -> str:
        payload = {
            "model": self._model,
            "messages": chat_prompt.to_dict_list(),
            "format": "json",
            "stream": False,
        }
        resp = self._client.post(f"{self._base_url}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        msg_obj = data.get("message")
        return str(msg_obj.get("content", "{}")) if isinstance(msg_obj, dict) else "{}"

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text using local Ollama model."""
        return evaluate_prompt_judge(
            context=context,
            prompt_provider=self._prompt_provider,
            pass_threshold=self._pass_threshold,
            provider_name="ollama",
            invoke_llm=self._invoke_ollama,
        )

    @property
    def pass_threshold(self) -> float:
        """Return the minimum score threshold required to pass."""
        return self._pass_threshold


__all__ = [
    "OllamaJudgeAdapter",
]
