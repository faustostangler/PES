"""Thread naming utilities for background telemetry workers.

Conforms to:
- ADR-020 Pillar 5: Thread Hierarchy & APM Visibility
"""

from __future__ import annotations

import threading
from typing import Any, Final

import structlog

logger = structlog.get_logger(__name__)

_LANGFUSE_MEDIA_THREAD_PREFIX: Final[str] = "LangfuseMediaUploadConsumer-"
_LANGFUSE_SCORE_THREAD_PREFIX: Final[str] = "LangfuseScoreIngestionConsumer-"
_LANGFUSE_CACHE_THREAD_PREFIX: Final[str] = "LangfusePromptCacheConsumer-"
_OTEL_DEFAULT_THREAD_NAME: Final[str] = "OtelBatchSpanRecordProcessor"
_CRESMO_OTEL_THREAD_NAME: Final[str] = "CresmoOtelBatchSpanProcessor"


def _name_langfuse_threads(langfuse_client: Any) -> None:
    """Assign canonical names to Langfuse background consumers."""
    resources = getattr(langfuse_client, "_resources", None)
    if not resources:
        return

    for idx, consumer in enumerate(getattr(resources, "_media_upload_consumers", [])):
        consumer.name = f"{_LANGFUSE_MEDIA_THREAD_PREFIX}{idx}"
    for idx, consumer in enumerate(getattr(resources, "_ingestion_consumers", [])):
        consumer.name = f"{_LANGFUSE_SCORE_THREAD_PREFIX}{idx}"

    prompt_cache = getattr(resources, "prompt_cache", None)
    if prompt_cache:
        prompt_task_manager = getattr(prompt_cache, "_task_manager", None)
        if prompt_task_manager:
            for idx, consumer in enumerate(getattr(prompt_task_manager, "_consumers", [])):
                consumer.name = f"{_LANGFUSE_CACHE_THREAD_PREFIX}{idx}"


def _name_otel_threads() -> None:
    """Assign canonical name to OpenTelemetry batch span processor thread."""
    for thread in threading.enumerate():
        if thread.name == _OTEL_DEFAULT_THREAD_NAME:
            thread.name = _CRESMO_OTEL_THREAD_NAME


def name_telemetry_threads(langfuse_client: Any | None = None) -> None:
    """Assign canonical SOTA-KISS thread names to background telemetry workers.

    Prevents anonymous threads ('Thread-1', 'Thread-2', etc.) in Linux thread dumps
    and APMs per ADR-020 Pillar 5 (Thread Hierarchy & APM Visibility).
    """
    if langfuse_client is not None:
        try:
            _name_langfuse_threads(langfuse_client)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Failed to assign canonical names to Langfuse threads: %s", exc)

    try:
        _name_otel_threads()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to assign canonical name to OpenTelemetry thread: %s", exc)
