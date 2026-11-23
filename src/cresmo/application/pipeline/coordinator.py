"""Cresmo Knowledge Synthesis Pipeline Orchestrator.

Orchestrates the cognitive synthesis pipeline per ADR-007 (Template Method), ADR-021, and ADR-070:
- Raw Ingestion (MediaIngestionPort ACL)
- Raw Indexing (IndexRawTranscriptsUseCase)  # FUTURE / DEFERRED
- Fluid Prose & Iterative Expansion Stages: fluid_prose -> gap_filler -> long_expander -> wide_expander (PipelineStageRunner)
- Holistic Inventory Discovery (DiscoverAtomicInventoryUseCase)  # FUTURE / DEFERRED
- Batched Atomic Synthesis (SynthesizeAtomicBatchUseCase)  # FUTURE / DEFERRED
- Map of Content Reconciliation (ReconcileMOCsUseCase)  # FUTURE / DEFERRED
- Duplicate Unification & Entity Resolution (UnifyDuplicateNotesUseCase)

Conforms to:
- ADR-001: Cresmo Modular Monolith Strangling
- ADR-007: Pipeline Template Method DRY
- ADR-021: Unified Pipeline Execution Template Method and Telemetry
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.models import (
    PipelineDependencies,
    PipelineResult,
)
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.pipeline.transcript_loader import (
    ensure_transcript_saved,
    load_manifest_urls,
    load_transcript_from_file,
)
from cresmo.application.ports import (
    PIPELINE_TRACE_NAME,
    ChannelTaxonomyPort,
    CritiqueSynthesizerPort,
    DefaultPipelineSettings,
    LedgerRepositoryPort,
    LlmJudgePort,
    LLMTransformationPort,
    MediaIngestionPort,
    MetricsPort,
    NoOpChannelTaxonomyPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
    PipelineSettingsProtocol,
    PromptProviderPort,
    SessionTelemetrySpec,
    TelemetryPort,
    VaultRepositoryPort,
)
from cresmo.application.use_cases import IngestRawTranscriptUseCase
from cresmo.domain.entities import (
    PipelineSessionId,
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.stage_registry import StageName, StageRegistry
from cresmo.domain.value_objects import (
    BatchId,
    ConvergenceMode,
    RawIndexEntry,
    is_processable_transcript_file,
)

logger = structlog.get_logger(__name__)

CONVEYOR_STAGES: tuple[StageName, ...] = (
    StageName.FLUID_PROSE,
    StageName.GAP_FILLER,
    StageName.LONG_EXPANDER,
    StageName.WIDE_EXPANDER,
)


def _extract_source_text(source_target: StageTranscript | Any) -> str:
    """Extract raw transcript text from StageTranscript triad."""
    if isinstance(source_target, StageTranscript):
        return source_target.content.text
    return ""


def _extract_fluid_text(source: StageTranscript | Any) -> str:
    """Extract synthesized fluid prose text from StageTranscript envelope."""
    if isinstance(source, StageTranscript):
        return source.content.text
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
        taxonomy_port: ChannelTaxonomyPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port

        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        self.taxonomy_port: ChannelTaxonomyPort = taxonomy_port or NoOpChannelTaxonomyPort()
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
            llm_judge = llm_judge_port
            llm_transformation_port = llm_synthesis_port
            prompt_provider = prompt_provider or NoOpPromptProviderPort()
            stage_factory = StageFactory(settings=self.settings)
            self.stage_runner = PipelineStageRunner(
                PipelineDependencies(
                    telemetry_port=self.telemetry_port,
                    metrics_port=self.metrics_port,
                    llm_judge=llm_judge,
                    judge_blocking=getattr(self.settings, "judge_blocking", False),
                    judge_max_attempts=getattr(self.settings, "judge_max_attempts", 2),
                    prompt_provider=prompt_provider,
                    llm_transformation_port=llm_transformation_port,
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
        runner_llm_port = getattr(self.stage_runner, "llm_transformation_port", None)
        if runner_llm_port is not None and runner_llm_port is not self.llm_indexing_port:
            self.stage_runner.warmup(timeout_seconds=timeout_seconds)

    def execute(
        self,
        raw: StageTranscript,
        expansion_max_passes: int | None = None,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        entry: RawIndexEntry | None = None,
        batch_id: BatchId | str | None = None,
    ) -> PipelineResult:
        """Execute the end-to-end synthesis pipeline (canonical Template Method)."""
        channel = raw.channel
        content = raw.content
        session_id = PipelineSessionId(content.session_id)
        user_identity = user or UserIdentity.anonymous()

        raw_text = _extract_source_text(raw)
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
            if early_result := self._check_idempotent_exit(raw, entry, force_reprocess):
                root_span.set_output(
                    {
                        "status": "SKIPPED_IDEMPOTENT",
                        "reason": "Existing content already processed",
                        "content_id": content.id.value,
                    }
                )
                return early_result

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
            for step in reversed(CONVEYOR_STAGES):
                candidate_text = _extract_fluid_text(stage_artifacts.get(step))
                if candidate_text:
                    synthesized_text = candidate_text
                    break
            raw_word_count = len(raw_text.split())
            synthesized_word_count = len(synthesized_text.split())
            expansion_ratio = round(synthesized_word_count / max(raw_word_count, 1), 3)

            resolved_title = ""
            for step in reversed(CONVEYOR_STAGES):
                step_content = getattr(stage_artifacts.get(step), "content", None)
                step_title = getattr(step_content, "title", None)
                if step_title:
                    resolved_title = str(step_title)
                    break
            if not resolved_title:
                resolved_title = str(content.title or "")

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

            return PipelineResult(
                content_id=content.id,
                success=True,
                source_transcript=raw,
                stage_artifacts=stage_artifacts,
                final_transcript=final_artifact,
                index_entry=entry,
            )

    def _check_idempotent_exit(
        self,
        raw: StageTranscript,
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
            loaded_artifacts: dict[StageName, StageTranscript] = {}
            for step in CONVEYOR_STAGES:
                cached = self.vault_port.get_stage_transcript(step, content_id)
                if cached is not None:
                    loaded_artifacts[step] = cached
            return PipelineResult(
                content_id=content_id,
                success=True,
                source_transcript=raw,
                index_entry=entry,
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
        self.warmup()
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
        self.warmup()
        raw = load_transcript_from_file(file_path, taxonomy_port=self.taxonomy_port)
        ensure_transcript_saved(
            self.vault_port,
            file_path,
            raw,
            target_dir=self.settings.raw_dir,
        )

        return self.execute(
            raw=raw,
            expansion_max_passes=expansion_max_passes,
            force_reprocess=force_reprocess,
            user=user,
            batch_id=batch_id,
        )

    def run_for_manifest(
        self,
        manifest_path: Path,
        expansion_max_passes: int | None = None,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        batch_id: BatchId | str | None = None,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file."""
        batch_id = batch_id or BatchId.generate()
        return [
            self.run_for_video(
                video_url=video_url,
                expansion_max_passes=expansion_max_passes,
                force_reprocess=force_reprocess,
                user=user,
                batch_id=batch_id,
            )
            for video_url in load_manifest_urls(manifest_path)
        ]
