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
from typing import Any

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineDependencies, PipelineResult
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.pipeline.transcript_loader import (
    ensure_transcript_saved,
    load_manifest_urls,
    load_transcript_from_file,
)
from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    DefaultPipelineSettings,
    LedgerRepositoryPort,
    LlmJudgePort,
    LLMTransformationPort,
    MediaIngestionPort,
    MetricsPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
    PipelineSettingsProtocol,
    PromptProviderPort,
    TelemetryPort,
    VaultRepositoryPort,
)
from cresmo.application.use_cases import IngestRawTranscriptUseCase
from cresmo.domain.entities import (
    PipelineSessionId,
    SourceTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import (
    BatchId,
    RawIndexEntry,
    is_processable_transcript_file,
)

logger = logging.getLogger(__name__)


def _extract_source_text(raw: Any) -> str:
    """Extract raw transcript text from SourceTranscript triad or duck-typed raw sources."""
    content = getattr(raw, "content", None)
    if content is not None:
        body = getattr(content, "body", None)
        if body:
            return body
    body = getattr(raw, "body", None)
    if body:
        return body
    text = getattr(raw, "text", None)
    if text:
        return text
    return ""


def _extract_fluid_text(fluid: Any) -> str:
    """Extract synthesized fluid prose text from FluidTranscript or duck-typed candidate."""
    body = getattr(fluid, "body", None)
    if body:
        return body
    text = getattr(fluid, "text", None)
    if text:
        return text
    return ""


class CresmoPipeline:
    """Hexagonal Modular Monolith orchestrator for the Cresmo synthesis engine.

    Implements the Template Method execution flow across cognitive synthesis stages,
    coordinating declarative stage specifications, ports, and closed-loop verifiers.
    """

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        vault_port: VaultRepositoryPort,
        stage_runner: PipelineStageRunner | None = None,
        *,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        settings: PipelineSettingsProtocol | None = None,
        telemetry_port: TelemetryPort | None = None,
        metrics_port: MetricsPort | None = None,
        llm_synthesis_port: LLMTransformationPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        llm_judge_port: LlmJudgePort | None = None,
        critique_synthesizer: CritiqueSynthesizerPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port

        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        self.batch_size = batch_size
        self.settings: PipelineSettingsProtocol = settings or DefaultPipelineSettings()

        if stage_runner is not None:
            self.stage_runner = stage_runner
            self.telemetry_port: TelemetryPort = (
                telemetry_port
                or getattr(stage_runner, "telemetry_port", None)
                or NoOpTelemetryPort()
            )
            self.metrics_port: MetricsPort = (
                metrics_port or getattr(stage_runner, "metrics_port", None) or NoOpMetricsPort()
            )
        else:
            if llm_synthesis_port is None:
                raise ValueError("Either stage_runner or llm_synthesis_port must be provided")
            self.telemetry_port = telemetry_port or NoOpTelemetryPort()
            self.metrics_port = metrics_port or NoOpMetricsPort()
            stage_factory = StageFactory(settings=self.settings)
            self.stage_runner = PipelineStageRunner(
                PipelineDependencies(
                    telemetry_port=self.telemetry_port,
                    metrics_port=self.metrics_port,
                    llm_judge=llm_judge_port,
                    judge_blocking=getattr(self.settings, "judge_blocking", False),
                    judge_max_attempts=getattr(self.settings, "judge_max_attempts", 1),
                    prompt_provider=prompt_provider or NoOpPromptProviderPort(),
                    llm_transformation_port=llm_synthesis_port,
                    stage_factory=stage_factory,
                    critique_synthesizer=critique_synthesizer,
                    ledger_port=self.ledger_port,
                )
            )

        self.llm_indexing_port = (
            llm_indexing_port
            or getattr(self.stage_runner, "llm_transformation_port", None)
            or llm_synthesis_port
        )

        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )

    @property
    def stage_factory(self) -> StageFactory | None:
        """Access the stage factory from the stage runner."""
        return self.stage_runner.stage_factory

    @property
    def llm_synthesis_port(self) -> LLMTransformationPort | None:
        """Access the primary LLM transformation port from the stage runner."""
        return self.stage_runner.llm_transformation_port

    @property
    def llm_judge(self) -> LlmJudgePort | None:
        """Access the LLM judge port from the stage runner."""
        return self.stage_runner.llm_judge

    @property
    def prompt_provider(self) -> PromptProviderPort | None:
        """Access the prompt provider from the stage runner."""
        return self.stage_runner.prompt_provider

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Asynchronously trigger warmup across pipeline LLM ports."""
        if self.llm_indexing_port is not None:
            self.llm_indexing_port.warmup(timeout_seconds=timeout_seconds)
        runner_llm = getattr(self.stage_runner, "llm_transformation_port", None)
        if runner_llm is not None and runner_llm is not self.llm_indexing_port:
            self.stage_runner.warmup(timeout_seconds=timeout_seconds)

    def execute(
        self,
        raw: SourceTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        entry: RawIndexEntry | None = None,
        batch_id: BatchId | str | None = None,
    ) -> PipelineResult:
        """Execute the end-to-end synthesis pipeline (canonical Template Method)."""
        channel = raw.channel
        content = raw.content
        session_id = PipelineSessionId.create(
            channel=channel,
            content_id=content,
        )
        user_identity = user or UserIdentity.anonymous()

        raw_text = _extract_source_text(raw)
        root_telemetry_metadata: dict[str, Any] = {
            "source": "transcript",
            "channel_id": str(channel.id) if channel.id else "",
            "channel_name": channel.name,
            "content_id": content.id.value,
            "content_title": content.title,
            "raw_characters": len(raw_text),
            "raw_words": len(raw_text.split()),
            "gap_filler_passes": gap_filler_passes,
        }
        if batch_id:
            resolved_batch_id = (
                batch_id.value if isinstance(batch_id, BatchId) else batch_id.strip()
            )
            root_telemetry_metadata["batch_id"] = resolved_batch_id
        if raw.provenance.url:
            root_telemetry_metadata["video_url"] = raw.provenance.url
        if raw.provenance.publication_date:
            root_telemetry_metadata["publication_date"] = (
                raw.provenance.publication_date.isoformat()
            )

        # Trace root Level 1: cresmo.synthesis_pipeline (ADR-037)
        with self.telemetry_port.start_pipeline_session(
            session_id=session_id,
            user_id=user_identity,
            channel_tenant_id=channel.tenant_key,
            metadata=root_telemetry_metadata,
            trace_name="cresmo.synthesis_pipeline",
        ):
            if early_result := self._check_idempotent_exit(raw, entry, force_reprocess):
                self.telemetry_port.record_session_output(
                    {
                        "status": "SKIPPED_IDEMPOTENT",
                        "reason": "Existing content already processed",
                        "content_id": content.id.value,
                    }
                )
                return early_result

            execution_context = PipelineExecutionContext(
                session_id=session_id,
                user_identity=user_identity,
                channel=channel,
                content=content,
            )

            # =========================================================================
            # ESTEIRA DE ESTÁGIOS CRESMO (CONVEYOR PIPELINE), Estágio 2 em diante por enquanto comentadas
            # =========================================================================

            # Estágio 1: Fluid Prose
            fluid = self.stage_runner.execute_stage(
                "fluid_prose",
                source=raw,
                context=execution_context,
            )

            # Estágio 2: Raw Indexing
            # index = self.stage_runner.execute_stage("raw_indexing", source=fluid, context=execution_context)

            # Estágio 3: Gap Filler
            # gaps = self.stage_runner.execute_stage("gap_filler", source=fluid, context=execution_context)

            # Estágio 4: Long Expander
            # long_exp = self.stage_runner.execute_stage("long_expander", source=gaps, context=execution_context)

            # Estágio 5: Wide Expander
            # wide_exp = self.stage_runner.execute_stage("wide_expander", source=long_exp, context=execution_context)

            # Estágio 6: Atomic Inventory
            # inventory = self.stage_runner.execute_stage("atomic_inventory", source=wide_exp, context=execution_context)

            # Estágio 7: Atomic Batch
            # notes = self.stage_runner.execute_stage("atomic_batch", source=inventory, context=execution_context)

            # Estágio 8: Reconcile MOCs
            # mocs = self.stage_runner.execute_stage("reconcile_mocs", source=notes, context=execution_context)

            fluid_text = _extract_fluid_text(fluid)
            raw_word_count = len(raw_text.split())
            synthesized_word_count = len(fluid_text.split())
            expansion_ratio = round(synthesized_word_count / max(raw_word_count, 1), 3)

            # Trace output (ADR-037 canonical DDD metrics)
            self.telemetry_port.record_session_output(
                {
                    "status": "COMPLETED",
                    "stage": "fluid_prose",
                    "stages_completed": ["fluid_prose"],
                    "content_title": getattr(fluid, "title", content.title),
                    "word_count": synthesized_word_count,
                    "char_count": len(fluid_text),
                    "source_words": raw_word_count,
                    "synthesized_words": synthesized_word_count,
                    "expansion_ratio": expansion_ratio,
                    "source_characters": len(raw_text),
                    "synthesized_characters": len(fluid_text),
                }
            )

            return PipelineResult(
                content_id=content.id,
                success=True,
                source_transcript=raw,
                fluid_transcript=fluid,
                index_entry=entry,
            )

    def _check_idempotent_exit(
        self,
        raw: SourceTranscript,
        entry: RawIndexEntry | None,
        force_reprocess: bool,
    ) -> PipelineResult | None:
        """Evaluate ledger idempotency guard and return existing result if already processed."""
        content_id = raw.content.id
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            channel_id = raw.channel.id.value if raw.channel.id else ""
            self.metrics_port.increment_counter(
                "cresmo_transcripts_processed_total",
                1.0,
                labels={
                    "channel_id": channel_id,
                    "channel_name": raw.channel.name,
                    "content_id": content_id.value,
                    "status": "skipped_idempotent",
                    "modality": "transcript",
                },
            )
            return PipelineResult(
                content_id=content_id,
                success=True,
                source_transcript=raw,
                index_entry=entry,
                compendium=self.vault_port.get_enriched_compendium(content_id),
                already_processed=True,
            )
        return None

    def run_for_video(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        batch_id: BatchId | str | None = None,
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
            batch_id=batch_id,
        )

    def run_for_text_file(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
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
        self.warmup()
        raw = load_transcript_from_file(file_path)
        ensure_transcript_saved(
            self.vault_port,
            file_path,
            raw,
            target_dir=self.settings.raw_dir,
        )

        return self.execute(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
            user=user,
            batch_id=batch_id,
        )

    def run_for_manifest(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        batch_id: BatchId | str | None = None,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file."""
        resolved_batch_id = batch_id or BatchId.generate()
        return [
            self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
                user=user,
                batch_id=resolved_batch_id,
            )
            for url in load_manifest_urls(manifest_path)
        ]
