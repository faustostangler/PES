"""Cresmo Knowledge Synthesis Pipeline Orchestrator package.

Conforms to:
- ADR-001: Cresmo Modular Monolith Strangling
- ADR-007: Pipeline Template Method DRY
- ADR-021: Unified Pipeline Execution Template Method and Telemetry
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.application.pipeline.coordinator import CresmoPipeline
from cresmo.application.pipeline.models import (
    PipelineDependencies,
    PipelineResult,
    StageExecutionOptions,
)
from cresmo.application.pipeline.stage_descriptor import StageConfig
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
from cresmo.application.pipeline.transcript_loader import load_transcript_from_file

__all__ = [
    "CresmoPipeline",
    "PipelineDependencies",
    "PipelineExecutionContext",
    "PipelineResult",
    "PipelineStageRunner",
    "StageConfig",
    "StageExecutionOptions",
    "StageFactory",
    "load_transcript_from_file",
]
