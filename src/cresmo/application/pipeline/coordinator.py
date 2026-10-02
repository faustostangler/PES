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

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import PipelineResult
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.pipeline.transcript_loader import (
    ensure_raw_saved_in_vault,
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
    SourceTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import (
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
        llm_judge_port: LlmJudgePort | None = None,
        critique_synthesizer: CritiqueSynthesizerPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port

        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port

        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        self.llm_judge = llm_judge_port

        self.telemetry_port: TelemetryPort = telemetry_port or NoOpTelemetryPort()
        self.metrics_port: MetricsPort = metrics_port or NoOpMetricsPort()
        self.settings: PipelineSettingsProtocol = settings or DefaultPipelineSettings()
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

        self.llm_indexing_port = llm_indexing_port or self.llm_synthesis_port

        self.stage_factory = StageFactory(settings=self.settings)

        self.stage_runner = PipelineStageRunner(
            telemetry_port=self.telemetry_port,
            metrics_port=self.metrics_port,
            llm_judge=self.llm_judge,
            judge_blocking=getattr(self.settings, "judge_blocking", False),
            judge_max_attempts=getattr(self.settings, "judge_max_attempts", 1),
            prompt_provider=self.prompt_provider,
            llm_transformation_port=self.llm_synthesis_port,
            stage_factory=self.stage_factory,
            critique_synthesizer=critique_synthesizer,
            ledger_port=self.ledger_port,
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
        raw: SourceTranscript,
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

            execution_context = PipelineExecutionContext(
                session_id=session_id,
                user_identity=user_identity,
                channel_name=channel_name,
                content_id=content_id,
                channel_id=raw.channel_id,
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

            return PipelineResult(
                content_id=content_id,
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
                source_transcript=raw,
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
