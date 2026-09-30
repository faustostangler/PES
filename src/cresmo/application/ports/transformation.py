"""Hexagonal LLM Transformation Port.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity (Ports & Adapters)
- EVAL-001: Evaluation and LLM Orchestration
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMTransformationPort(ABC):
    """Hexagonal Port defining contracts for generative synthesis and structured extraction.

    Conforms to ADR-001 and EVAL-001. Shields use cases from provider-specific SDKs
    (Google GenAI, Ollama, local models).
    """

    @abstractmethod
    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation given input prompt and optional system directive.

        Args:
            prompt: Formatted user prompt or synthesis task.
            system_instruction: Optional system instruction guiding model persona.
            temperature: Sampling temperature override.
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

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Asynchronously preload model weights in background if supported by provider.

        Default implementation is a no-op for providers not requiring local weight loading
        (e.g. cloud APIs or test doubles).

        Args:
            timeout_seconds: Optional timeout in seconds for background model loading.
        """

    def wait_for_warmup(self, timeout_seconds: float | None = None) -> bool:
        """Wait at the rendezvous barrier until model warmup completes.

        Default implementation returns True immediately for providers not requiring
        explicit local memory allocation.

        Args:
            timeout_seconds: Optional timeout in seconds to wait for warmup.

        Returns:
            True if warmup completed successfully; False if timed out.
        """
        _ = timeout_seconds
        return True
