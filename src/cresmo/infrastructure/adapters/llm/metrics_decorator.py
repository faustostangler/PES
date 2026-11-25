"""Hexagonal Metrics Decorator for LLMTransformationPort latency instrumentation."""

from __future__ import annotations

import time

from cresmo.application.ports import (
    LLMTransformationPort,
    MetricName,
    MetricsPort,
    NoOpMetricsPort,
)
from cresmo.domain.value_objects import ChatPrompt


class MetricsLLMTransformationDecorator(LLMTransformationPort):
    """Decorator observing ``MetricName.LLM_REQUEST_DURATION`` around LLM calls."""

    def __init__(
        self,
        inner: LLMTransformationPort,
        metrics_port: MetricsPort | None = None,
        provider: str = "llm",
    ) -> None:
        self._inner = inner
        self._metrics_port: MetricsPort = metrics_port or NoOpMetricsPort()
        self._provider = provider

    def warmup(self) -> None:
        """Delegate model preload to the wrapped LLM adapter."""
        self._inner.warmup()

    def transform(
        self,
        prompt: ChatPrompt,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Delegate transformation while recording request duration histogram."""
        start_time = time.perf_counter()
        status = "success"
        try:
            return self._inner.transform(
                prompt=prompt,
                temperature=temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
        except Exception:
            status = "error"
            raise
        finally:
            self._metrics_port.observe_histogram(
                MetricName.LLM_REQUEST_DURATION,
                time.perf_counter() - start_time,
                labels={"provider": self._provider, "status": status},
            )


__all__ = ["MetricsLLMTransformationDecorator"]
