"""Application Ports (Abstract Base Classes) for the Cresmo Knowledge Synthesis Bounded Context.

Defines the Hexagonal Ports that decouple business logic orchestration from infrastructure
adapters (media scraping, LLM APIs, Obsidian filesystem storage, status ledgers, and prompt templates).

Conforms to:
- ADR-001: Modular Monolith Domain Integrity (Ports & Adapters)
- ADR-004: Native Media Ingestion Decommissioning & Pure Python Adapter
- SPEC-001: Core Knowledge Synthesis Specifications
- SPEC-004: Native Media Ingestion Specifications
"""

from __future__ import annotations

from cresmo.application.ports.anonymizer import AnonymizerPort
from cresmo.application.ports.critique_synthesizer import CritiqueSynthesizerPort
from cresmo.application.ports.embedding import TextEmbeddingPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.application.ports.media import MediaIngestionPort
from cresmo.application.ports.metrics import MetricsPort, NoOpMetricsPort
from cresmo.application.ports.preflight import PreflightProbePort
from cresmo.application.ports.prompt import NoOpPromptProviderPort, PromptProviderPort
from cresmo.application.ports.runtime import NoOpProcessRuntimePort, ProcessRuntimePort
from cresmo.application.ports.settings import (
    DefaultPipelineSettings,
    PipelineSettingsProtocol,
)
from cresmo.application.ports.storage import (
    LedgerRepositoryPort,
    VaultRepositoryPort,
)
from cresmo.application.ports.taxonomy import (
    ChannelTaxonomyPort,
    NoOpChannelTaxonomyPort,
)
from cresmo.application.ports.telemetry import (
    LLM_GENERATION_FALLBACK_SPAN_NAME,
    LLM_GENERATION_SPAN_NAME,
    PIPELINE_ROOT_SPAN_NAME,
    PIPELINE_TRACE_NAME,
    NoOpTelemetryPort,
    TelemetryPort,
    active_telemetry_pass,
    active_telemetry_stage,
    format_stage_generation_span_name,
    format_stage_judge_span_name,
    format_stage_saturation_span_name,
    format_stage_span_name,
    get_active_telemetry_pass,
    get_active_telemetry_stage,
    resolve_llm_generation_span_name,
)
from cresmo.application.ports.transformation import LLMTransformationPort

__all__ = [
    "LLM_GENERATION_FALLBACK_SPAN_NAME",
    "LLM_GENERATION_SPAN_NAME",
    "PIPELINE_ROOT_SPAN_NAME",
    "PIPELINE_TRACE_NAME",
    "AnonymizerPort",
    "ChannelTaxonomyPort",
    "CritiqueSynthesizerPort",
    "DefaultPipelineSettings",
    "LLMTransformationPort",
    "LedgerRepositoryPort",
    "LlmJudgePort",
    "MediaIngestionPort",
    "MetricsPort",
    "NoOpChannelTaxonomyPort",
    "NoOpMetricsPort",
    "NoOpProcessRuntimePort",
    "NoOpPromptProviderPort",
    "NoOpTelemetryPort",
    "PipelineSettingsProtocol",
    "PreflightProbePort",
    "ProcessRuntimePort",
    "PromptProviderPort",
    "TelemetryPort",
    "TextEmbeddingPort",
    "VaultRepositoryPort",
    "active_telemetry_pass",
    "active_telemetry_stage",
    "format_stage_generation_span_name",
    "format_stage_judge_span_name",
    "format_stage_saturation_span_name",
    "format_stage_span_name",
    "get_active_telemetry_pass",
    "get_active_telemetry_stage",
    "resolve_llm_generation_span_name",
]
