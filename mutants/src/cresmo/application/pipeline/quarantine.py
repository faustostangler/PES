"""Quarantine handling protocol for quarantined stages (ADR-031)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from opentelemetry import trace

from cresmo.application.ports import LedgerRepositoryPort, MetricsPort
from cresmo.domain.exceptions import StageQuarantinedError
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    JudgeEvaluation,
    LedgerEntry,
    MediaProvenance,
    PipelineStatus,
)

logger = logging.getLogger(__name__)


def record_stage_quarantine(
    *,
    stage_name: str,
    channel: Channel | None = None,
    content: Content | None = None,
    evaluation: JudgeEvaluation,
    critique: str,
    effective_max_attempts: int,
    ledger_port: LedgerRepositoryPort | None,
    metrics_port: MetricsPort,
    provenance: MediaProvenance | None = None,
    media_url: str = "",
    content_id: ContentId | None = None,
    channel_name: str | ChannelName | None = None,
    channel_id: ChannelId | str | None = None,
    content_title: str = "",
) -> None:
    """Execute the 4-step fail-fast quarantine protocol per ADR-031."""
    resolved_cid = content.id if content is not None else content_id
    if resolved_cid is None:
        raise ValueError("content or content_id must be provided to record_stage_quarantine")

    if channel is not None:
        channel_name_string = channel.name
        channel_name_vo = ChannelName(channel.name)
        channel_id_string = channel.id.value if channel.id else ""
    else:
        channel_name_string = (
            channel_name.value if isinstance(channel_name, ChannelName) else (channel_name or "")
        )
        channel_name_vo = (
            channel_name
            if isinstance(channel_name, ChannelName)
            else ChannelName(channel_name_string or "unknown")
        )
        channel_id_string = (
            channel_id.value if isinstance(channel_id, ChannelId) else (channel_id or "")
        )

    resolved_title = (content.title if content is not None else content_title) or ""

    if ledger_port is not None:
        try:
            existing = ledger_port.get_entry(resolved_cid)
            effective_media_url = (
                existing.media_url
                if existing
                else (
                    provenance.url
                    if provenance and provenance.url
                    else (
                        media_url
                        if media_url
                        else f"https://cresmo.internal/content/{resolved_cid.value}"
                    )
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

    span = trace.get_current_span()
    if span:
        span.set_attribute("quarantined", True)
        span.set_attribute("quarantine.stage", stage_name)
        span.set_attribute("quarantine.critique", critique or "")
        span.set_attribute("quarantine.attempts", effective_max_attempts)
        span.set_attribute("quarantine.overall_score", evaluation.overall_score)
        # ID-ID Parity: Algorithmic Identifiers
        effective_channel_id = channel_id_string or channel_name_string
        span.set_attribute("cresmo.content.id", resolved_cid.value)
        span.set_attribute("cresmo.channel.id", effective_channel_id)
        # TXT-TXT Parity: Cognitive Display Names
        effective_content_title = resolved_title or resolved_cid.value
        span.set_attribute("cresmo.channel.name", channel_name_string)
        span.set_attribute("cresmo.content.title", effective_content_title)

    metrics_port.increment_counter(
        "cresmo_stage_quarantines_total",
        1.0,
        labels={"stage": stage_name, "channel_name": channel_name_string},
    )

    raise StageQuarantinedError(
        stage_name=stage_name,
        content_id=resolved_cid.value,
        attempts=effective_max_attempts,
        critique=critique or "",
        overall_score=evaluation.overall_score,
    )
