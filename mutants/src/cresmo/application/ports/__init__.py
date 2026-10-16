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
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.application.ports.media import MediaIngestionPort
from cresmo.application.ports.metrics import MetricsPort, NoOpMetricsPort
from cresmo.application.ports.prompt import NoOpPromptProviderPort, PromptProviderPort
from cresmo.application.ports.settings import (
    DefaultPipelineSettings,
    PipelineSettingsProtocol,
)
from cresmo.application.ports.storage import (
    LedgerRepositoryPort,
    VaultRepositoryPort,
)
from cresmo.application.ports.telemetry import (
    NoOpTelemetryPort,
    TelemetryPort,
)
from cresmo.application.ports.transformation import LLMTransformationPort

__all__ = [
    "AnonymizerPort",
    "CritiqueSynthesizerPort",
    "DefaultPipelineSettings",
    "LLMTransformationPort",
    "LedgerRepositoryPort",
    "LlmJudgePort",
    "MediaIngestionPort",
    "MetricsPort",
    "NoOpMetricsPort",
    "NoOpPromptProviderPort",
    "NoOpTelemetryPort",
    "PipelineSettingsProtocol",
    "PromptProviderPort",
    "TelemetryPort",
    "VaultRepositoryPort",
]
