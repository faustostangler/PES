"""Pipeline outcome models and execution result aggregates."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING

from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    LedgerRepositoryPort,
    LlmJudgePort,
    LLMTransformationPort,
    MetricsPort,
    PromptProviderPort,
    TelemetryPort,
)
from cresmo.domain.entities import StageTranscript
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import ContentId
from cresmo.domain.value_objects.policies import DEFAULT_JUDGE_MAX_ATTEMPTS

if TYPE_CHECKING:
    from cresmo.application.pipeline.stage_factory import StageFactory


@dataclass(frozen=True, slots=True)
class PipelineDependencies:
    """Strongly-typed Parameter Object encapsulating pipeline runner collaborators (ADR-026 Rule 7)."""

    telemetry_port: TelemetryPort
    metrics_port: MetricsPort
    llm_judge: LlmJudgePort | None = None
    judge_blocking: bool = False
    judge_max_attempts: int = DEFAULT_JUDGE_MAX_ATTEMPTS
    prompt_provider: PromptProviderPort | None = None
    llm_transformation_port: LLMTransformationPort | None = None
    stage_factory: StageFactory | None = None
    critique_synthesizer: CritiqueSynthesizerPort | None = None
    ledger_port: LedgerRepositoryPort | None = None


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Summary record emitted upon successful completion of a pipeline execution.

    Conforms to Single Error Channel (ADR-077): failures always raise typed exceptions.

    Attributes:
        content_id: Canonical ContentId processed.
        source_transcript: Optional StageTranscript aggregate root from raw ingestion.
        stage_artifacts: Read-only mapping of conveyor StageName to StageTranscript output.
        final_transcript: Terminal conveyor StageTranscript output.
        already_processed: True if execution was skipped due to ledger idempotency match.
    """

    content_id: ContentId
    source_transcript: StageTranscript | None = None
    stage_artifacts: Mapping[StageName, StageTranscript] = field(default_factory=dict)
    final_transcript: StageTranscript | None = None
    already_processed: bool = False

    def __post_init__(self) -> None:
        """Freeze stage_artifacts mapping to preserve PipelineResult immutability."""
        object.__setattr__(self, "stage_artifacts", MappingProxyType(dict(self.stage_artifacts)))
