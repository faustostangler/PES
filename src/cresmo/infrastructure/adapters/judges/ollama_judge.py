"""Ollama Local LLM-as-a-Judge Adapter for Offline Fallback Quality Evaluation.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

from typing import Any, Final

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

DEFAULT_OLLAMA_BASE_URL: Final[str] = "http://localhost:11434"
DEFAULT_OLLAMA_JUDGE_MODEL: Final[str] = "qwen2.5:7b"
DEFAULT_OLLAMA_JUDGE_TIMEOUT_SECONDS: Final[float] = 120.0
OLLAMA_PROVIDER_NAME: Final[str] = "ollama"
_URL_TRAILING_SLASH: Final[str] = "/"
_OLLAMA_CHAT_PATH: Final[str] = "/api/chat"
_OLLAMA_FORMAT_JSON: Final[str] = "json"
_KEY_MODEL: Final[str] = "model"
_KEY_MESSAGES: Final[str] = "messages"
_KEY_FORMAT: Final[str] = "format"
_KEY_STREAM: Final[str] = "stream"
_KEY_MESSAGE: Final[str] = "message"
_KEY_CONTENT: Final[str] = "content"
_EMPTY_JSON_OBJECT_STR: Final[str] = "{}"


class OllamaJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing local Ollama instance for offline fallback evaluation."""

    def __init__(
        self,
        http_client: Any | None = None,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        model: str = DEFAULT_OLLAMA_JUDGE_MODEL,
        timeout_seconds: float = DEFAULT_OLLAMA_JUDGE_TIMEOUT_SECONDS,
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
        self._base_url = base_url.rstrip(_URL_TRAILING_SLASH)
        self._model = model
        self._pass_threshold = pass_threshold
        self._client = http_client or httpx.Client(timeout=timeout_seconds)
        self._prompt_provider = prompt_provider or JsonPromptProvider()

    def _invoke_ollama(self, chat_prompt: ChatPrompt) -> str:
        payload = {
            _KEY_MODEL: self._model,
            _KEY_MESSAGES: chat_prompt.to_dict_list(),
            _KEY_FORMAT: _OLLAMA_FORMAT_JSON,
            _KEY_STREAM: False,
        }
        resp = self._client.post(f"{self._base_url}{_OLLAMA_CHAT_PATH}", json=payload)
        resp.raise_for_status()
        data = resp.json()
        msg_obj = data.get(_KEY_MESSAGE)
        return (
            str(msg_obj.get(_KEY_CONTENT, _EMPTY_JSON_OBJECT_STR))
            if isinstance(msg_obj, dict)
            else _EMPTY_JSON_OBJECT_STR
        )

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text using local Ollama model."""
        return evaluate_prompt_judge(
            context=context,
            prompt_provider=self._prompt_provider,
            pass_threshold=self._pass_threshold,
            provider_name=OLLAMA_PROVIDER_NAME,
            invoke_llm=self._invoke_ollama,
        )

    @property
    def pass_threshold(self) -> float:
        """Return the minimum score threshold required to pass."""
        return self._pass_threshold


__all__ = [
    "OllamaJudgeAdapter",
]
