"""Cresmo Knowledge Synthesis Pipeline Orchestrator.

Orchestrates the cognitive synthesis pipeline per ADR-007 (Template Method) and ADR-021:
- Raw Ingestion (MediaIngestionPort ACL)
- Raw Indexing (IndexRawTranscriptsUseCase)
- Fluid Prose Synthesis (FillGapsUseCase)
- Longitudinal & Synchronic Expansion (ExpandCompendiumUseCase)
- Holistic Inventory Discovery (DiscoverAtomicInventoryUseCase)
- Batched Atomic Synthesis (SynthesizeAtomicBatchUseCase)
- Map of Content Reconciliation (ReconcileMOCsUseCase)
- Duplicate Unification & Entity Resolution (UnifyDuplicateNotesUseCase)

Conforms to:
- ADR-001: Cresmo Modular Monolith Strangling
- ADR-007: Pipeline Template Method DRY
- ADR-021: Unified Pipeline Execution Template Method and Telemetry
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import logging
from pathlib import Path

from opentelemetry import trace

from cresmo.application.pipeline.models import PipelineResult
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.pipeline.transcript_loader import (
    ensure_raw_saved_in_vault,
    load_manifest_urls,
    load_transcript_from_file,
)
from cresmo.application.ports import (
    DefaultPipelineSettings,
    LedgerRepositoryPort,
    LLMTransformationPort,
    MediaIngestionPort,
    MetricsPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
    PipelineSettingsProtocol,
    PromptProviderPort,
    QualityJudgePort,
    TelemetryPort,
    VaultRepositoryPort,
)
from cresmo.application.use_cases import (
    ConcatMasterUseCase,
    DiscoverAtomicInventoryUseCase,
    ExpandCompendiumUseCase,
    FillGapsUseCase,
    IndexRawTranscriptsUseCase,
    IngestRawTranscriptUseCase,
    ReconcileMOCsUseCase,
    SynthesizeAtomicBatchUseCase,
    TransformFluidProseUseCase,
    UnifyDuplicateNotesUseCase,
)
from cresmo.domain.entities import (
    ChannelTenantId,
    PipelineSessionId,
    RawTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CresmoDomainError, DomainValidationError
from cresmo.domain.value_objects import (
    EvaluationContext,
    JudgeCriterion,
    RawIndexEntry,
    is_processable_transcript_file,
)

logger = logging.getLogger(__name__)


class CresmoPipeline:
    """Hexagonal Modular Monolith orchestrator for the Cresmo synthesis engine.

    Implements the Template Method execution flow across cognitive synthesis use cases,
    coordinating dependency-injected Use Cases, Ports, and Adapters.
    """

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        settings: PipelineSettingsProtocol | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        telemetry_port: TelemetryPort | None = None,
        metrics_port: MetricsPort | None = None,
        quality_judge_port: QualityJudgePort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port

        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port

        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        self.quality_judge = quality_judge_port

        self.telemetry_port: TelemetryPort = telemetry_port or NoOpTelemetryPort()
        self.metrics_port: MetricsPort = metrics_port or NoOpMetricsPort()
        self.settings: PipelineSettingsProtocol = settings or DefaultPipelineSettings()
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

        self.llm_indexing_port = llm_indexing_port or self.llm_synthesis_port

        self.stage_runner = PipelineStageRunner(
            telemetry_port=self.telemetry_port,
            metrics_port=self.metrics_port,
        )

        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )

        self.transform_fluid_prose = TransformFluidProseUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )

        self.index_raw = IndexRawTranscriptsUseCase(
            vault_port=self.vault_port,
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            max_chars=self.settings.raw_index_max_chars,
            temperature=self.settings.raw_index_temperature,
            language=self.settings.language,
        )

        self.fill_gaps = FillGapsUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )

        self.expand_compendium = ExpandCompendiumUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )

        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            prompt_provider=self.prompt_provider,
            temperature=0.0,
            max_rewrites=self.settings.inventory_max_attempts,
        )

        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )

        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )

        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

        self.concat_master = ConcatMasterUseCase(
            vault_port=self.vault_port,
            settings=self.settings,
        )

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Asynchronously trigger warmup across pipeline LLM ports."""
        self.llm_indexing_port.warmup(timeout_seconds=timeout_seconds)
        if self.llm_synthesis_port is not self.llm_indexing_port:
            self.llm_synthesis_port.warmup(timeout_seconds=timeout_seconds)

    def execute(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        entry: RawIndexEntry | None = None,
    ) -> PipelineResult:
        """Execute the end-to-end synthesis pipeline (canonical Template Method)."""
        content_id = raw.content_id
        channel_name = raw.channel_name
        session_id = PipelineSessionId.create(
            channel=channel_name,
            content_id=content_id,
            channel_id=raw.channel_id,
        )
        tenant_id = ChannelTenantId.create(
            channel=channel_name,
            channel_id=raw.channel_id,
        )
        user_identity = user or UserIdentity.anonymous()

        root_metadata = {
            "source": "transcript",
            "channel": channel_name.value,
            "channel_name": channel_name.value,
            "content_id": content_id.value,
            "title": raw.title or content_id.value,
        }
        if raw.channel_id:
            root_metadata["channel_id"] = raw.channel_id.value
        if raw.source_url:
            root_metadata["video_url"] = raw.source_url

        with self.telemetry_port.start_pipeline_session(
            session_id=session_id,
            user_id=user_identity,
            channel_tenant_id=tenant_id,
            metadata=root_metadata,
            trace_name="cresmo.pipeline.execution",
        ):
            if early_result := self._check_idempotent_exit(raw, entry, force_reprocess):
                return early_result

            fluid_transcript = self.stage_runner.run_stage(
                "fluid_prose",
                lambda: self.transform_fluid_prose.execute(raw, user=user_identity),
                channel_name=channel_name,
                content_id=content_id,
                channel_id=raw.channel_id,
            )

            if self.quality_judge is not None:
                span = trace.get_current_span()
                ctx = span.get_span_context() if span else None
                active_trace_id = (
                    format(ctx.trace_id, "032x")
                    if ctx and ctx.trace_id
                    else f"cresmo_{channel_name.value}_{content_id.value}"
                )
                eval_context = EvaluationContext(
                    stage_name="fluid_prose",
                    raw_text=raw.body,
                    candidate_text=fluid_transcript.body,
                    metadata={"content_id": content_id.value, "channel_name": channel_name.value},
                    trace_id=active_trace_id,
                    required_criteria=(
                        JudgeCriterion.ORALITY_REMOVAL,
                        JudgeCriterion.SEMANTIC_FAITHFULNESS,
                        JudgeCriterion.NER_PRESERVATION,
                        JudgeCriterion.STRUCTURAL_COMPLIANCE,
                    ),
                )
                evaluation = self.quality_judge.evaluate(eval_context)
                if not evaluation.passed:
                    logger.warning(
                        "Quality judge reported low score for 'fluid_prose' (overall=%.2f, passed=%s).",
                        evaluation.overall_score,
                        evaluation.passed,
                    )
                    if getattr(self.settings, "judge_blocking", False):
                        raise DomainValidationError(
                            f"Fluid prose quality evaluation failed threshold: {evaluation.overall_score:.2f}"
                        )

            if entry is None:
                entry = self.stage_runner.run_stage(
                    "raw_indexing",
                    lambda: self.index_raw.execute(fluid_transcript, user=user_identity),
                    channel_name=channel_name,
                    content_id=content_id,
                    channel_id=raw.channel_id,
                    fatal=False,
                )

            expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
            if expanded_compendium is None:
                enriched_compendium = self.stage_runner.run_stage(
                    "gap_filler",
                    lambda: self.fill_gaps.execute(
                        fluid_transcript=fluid_transcript,
                        passes=gap_filler_passes,
                        user=user_identity,
                    ),
                    channel_name=channel_name,
                    content_id=content_id,
                    channel_id=raw.channel_id,
                )
                expanded_compendium = self.stage_runner.run_stage(
                    "expansion",
                    lambda: self.expand_compendium.execute(
                        compendium=enriched_compendium,
                        user=user_identity,
                    ),
                    channel_name=channel_name,
                    content_id=content_id,
                    channel_id=raw.channel_id,
                )

            inventory = self.stage_runner.run_stage(
                "inventory",
                lambda: self.discover_atomic_inventory.execute(
                    compendium=expanded_compendium,
                    user=user_identity,
                ),
                channel_name=channel_name,
                content_id=content_id,
                channel_id=raw.channel_id,
            )

            synthesized_notes = self.stage_runner.run_stage(
                "atomic_batch",
                lambda: self.synthesize_atomic_batch.execute(
                    inventory=inventory,
                    compendium=expanded_compendium,
                    user=user_identity,
                ),
                channel_name=channel_name,
                content_id=content_id,
                channel_id=raw.channel_id,
            )

            mocs = self.stage_runner.run_stage(
                "mocs",
                lambda: self.reconcile_mocs.execute(
                    session_id=session_id,
                    user_id=user_identity,
                ),
                channel_name=channel_name,
                content_id=content_id,
                channel_id=raw.channel_id,
            )

            dedup_report = self.stage_runner.run_stage(
                "duplicate_unification",
                lambda: self.unify_duplicate_notes.execute(),
                channel_name=channel_name,
                content_id=content_id,
                channel_id=raw.channel_id,
            )

            if self.ledger_port:
                self.ledger_port.mark_processed(content_id)

            self.stage_runner.record_session_completion(
                session_id=session_id,
                content_id=content_id,
                channel_name=channel_name,
                synthesized_notes=synthesized_notes,
                inventory=inventory,
                mocs=mocs,
                dedup_report=dedup_report,
                channel_id=raw.channel_id,
            )

            return PipelineResult(
                content_id=content_id,
                success=True,
                raw_transcript=raw,
                fluid_transcript=fluid_transcript,
                index_entry=entry,
                compendium=expanded_compendium,
                inventory=inventory,
                synthesized_notes=tuple(synthesized_notes),
                reconciled_mocs=tuple(mocs),
                dedup_report=dedup_report,
                duplicates_unified=dedup_report.duplicates_unified_count,
            )

    def _check_idempotent_exit(
        self,
        raw: RawTranscript,
        entry: RawIndexEntry | None,
        force_reprocess: bool,
    ) -> PipelineResult | None:
        """Evaluate ledger idempotency guard and return existing result if already processed."""
        content_id = raw.content_id
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            ch_id_str = raw.channel_id.value if raw.channel_id else ""
            self.metrics_port.increment_counter(
                "cresmo_transcripts_processed_total",
                1.0,
                labels={
                    "channel_id": ch_id_str,
                    "channel_name": raw.channel_name.value,
                    "content_id": content_id.value,
                    "status": "skipped_idempotent",
                    "modality": "transcript",
                },
            )
            return PipelineResult(
                content_id=content_id,
                success=True,
                raw_transcript=raw,
                index_entry=entry,
                compendium=self.vault_port.get_enriched_compendium(content_id),
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )
        return None

    def run_for_video(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source."""
        self.warmup()
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self.execute(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
            user=user,
        )

    def run_for_text_file(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file."""
        if not is_processable_transcript_file(file_path):
            raise CresmoDomainError(
                f"File '{file_path.name}' is an internal Cresmo artifact or system index "
                "and cannot be processed as a transcript."
            )
        self.warmup()
        raw = load_transcript_from_file(file_path)
        ensure_raw_saved_in_vault(self.vault_port, file_path, raw)

        return self.execute(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
            user=user,
        )

    def run_for_manifest(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file."""
        return [
            self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
                user=user,
            )
            for url in load_manifest_urls(manifest_path)
        ]
