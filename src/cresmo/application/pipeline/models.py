"""Pipeline outcome models and execution result aggregates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    LedgerRepositoryPort,
    LlmJudgePort,
    LLMTransformationPort,
    MetricsPort,
    PromptProviderPort,
    TelemetryPort,
)
from cresmo.application.use_cases import DeduplicationReport
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    FluidTranscript,
    MapOfContent,
    SourceTranscript,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    ChannelId,
    ChannelName,
    ContentId,
    RawIndexEntry,
)


@dataclass(frozen=True, slots=True)
class PipelineDependencies:
    """Strongly-typed Parameter Object encapsulating pipeline runner collaborators (ADR-026 Rule 7)."""

    telemetry_port: TelemetryPort
    metrics_port: MetricsPort
    llm_judge: LlmJudgePort | None = None
    judge_blocking: bool = False
    judge_max_attempts: int = 1
    prompt_provider: PromptProviderPort | None = None
    llm_transformation_port: LLMTransformationPort | None = None
    stage_factory: Any | None = None
    critique_synthesizer: CritiqueSynthesizerPort | None = None
    ledger_port: LedgerRepositoryPort | None = None


@dataclass(frozen=True, slots=True)
class StageExecutionOptions:
    """Strongly-typed Parameter Object for stage execution parameters (ADR-026 Rule 7)."""

    channel_name: ChannelName | None = None
    content_id: ContentId | None = None
    channel_id: ChannelId | None = None
    session_id: str | None = None
    user_id: str | None = None
    fatal: bool = True
    fallback: Any | None = None


@dataclass(frozen=True)
class PipelineResult:
    """Summary record emitted at the conclusion of an end-to-end pipeline execution.

    Encapsulates both the terminal operational outcome and the rich domain aggregates
    and intermediate artifacts produced across all incremental synthesis stages.

    Attributes:
        content_id: Canonical ContentId processed.
        success: True if all stages completed successfully without unhandled errors.
        synthesized_notes: Tuple of all newly synthesized AtomicNote domain aggregates.
        reconciled_mocs: Tuple of MapOfContent aggregates updated or created.
        source_transcript: Optional SourceTranscript aggregate root from raw ingestion.
        index_entry: Optional RawIndexEntry catalog projection from raw indexing.
        compendium: Optional EnrichedCompendium aggregate root from fluid prose & expansion.
        inventory: Optional AtomicEntityInventory value object from inventory discovery.
        dedup_report: Optional DeduplicationReport execution summary from duplicate unification.
        duplicates_unified: Total count of duplicate notes consolidated during duplicate unification.
        already_processed: True if execution was skipped due to ledger idempotency match.
        error_message: Optional error message string if execution terminated early.
    """

    content_id: ContentId
    success: bool
    synthesized_notes: tuple[AtomicNote, ...] = ()
    reconciled_mocs: tuple[MapOfContent, ...] = ()
    source_transcript: SourceTranscript | None = None
    fluid_transcript: FluidTranscript | None = None
    index_entry: RawIndexEntry | None = None
    compendium: EnrichedCompendium | None = None
    inventory: AtomicEntityInventory | None = None
    dedup_report: DeduplicationReport | None = None
    duplicates_unified: int = 0
    already_processed: bool = False
    error_message: str | None = None
