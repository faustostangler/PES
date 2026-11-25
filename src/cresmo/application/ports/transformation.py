"""Hexagonal LLM Transformation Port.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity (Ports & Adapters)
- EVAL-001: Evaluation and LLM Orchestration
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from cresmo.domain.value_objects import ChatPrompt


class LLMTransformationPort(ABC):
    """Hexagonal Port defining contracts for generative synthesis and structured extraction.

    Conforms to ADR-001, ADR-036, and EVAL-001. Shields use cases from provider-specific SDKs
    (Google GenAI, Ollama, local models).
    """

    @abstractmethod
    def transform(
        self,
        prompt: ChatPrompt,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation given canonical multi-turn or single-turn ChatPrompt.

        Args:
            prompt: Canonical ChatPrompt value object with system prompt and messages.
            temperature: Sampling temperature override (used by local providers; ignored by Gemini).
            trace_id: Optional trace ID (e.g. ContentId or session key).
            session_id: Pipeline session identifier.
            user_id: Operator or channel identifier.

        Returns:
            Generated response text string.

        Raises:
            LLMInfrastructureError: If provider API or socket fails.
            RateLimitExceededError: If rate quotas are exhausted.
        """
        raise NotImplementedError("Implement LLM transformation contract.")

    def warmup(self) -> None:
        """Asynchronously preload model weights in background if supported by provider.

        Default implementation is a no-op for providers not requiring local weight loading
        (e.g. cloud APIs or test doubles).
        """
        return None
