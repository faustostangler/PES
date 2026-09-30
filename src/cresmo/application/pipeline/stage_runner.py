"""Telemetry-instrumented stage execution runner and session metrics recorder."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Sequence
from typing import Literal, TypeVar, overload

from cresmo.application.ports import MetricsPort, TelemetryPort
from cresmo.application.use_cases import DeduplicationReport
from cresmo.domain.entities import (
    AtomicNote,
    MapOfContent,
    PipelineSessionId,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    ChannelId,
    ChannelName,
    ContentId,
)

logger = logging.getLogger(__name__)

_StageRet = TypeVar("_StageRet")


class PipelineStageRunner:
    """Encapsulates execution of discrete pipeline stages with telemetry spans, metrics, and error handling."""

    def __init__(
        self,
        telemetry_port: TelemetryPort,
        metrics_port: MetricsPort,
    ) -> None:
        self.telemetry_port = telemetry_port
        self.metrics_port = metrics_port

    @overload
    def run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        channel_id: ChannelId | None = ...,
        fatal: Literal[True] = ...,
        fallback: _StageRet | None = ...,
    ) -> _StageRet: ...

    @overload
    def run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        channel_id: ChannelId | None = ...,
        fatal: Literal[False],
        fallback: _StageRet | None = ...,
    ) -> _StageRet | None: ...

    def run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        channel_id: ChannelId | None = None,
        fatal: bool = True,
        fallback: _StageRet | None = None,
    ) -> _StageRet | None:
        """Execute a pipeline stage wrapped with telemetry spans, metrics, and error handling.

        Args:
            stage_name: Identifier for the stage (e.g. 'fluid_prose', 'atomic_batch').
            fn: Callable executing the use case logic.
            channel_name: Target channel name for metric labeling (cognitive).
            content_id: Target content identifier for audit logging and metrics (algorithmic).
            channel_id: Optional platform channel ID (algorithmic).
            fatal: If True, re-raises any caught exception. If False, logs warning and returns fallback.
            fallback: Value returned when non-fatal execution encounters an exception.

        Returns:
            Result of fn() or fallback if non-fatal exception caught.
        """
        start_time = time.perf_counter()
        status = "success"
        ch_id_str = channel_id.value if channel_id else ""

        with self.telemetry_port.start_stage_span(stage_name):
            try:
                return fn()
            except Exception as exc:
                status = "failure"
                self.metrics_port.increment_counter(
                    "cresmo_pipeline_errors_total",
                    1.0,
                    labels={
                        "error_type": exc.__class__.__name__,
                        "channel_id": ch_id_str,
                        "channel_name": channel_name.value,
                        "content_id": content_id.value,
                        "stage": stage_name,
                    },
                )
                if fatal:
                    raise
                logger.warning(
                    "[Pipeline] %s skipped for %s: %s",
                    stage_name,
                    content_id.value,
                    exc,
                )
                return fallback
            finally:
                elapsed = time.perf_counter() - start_time
                self.metrics_port.observe_histogram(
                    "cresmo_pipeline_stage_duration_seconds",
                    elapsed,
                    labels={
                        "stage": stage_name,
                        "channel_id": ch_id_str,
                        "channel_name": channel_name.value,
                        "status": status,
                    },
                )

    def record_session_completion(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        channel_name: ChannelName,
        synthesized_notes: Sequence[AtomicNote],
        inventory: AtomicEntityInventory,
        mocs: Sequence[MapOfContent],
        dedup_report: DeduplicationReport,
        channel_id: ChannelId | None = None,
    ) -> None:
        """Record completed process metrics and session coherence evaluation score."""
        ch_id_str = channel_id.value if channel_id else ""
        self.metrics_port.increment_counter(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={
                "channel_id": ch_id_str,
                "channel_name": channel_name.value,
                "content_id": content_id.value,
                "status": "completed",
                "modality": "transcript",
            },
        )
        self.metrics_port.increment_counter(
            "cresmo_atomic_notes_synthesized_total",
            float(len(synthesized_notes)),
            labels={
                "channel_id": ch_id_str,
                "channel_name": channel_name.value,
                "content_id": content_id.value,
                "note_type": "all",
            },
        )

        item_count = len(inventory.items) if hasattr(inventory, "items") else 1
        coherence_score = (
            min(1.0, len(synthesized_notes) / max(1, item_count)) if item_count else 1.0
        )
        self.telemetry_port.record_session_coherence(
            session_id=session_id,
            content_id=content_id,
            score=coherence_score,
            details={
                "synthesized_notes_count": len(synthesized_notes),
                "inventory_count": item_count,
                "mocs_count": len(mocs),
                "duplicates_unified": dedup_report.duplicates_unified_count,
            },
        )
