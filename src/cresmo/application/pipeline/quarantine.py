"""Quarantine handling protocol for quarantined stages (ADR-031, ADR-070)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog

from cresmo.application.ports import (
    LedgerRepositoryPort,
    MetricName,
    MetricsPort,
    TelemetryPort,
)
from cresmo.domain.exceptions import StageQuarantinedError
from cresmo.domain.value_objects import (
    ChannelName,
    JudgeEvaluation,
    LedgerEntry,
    MediaProvenance,
    PipelineStatus,
)

if TYPE_CHECKING:
    from cresmo.application.pipeline.context import PipelineExecutionContext

logger = structlog.get_logger(__name__)


def record_stage_quarantine(
    *,
    stage_name: str,
    context: PipelineExecutionContext,
    evaluation: JudgeEvaluation,
    critique: str,
    effective_max_attempts: int,
    ledger_port: LedgerRepositoryPort | None,
    metrics_port: MetricsPort,
    telemetry_port: TelemetryPort,
    provenance: MediaProvenance | None = None,
) -> None:
    """Execute the 4-step fail-fast quarantine protocol per ADR-031 and ADR-070."""
    channel = context.channel
    content = context.content
    resolved_cid = content.id
    channel_name_string = channel.name
    channel_name_vo = ChannelName(channel.name)
    channel_id_string = channel.id.value if channel.id else ""
    resolved_title = content.title or ""

    if ledger_port is not None:
        try:
            existing = ledger_port.get_entry(resolved_cid)
            effective_media_url = (
                existing.media_url
                if existing
                else (
                    provenance.url
                    if provenance and provenance.url
                    else f"https://cresmo.internal/content/{resolved_cid.value}"
                )
            )
            ledger_port.save_entry(
                LedgerEntry(
                    content_id=resolved_cid,
                    media_url=effective_media_url,
                    title=existing.title
                    if existing
                    else (resolved_title or f"Quarantined Content {resolved_cid.value}"),
                    channel_name=channel_name_vo,
                    status=PipelineStatus.QUARANTINED,
                    error_message=f"Stage '{stage_name}' quarantined: {critique}",
                    started_at=existing.started_at if existing else None,
                    completed_at=datetime.now(UTC),
                )
            )
        except Exception as ledger_err:  # noqa: BLE001 - Resilient audit persistence
            logger.error(
                "Failed to record quarantine entry in ledger for %s: %s",
                resolved_cid.value,
                ledger_err,
            )

    effective_channel_id = channel_id_string or channel_name_string
    effective_content_title = resolved_title or resolved_cid.value
    telemetry_port.current_span().set_attributes(
        {
            "quarantined": True,
            "quarantine.stage": stage_name,
            "quarantine.critique": critique,
            "quarantine.attempts": effective_max_attempts,
            "quarantine.overall_score": evaluation.overall_score,
            "cresmo.content.id": resolved_cid.value,
            "cresmo.channel.id": effective_channel_id,
            "cresmo.channel.name": channel_name_string,
            "cresmo.content.title": effective_content_title,
        }
    )

    metrics_port.increment_counter(
        MetricName.STAGE_QUARANTINES,
        1.0,
        labels={"stage": stage_name, "channel_id": channel_id_string},
    )

    raise StageQuarantinedError(
        stage_name=stage_name,
        content_id=resolved_cid.value,
        attempts=effective_max_attempts,
        critique=critique,
        overall_score=evaluation.overall_score,
    )
