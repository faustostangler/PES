"""Quarantine handling protocol for quarantined stages (ADR-031)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from opentelemetry import trace

from cresmo.application.ports import LedgerRepositoryPort, MetricsPort
from cresmo.domain.exceptions import StageQuarantinedError
from cresmo.domain.value_objects import (
    ChannelName,
    ContentId,
    JudgeEvaluation,
    LedgerEntry,
    PipelineStatus,
)

logger = logging.getLogger(__name__)


def record_stage_quarantine(
    *,
    stage_name: str,
    content_id: ContentId,
    channel_name: ChannelName,
    evaluation: JudgeEvaluation,
    critique: str,
    effective_max_attempts: int,
    ledger_port: LedgerRepositoryPort | None,
    metrics_port: MetricsPort,
) -> None:
    """Execute the 4-step fail-fast quarantine protocol per ADR-031."""
    if ledger_port is not None:
        try:
            existing = ledger_port.get_entry(content_id)
            media_url = (
                existing.media_url
                if existing
                else f"https://cresmo.internal/content/{content_id.value}"
            )
            title = existing.title if existing else f"Quarantined Content {content_id.value}"
            started_at = existing.started_at if existing else None
            entry = LedgerEntry(
                content_id=content_id,
                media_url=media_url,
                title=title,
                channel_name=channel_name,
                status=PipelineStatus.QUARANTINED,
                error_message=f"Stage '{stage_name}' quarantined: {critique}",
                started_at=started_at,
                completed_at=datetime.now(UTC),
            )
            ledger_port.save_entry(entry)
        except Exception as ledger_err:  # noqa: BLE001 - Resilient audit persistence
            logger.error(
                "Failed to record quarantine entry in ledger for %s: %s",
                content_id.value,
                ledger_err,
            )

    span = trace.get_current_span()
    if span:
        span.set_attribute("quarantined", True)
        span.set_attribute("quarantine.stage", stage_name)
        span.set_attribute("quarantine.critique", critique or "")
        span.set_attribute("quarantine.attempts", effective_max_attempts)
        span.set_attribute("quarantine.overall_score", evaluation.overall_score)

    metrics_port.increment_counter(
        "cresmo_stage_quarantines_total",
        1.0,
        labels={"stage": stage_name, "channel_name": channel_name.value},
    )

    raise StageQuarantinedError(
        stage_name=stage_name,
        content_id=content_id.value,
        attempts=effective_max_attempts,
        critique=critique or "",
        overall_score=evaluation.overall_score,
    )
