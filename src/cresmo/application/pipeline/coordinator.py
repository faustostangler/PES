"""Cresmo Knowledge Synthesis Pipeline Orchestrator.

Orchestrates the cognitive synthesis pipeline per ADR-007 (Template Method), ADR-021, and ADR-070:
- Raw Ingestion (MediaIngestionPort ACL)
- Raw Indexing (IndexRawTranscriptsUseCase)  # FUTURE / DEFERRED
- Fluid Prose & Iterative Expansion Stages: fluid_prose -> gap_filler -> long_expander -> wide_expander (PipelineStageRunner)
- Holistic Inventory Discovery (DiscoverAtomicInventoryUseCase)  # FUTURE / DEFERRED
- Batched Atomic Synthesis (SynthesizeAtomicBatchUseCase)  # FUTURE / DEFERRED
- Map of Content Reconciliation (ReconcileMOCsUseCase)  # FUTURE / DEFERRED
- Duplicate Unification & Entity Resolution (UnifyDuplicateNotesUseCase)  # FUTURE / DEFERRED

Conforms to:
- ADR-001: Cresmo Modular Monolith Strangling
- ADR-007: Pipeline Template Method DRY
- ADR-021: Unified Pipeline Execution Template Method and Telemetry
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineResult
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.pipeline.transcript_loader import (
    ensure_transcript_saved,
    load_transcript_from_file,
)
from cresmo.application.ports import (
    PIPELINE_TRACE_NAME,
    ChannelTaxonomyPort,
    LedgerRepositoryPort,
    MediaIngestionPort,
    MetricName,
    MetricsPort,
    NoOpChannelTaxonomyPort,
    SessionTelemetrySpec,
    TelemetryPort,
    VaultRepositoryPort,
)
from cresmo.application.use_cases.ingest_raw_transcript import IngestRawTranscriptUseCase
from cresmo.domain.entities import (
    PipelineSessionId,
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CresmoDomainError, StageQuarantinedError
from cresmo.domain.stage_registry import StageName, StageRegistry
from cresmo.domain.value_objects import (
    BatchId,
    ChannelName,
    ConvergenceMode,
    LedgerEntry,
    PipelineStatus,
    is_processable_transcript_file,
)

logger = structlog.get_logger(__name__)

CONVEYOR_STAGES: tuple[StageName, ...] = (
    StageName.FLUID_PROSE,
    StageName.GAP_FILLER,
    StageName.LONG_EXPANDER,
    StageName.WIDE_EXPANDER,
)


class CresmoPipeline:
    """Hexagonal Modular Monolith orchestrator for the Cresmo synthesis engine.

    Implements the Template Method execution flow across cognitive synthesis stages,
    coordinating declarative stage specifications, ports, and closed-loop verifiers.
    """

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        stage_runner: PipelineStageRunner,
        *,
        ledger_port: LedgerRepositoryPort | None = None,
        telemetry_port: TelemetryPort | None = None,
        metrics_port: MetricsPort | None = None,
        taxonomy_port: ChannelTaxonomyPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port

        if vault_port is None:
            raise ValueError("vault_port must be provided")
        if stage_runner is None:
            raise ValueError("stage_runner must be provided")
        self.vault_port = vault_port
        self.stage_runner = stage_runner
        self.ledger_port = ledger_port
        self.taxonomy_port: ChannelTaxonomyPort = taxonomy_port or NoOpChannelTaxonomyPort()
        self.telemetry_port: TelemetryPort = telemetry_port or stage_runner.telemetry_port
        self.metrics_port: MetricsPort = metrics_port or stage_runner.metrics_port
        self._warmup_dispatched: bool = False

        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )

    def warmup(self) -> None:
        """Idempotently trigger background warmup across pipeline LLM ports once per instance."""
        if self._warmup_dispatched:
            return
        self._warmup_dispatched = True
        self.stage_runner.warmup()

    def execute(
        self,
        raw: StageTranscript,
        expansion_max_passes: int | None = None,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        batch_id: BatchId | str | None = None,
    ) -> PipelineResult:
        """Execute the end-to-end synthesis pipeline (canonical Template Method)."""
        channel = raw.channel
        content = raw.content
        session_id = PipelineSessionId(content.session_id)
        user_identity = user or UserIdentity.anonymous()

        raw_text = content.text
        resolved_batch_id: str | None = None
        if batch_id:
            resolved_batch_id = (
                batch_id.value if isinstance(batch_id, BatchId) else batch_id.strip()
            ) or None

        session_spec = SessionTelemetrySpec(
            session_id=session_id,
            user_id=user_identity,
            channel_tenant_id=channel.tenant_key,
            trace_name=PIPELINE_TRACE_NAME,
            channel_id=str(channel.id) if channel.id else "",
            channel_name=channel.name,
            content_id=content.id.value,
            content_title=content.title,
            source="transcript",
            raw_characters=len(raw_text),
            raw_words=len(raw_text.split()),
            expansion_max_passes=expansion_max_passes,
            force_reprocess=force_reprocess,
            batch_id=resolved_batch_id,
            video_url=raw.provenance.url or None,
            publication_date=(
                raw.provenance.publication_date.isoformat()
                if raw.provenance.publication_date
                else None
            ),
        )

        # Trace root Level 1: PIPELINE_TRACE_NAME (ADR-037, ADR-065, ADR-070)
        with self.telemetry_port.start_session(session_spec) as root_span:
            if early_result := self._check_idempotent_exit(raw, force_reprocess):
                root_span.set_output(
                    {
                        "status": "SKIPPED_IDEMPOTENT",
                        "reason": "Existing content already processed",
                        "content_id": content.id.value,
                    }
                )
                return early_result

            started_at = datetime.now(UTC)
            if self.ledger_port is not None:
                self.ledger_port.save_entry(
                    self._build_ledger_entry(
                        raw,
                        PipelineStatus.RUNNING,
                        started_at=started_at,
                    )
                )

            execution_context = PipelineExecutionContext(
                user_identity=user_identity,
                channel=channel,
                content=content,
            )

            # =========================================================================
            # CRESMO STAGES CONVEYOR PIPELINE (ADR-007, ADR-043, ADR-054, ADR-057, ADR-073)
            # =========================================================================
            stage_artifacts: dict[StageName, StageTranscript] = {}
            cached_stages: list[str] = []
            current_source: Any = raw

            try:
                for step in CONVEYOR_STAGES:
                    artifact = None
                    if not force_reprocess:
                        cached = self.vault_port.get_stage_transcript(step, content.id)
                        if isinstance(cached, StageTranscript):
                            artifact = cached
                            cached_stages.append(step.value)
                            logger.info(
                                "Reusing cached %s for content_id '%s'",
                                step,
                                content.id.value,
                            )

                    if artifact is None:
                        extra_kwargs: dict[str, Any] = {}
                        if (
                            expansion_max_passes is not None
                            and StageRegistry.contains(step)
                            and StageRegistry.get(step).convergence_mode
                            == ConvergenceMode.HYBRID_SEMANTIC
                        ):
                            extra_kwargs["max_passes"] = expansion_max_passes

                        if (
                            step == StageName.GAP_FILLER
                            or step == StageName.LONG_EXPANDER
                            or step == StageName.WIDE_EXPANDER
                        ):
                            print(f"[STAGE] {step.value}")

                        artifact = self.stage_runner.execute_stage(
                            step,
                            source=current_source,
                            context=execution_context,
                            **extra_kwargs,
                        )
                        if isinstance(artifact, StageTranscript):
                            self.vault_port.save_stage_transcript(step, artifact)

                    stage_artifacts[step] = artifact
                    current_source = artifact

                final_artifact = stage_artifacts[CONVEYOR_STAGES[-1]]

                # Note: Subsequent downstream atomic stages (raw_indexing, atomic_inventory,
                # atomic_batch, reconcile_mocs, duplicate_unification) will be appended once
                # their domain VOs conform to StageTranscript (ADR-054).

                synthesized_text = ""
                resolved_title = ""
                for step in reversed(CONVEYOR_STAGES):
                    step_artifact = stage_artifacts.get(step)
                    if isinstance(step_artifact, StageTranscript):
                        if not synthesized_text and step_artifact.content.text:
                            synthesized_text = step_artifact.content.text
                        if not resolved_title and step_artifact.content.title:
                            resolved_title = step_artifact.content.title
                        if synthesized_text and resolved_title:
                            break
                if not resolved_title:
                    resolved_title = str(content.title or "")

                raw_word_count = len(raw_text.split())
                synthesized_word_count = len(synthesized_text.split())
                expansion_ratio = round(synthesized_word_count / max(raw_word_count, 1), 3)

                cache_hit_count = len(cached_stages)
                cache_hit_ratio = round(cache_hit_count / max(len(CONVEYOR_STAGES), 1), 3)
                completed_stage_names = [step.value for step in CONVEYOR_STAGES]
                root_span.set_output(
                    {
                        "status": "COMPLETED",
                        "stage": completed_stage_names[-1],
                        "stages_completed": completed_stage_names,
                        "stages_reused_from_cache": cached_stages,
                        "cache_hit_count": cache_hit_count,
                        "cache_hit_ratio": cache_hit_ratio,
                        "force_reprocess": force_reprocess,
                        "expansion_max_passes": expansion_max_passes,
                        "content_title": resolved_title,
                        "word_count": synthesized_word_count,
                        "char_count": len(synthesized_text),
                        "source_words": raw_word_count,
                        "synthesized_words": synthesized_word_count,
                        "expansion_ratio": expansion_ratio,
                        "source_characters": len(raw_text),
                        "synthesized_characters": len(synthesized_text),
                    }
                )
            except StageQuarantinedError:
                raise
            except Exception as exc:
                if self.ledger_port is not None:
                    self.ledger_port.save_entry(
                        self._build_ledger_entry(
                            raw,
                            PipelineStatus.FAILED_TRANSFORMATION,
                            started_at=started_at,
                            completed_at=datetime.now(UTC),
                            error_message=str(exc),
                        )
                    )
                raise

            if self.ledger_port is not None:
                self.ledger_port.save_entry(
                    self._build_ledger_entry(
                        raw,
                        PipelineStatus.COMPLETED,
                        started_at=started_at,
                        completed_at=datetime.now(UTC),
                    )
                )

            channel_id = channel.id.value if channel.id else ""
            self.metrics_port.increment_counter(
                MetricName.TRANSCRIPTS_PROCESSED,
                1.0,
                labels={
                    "channel_id": channel_id,
                    "status": "completed",
                    "modality": "transcript",
                },
            )
            self.metrics_port.flush()

            return PipelineResult(
                content_id=content.id,
                source_transcript=raw,
                stage_artifacts=stage_artifacts,
                final_transcript=final_artifact,
            )

    @staticmethod
    def _build_ledger_entry(
        raw: StageTranscript,
        status: PipelineStatus,
        *,
        started_at: datetime,
        completed_at: datetime | None = None,
        error_message: str | None = None,
    ) -> LedgerEntry:
        """Build validated LedgerEntry from StageTranscript for unified ledger persistence."""
        media_url = raw.provenance.url.strip()
        if not media_url.startswith(("http://", "https://")):
            media_url = f"https://cresmo.internal/content/{raw.content.id.value}"
        title = raw.content.title.strip() or f"Content {raw.content.id.value}"
        return LedgerEntry(
            content_id=raw.content.id,
            media_url=media_url,
            title=title,
            channel_name=ChannelName.from_string(raw.channel.name),
            status=status,
            error_message=error_message,
            started_at=started_at,
            completed_at=completed_at,
        )

    def _check_idempotent_exit(
        self,
        raw: StageTranscript,
        force_reprocess: bool,
    ) -> PipelineResult | None:
        """Evaluate ledger idempotency guard and return existing result if already processed."""
        content_id = raw.content.id
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            channel_id = raw.channel.id.value if raw.channel.id else ""
            self.metrics_port.increment_counter(
                MetricName.TRANSCRIPTS_PROCESSED,
                1.0,
                labels={
                    "channel_id": channel_id,
                    "status": "skipped_idempotent",
                    "modality": "transcript",
                },
            )
            self.metrics_port.flush()
            loaded_artifacts: dict[StageName, StageTranscript] = {}
            for step in CONVEYOR_STAGES:
                cached = self.vault_port.get_stage_transcript(step, content_id)
                if cached is not None:
                    loaded_artifacts[step] = cached
            return PipelineResult(
                content_id=content_id,
                source_transcript=raw,
                stage_artifacts=loaded_artifacts,
                final_transcript=loaded_artifacts.get(CONVEYOR_STAGES[-1]),
                already_processed=True,
            )
        return None

    def run_for_video(
        self,
        video_url: str,
        expansion_max_passes: int | None = None,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        batch_id: BatchId | str | None = None,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source."""
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self.execute(
            raw=raw,
            expansion_max_passes=expansion_max_passes,
            force_reprocess=force_reprocess,
            user=user,
            batch_id=batch_id,
        )

    def run_for_text_file(
        self,
        file_path: Path,
        expansion_max_passes: int | None = None,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        batch_id: BatchId | str | None = None,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file."""
        if not is_processable_transcript_file(file_path):
            raise CresmoDomainError(
                f"File '{file_path.name}' is an internal Cresmo artifact or system index "
                "and cannot be processed as a transcript."
            )
        raw = load_transcript_from_file(file_path, taxonomy_port=self.taxonomy_port)
        ensure_transcript_saved(
            self.vault_port,
            file_path,
            raw,
            target_dir=self.vault_port.resolve_stage_dir(StageName.RAW),
        )

        return self.execute(
            raw=raw,
            expansion_max_passes=expansion_max_passes,
            force_reprocess=force_reprocess,
            user=user,
            batch_id=batch_id,
        )
