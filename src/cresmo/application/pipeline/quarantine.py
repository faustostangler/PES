"""Quarantine handling protocol for quarantined stages (ADR-031)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from opentelemetry import trace

from cresmo.application.ports import LedgerRepositoryPort, MetricsPort
from cresmo.domain.exceptions import StageQuarantinedError
from cresmo.domain.value_objects import (
    ChannelId,
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
    channel_name: str | ChannelName,
    channel_id: ChannelId | str | None = None,
    evaluation: JudgeEvaluation,
    critique: str,
    effective_max_attempts: int,
    ledger_port: LedgerRepositoryPort | None,
    metrics_port: MetricsPort,
) -> None:
    """Execute the 4-step fail-fast quarantine protocol per ADR-031."""
    ch_name_str = channel_name.value if isinstance(channel_name, ChannelName) else channel_name
    ch_name_vo = channel_name if isinstance(channel_name, ChannelName) else ChannelName(ch_name_str)
    channel_id_str = channel_id.value if isinstance(channel_id, ChannelId) else (channel_id or "")

    if ledger_port is not None:
        try:
            existing = ledger_port.get_entry(content_id)
            ledger_port.save_entry(
                LedgerEntry(
                    content_id=content_id,
                    media_url=(
                        existing.media_url
                        if existing
                        else f"https://cresmo.internal/content/{content_id.value}"
                    ),
                    title=existing.title if existing else f"Quarantined Content {content_id.value}",
                    channel_name=ch_name_vo,
                    status=PipelineStatus.QUARANTINED,
                    error_message=f"Stage '{stage_name}' quarantined: {critique}",
                    started_at=existing.started_at if existing else None,
                    completed_at=datetime.now(UTC),
                )
            )
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
        span.set_attribute("cresmo.content.id", content_id.value)
        span.set_attribute("cresmo.channel.name", ch_name_str)
        if channel_id_str:
            span.set_attribute("cresmo.channel.id", channel_id_str)

    metrics_port.increment_counter(
        "cresmo_stage_quarantines_total",
        1.0,
        labels={"stage": stage_name, "channel_name": ch_name_str},
    )

    raise StageQuarantinedError(
        stage_name=stage_name,
        content_id=content_id.value,
        attempts=effective_max_attempts,
        critique=critique or "",
        overall_score=evaluation.overall_score,
    )
