"""Thread naming utilities for background telemetry workers.

Conforms to:
- ADR-020 Pillar 5: Thread Hierarchy & APM Visibility
"""

from __future__ import annotations

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)


def _name_langfuse_threads(langfuse_client: Any) -> None:
    """Assign canonical names to Langfuse background consumers."""
    resources = getattr(langfuse_client, "_resources", None)
    if not resources:
        return

    for idx, consumer in enumerate(getattr(resources, "_media_upload_consumers", [])):
        consumer.name = f"LangfuseMediaUploadConsumer-{idx}"
    for idx, consumer in enumerate(getattr(resources, "_ingestion_consumers", [])):
        consumer.name = f"LangfuseScoreIngestionConsumer-{idx}"

    pc = getattr(resources, "prompt_cache", None)
    if pc:
        ptm = getattr(pc, "_task_manager", None)
        if ptm:
            for idx, consumer in enumerate(getattr(ptm, "_consumers", [])):
                consumer.name = f"LangfusePromptCacheConsumer-{idx}"


def _name_otel_threads() -> None:
    """Assign canonical name to OpenTelemetry batch span processor thread."""
    for t in threading.enumerate():
        if t.name == "OtelBatchSpanRecordProcessor":
            t.name = "CresmoOtelBatchSpanProcessor"


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
