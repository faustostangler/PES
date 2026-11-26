"""Hexagonal Metrics Decorator for LLMTransformationPort latency instrumentation."""

from __future__ import annotations

import time
from typing import Final

from cresmo.application.ports import (
    LLMTransformationPort,
    MetricName,
    MetricsPort,
    NoOpMetricsPort,
)
from cresmo.domain.value_objects import ChatPrompt

DEFAULT_LLM_PROVIDER_LABEL: Final[str] = "llm"
_STATUS_SUCCESS: Final[str] = "success"
_STATUS_ERROR: Final[str] = "error"
_LABEL_PROVIDER: Final[str] = "provider"
_LABEL_STATUS: Final[str] = "status"


class MetricsLLMTransformationDecorator(LLMTransformationPort):
    """Decorator observing ``MetricName.LLM_REQUEST_DURATION`` around LLM calls."""

    def __init__(
        self,
        inner: LLMTransformationPort,
        metrics_port: MetricsPort | None = None,
        provider: str = DEFAULT_LLM_PROVIDER_LABEL,
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
        status = _STATUS_SUCCESS
        try:
            return self._inner.transform(
                prompt=prompt,
                temperature=temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
        except Exception:
            status = _STATUS_ERROR
            raise
        finally:
            self._metrics_port.observe_histogram(
                MetricName.LLM_REQUEST_DURATION,
                time.perf_counter() - start_time,
                labels={_LABEL_PROVIDER: self._provider, _LABEL_STATUS: status},
            )


__all__ = ["MetricsLLMTransformationDecorator"]
