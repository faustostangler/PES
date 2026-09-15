"""Cresmo Knowledge Synthesis Pipeline Orchestrator.

Orchestrates the 7 incremental integer stages:
- Stage 1: Raw Transcript Ingestion (MediaIngestionPort ACL)
- Stage 2: Socratic Gap Filler (FillGapsFluidProseUseCase)
- Stage 3: Longitudinal & Synchronic Expander (ExpandLongitudinalSynchronicUseCase)
- Stage 4: Holistic Inventory Discovery (DiscoverAtomicInventoryUseCase)
- Stage 5: Batched Atomic Synthesis (SynthesizeAtomicBatchUseCase)
- Stage 6: Map of Content Reconciliation (ReconcileMOCsUseCase)
- Stage 7: Graph Entity Resolution & Duplicate Unification (UnifyDuplicateNotesUseCase)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from cresmo.application.ports import (
    LedgerRepositoryPort,
    LLMTransformationPort,
    MediaIngestionPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.application.use_cases import (
    DiscoverAtomicInventoryUseCase,
    ExpandLongitudinalSynchronicUseCase,
    FillGapsFluidProseUseCase,
    IngestRawTranscriptUseCase,
    ReconcileMOCsUseCase,
    SynthesizeAtomicBatchUseCase,
    UnifyDuplicateNotesUseCase,
)
from cresmo.domain.entities import AtomicNote, MapOfContent, RawTranscript
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import ContentId


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass(frozen=True)
class PipelineResult:
    """Summary record emitted at the conclusion of a pipeline run."""

    content_id: ContentId
    success: bool
    synthesized_notes: tuple[AtomicNote, ...]
    reconciled_mocs: tuple[MapOfContent, ...]
    duplicates_unified: int = 0
    already_processed: bool = False
    error_message: str | None = None
mutants_xǁCresmoPipelineǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCresmoPipelineǁrun_for_video__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut: MutantDict = {}  # type: ignore
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut: MutantDict = {}  # type: ignore


class CresmoPipeline:
    """Hexagonal Modular Monolith orchestrator for the Cresmo synthesis engine."""

    @_mutmut_mutated(mutants_xǁCresmoPipelineǁ__init____mutmut)
    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_orig(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_1(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 6,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_2(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = None
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_3(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = None
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_4(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = None
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_5(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = None
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_6(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is not None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_7(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = None
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_8(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = None

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_9(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = None
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_10(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=None,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_11(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=None,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_12(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_13(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_14(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = None
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_15(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=None,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_16(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=None,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_17(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=None,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_18(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_19(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_20(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_21(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = None
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_22(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=None,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_23(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=None,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_24(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=None,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_25(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_26(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_27(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_28(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = None
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_29(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=None,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_30(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=None,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_31(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_32(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_33(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = None
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_34(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=None,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_35(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=None,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_36(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=None,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_37(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=None,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_38(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_39(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_40(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_41(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_42(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = None
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_43(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=None,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_44(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=None,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_45(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=None,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_46(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_47(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_48(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def xǁCresmoPipelineǁ__init____mutmut_49(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = None

    def xǁCresmoPipelineǁ__init____mutmut_50(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.fill_gaps_fluid_prose = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.expand_longitudinal_synchronic = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
            prompt_provider=self.prompt_provider,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=None,
        )

    @_mutmut_mutated(mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut)
    def _synthesize_transcript(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_orig(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_1(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 4,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_2(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = True,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_3(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = None

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_4(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) or not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_5(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port or self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_6(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(None) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_7(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_8(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=None,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_9(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=None,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_10(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=None,
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_11(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=None,
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_12(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=None,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_13(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_14(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_15(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_16(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_17(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_18(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=False,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_19(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=False,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_20(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = None
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_21(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(None)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_22(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is not None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_23(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = None
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_24(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=None,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_25(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=None,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_26(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_27(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_28(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = None

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_29(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=None,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_30(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = None

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_31(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=None,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_32(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=None,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_33(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=None,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_34(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_35(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_36(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = None

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_37(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = None

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_38(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(None)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_39(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = None

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_40(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=None,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_41(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=None,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_42(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=None,
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_43(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=None,
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_44(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=None,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_45(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_46(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_47(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_48(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_49(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_50(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=False,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_51(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(None),
            reconciled_mocs=tuple(mocs),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    def xǁCresmoPipelineǁ_synthesize_transcript__mutmut_52(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Execute Stages 2 through 7 (Template Method core for knowledge synthesis).

        Coordinates idempotency checks, enrichment, inventory discovery,
        atomic note batching, MOC reconciliation, and duplicate unification.
        """
        content_id = raw.content_id

        # Idempotency guard — bypass only when caller explicitly requests force-reprocess
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

        # Socratic Gap Filler & Longitudinal Expander (supports resumed execution)
        expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
        if expanded_compendium is None:
            compendium = self.fill_gaps_fluid_prose.execute(
                raw_transcript=raw,
                passes=gap_filler_passes,
            )
            expanded_compendium = self.expand_longitudinal_synchronic.execute(
                compendium=compendium,
            )

        # Holistic Inventory Discovery
        inventory = self.discover_atomic_inventory.execute(
            compendium=expanded_compendium,
        )

        # Batched Atomic Synthesis
        self.synthesize_atomic_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Map of Content Reconciliation
        mocs = self.reconcile_mocs.execute()

        # Stage 7: Graph Entity Resolution & Duplicate Unification
        dedup_report = self.unify_duplicate_notes.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        final_notes = self.vault_port.get_all_atomic_notes()

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(final_notes),
            reconciled_mocs=tuple(None),
            duplicates_unified=dedup_report.duplicates_unified_count,
        )

    @_mutmut_mutated(mutants_xǁCresmoPipelineǁrun_for_video__mutmut)
    def run_for_video(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_orig(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_1(
        self,
        video_url: str,
        gap_filler_passes: int = 4,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_2(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = True,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_3(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = None
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_4(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=None)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_5(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is not None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_6(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(None)

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_7(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=None,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_8(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=None,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_9(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=None,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_10(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_11(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_video__mutmut_12(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            )

    @_mutmut_mutated(mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut)
    def _load_transcript_from_file(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_orig(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_1(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_2(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(None)

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_3(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = None
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_4(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding=None).strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_5(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="XXutf-8XX").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_6(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="UTF-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_7(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_8(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(None)

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_9(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = None
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_10(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = None
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_11(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(None)
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_12(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "XXXX".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_13(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() and c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_14(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c not in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_15(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("XX-XX", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_16(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "XX_XX"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_17(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 9 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_18(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 < len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_19(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) < 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_20(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 65:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_21(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = None
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_22(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = None
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_23(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:25] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_24(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "XXtextXX"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_25(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "TEXT"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_26(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = None
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_27(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(None).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_28(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode(None)).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_29(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("XXutf-8XX")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_30(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("UTF-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_31(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:17]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_32(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = None

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_33(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = None

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_34(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=None)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_35(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = None
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_36(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace(None, " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_37(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", None).title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_38(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace(" ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_39(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", ).title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_40(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace(None, " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_41(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", None).replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_42(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace(" ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_43(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", ).replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_44(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("XX_XX", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_45(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", "XX XX").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_46(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("XX-XX", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_47(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", "XX XX").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_48(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = None
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_49(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "XXtextXX"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_50(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "TEXT"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_51(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = None
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_52(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "XXpriority_textXX"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_53(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "PRIORITY_TEXT"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_54(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = None
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_55(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(None)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_56(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = None
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_57(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = None
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_58(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = "XXXX"
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_59(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = None

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_60(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith(None):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_61(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("XX---XX"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_62(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = None
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_63(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(None, raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_64(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", None)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_65(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_66(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", )
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_67(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"XX^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$XX", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_68(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = None
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_69(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = None
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_70(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = None
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_71(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) and {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_72(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(None) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_73(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") and meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_74(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get(None) or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_75(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("XXvideo_titleXX") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_76(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("VIDEO_TITLE") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_77(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get(None):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_78(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("XXtitleXX"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_79(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("TITLE"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_80(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = None
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_81(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(None)
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_82(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") and meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_83(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get(None) or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_84(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("XXvideo_titleXX") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_85(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("VIDEO_TITLE") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_86(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get(None))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_87(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("XXtitleXX"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_88(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("TITLE"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_89(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") and meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_90(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get(None) or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_91(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("XXchannel_nameXX") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_92(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("CHANNEL_NAME") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_93(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get(None):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_94(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("XXchannelXX"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_95(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("CHANNEL"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_96(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = None
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_97(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(None)
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_98(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") and meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_99(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get(None) or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_100(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("XXchannel_nameXX") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_101(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("CHANNEL_NAME") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_102(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get(None))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_103(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("XXchannelXX"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_104(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("CHANNEL"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_105(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = None
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_106(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(None)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_107(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get(None):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_108(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("XXchannel_idXX"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_109(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("CHANNEL_ID"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_110(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = None
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_111(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(None)
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_112(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["XXchannel_idXX"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_113(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["CHANNEL_ID"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_114(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") and meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_115(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get(None) or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_116(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("XXchannel_categoryXX") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_117(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("CHANNEL_CATEGORY") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_118(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get(None):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_119(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("XXdomainXX"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_120(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("DOMAIN"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_121(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = None
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_122(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(None)
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_123(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") and meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_124(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get(None) or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_125(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("XXchannel_categoryXX") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_126(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("CHANNEL_CATEGORY") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_127(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get(None))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_128(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("XXdomainXX"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_129(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("DOMAIN"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_130(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get(None):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_131(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("XXurlXX"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_132(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("URL"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_133(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = None
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_134(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(None)
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_135(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["XXurlXX"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_136(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["URL"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_137(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get(None):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_138(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("XXvideo_descriptionXX"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_139(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("VIDEO_DESCRIPTION"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_140(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = None
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_141(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(None)
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_142(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["XXvideo_descriptionXX"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_143(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["VIDEO_DESCRIPTION"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_144(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=None,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_145(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=None,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_146(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=None,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_147(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=None,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_148(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=None,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_149(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=None,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_150(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=None,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_151(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=None,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_152(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_153(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_154(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_155(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_156(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_157(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_category=channel_category,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_158(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            video_description=video_description,
        )

    def xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_159(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name = file_path.parent.name if file_path.parent.name else "text"
        channel_id = "priority_text"
        channel_category, _ = classify_channel(channel_name)
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name = str(meta.get("channel_name") or meta.get("channel"))
                        channel_category, _ = classify_channel(channel_name)
                    if meta.get("channel_id"):
                        channel_id = str(meta["channel_id"])
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            )

    @_mutmut_mutated(mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut)
    def run_for_text_file(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_orig(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_1(
        self,
        file_path: Path,
        gap_filler_passes: int = 4,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_2(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = True,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_3(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = None
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_4(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(None)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_5(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(None)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_6(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=None,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_7(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=None,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_8(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=None,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_9(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_10(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            force_reprocess=force_reprocess,
        )

    def xǁCresmoPipelineǁrun_for_text_file__mutmut_11(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses Stage 1 media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through Stages 2-7.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        raw = self._load_transcript_from_file(file_path)
        self.vault_port.save_raw_transcript(raw)
        return self._synthesize_transcript(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            )

    @_mutmut_mutated(mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut)
    def run_for_manifest(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_orig(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_1(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 2,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_2(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = True,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_3(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_4(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(None)

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_5(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = None
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_6(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding=None).splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_7(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="XXutf-8XX").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_8(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="UTF-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_9(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = None
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_10(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = None
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_11(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str or not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_12(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_13(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith(None):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_14(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("XX#XX"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_15(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(None)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_16(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = None
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_17(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = None
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_18(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=None,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_19(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=None,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_20(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=None,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_21(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_22(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                force_reprocess=force_reprocess,
            )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_23(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                )
            results.append(res)
        return results

    def xǁCresmoPipelineǁrun_for_manifest__mutmut_24(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
            )
            results.append(None)
        return results

mutants_xǁCresmoPipelineǁ__init____mutmut['_mutmut_orig'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_1'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_2'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_3'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_4'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_5'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_6'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_7'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_8'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_9'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_10'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_11'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_12'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_13'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_14'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_15'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_16'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_17'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_18'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_18 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_19'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_19 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_20'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_20 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_21'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_21 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_22'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_22 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_23'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_23 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_24'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_24 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_25'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_25 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_26'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_26 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_27'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_27 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_28'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_28 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_29'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_29 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_30'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_30 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_31'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_31 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_32'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_32 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_33'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_33 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_34'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_34 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_35'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_35 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_36'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_36 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_37'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_37 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_38'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_38 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_39'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_39 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_40'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_40 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_41'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_41 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_42'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_42 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_43'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_43 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_44'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_44 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_45'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_45 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_46'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_46 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_47'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_47 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_48'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_48 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_49'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_49 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ__init____mutmut['xǁCresmoPipelineǁ__init____mutmut_50'] = CresmoPipeline.xǁCresmoPipelineǁ__init____mutmut_50 # type: ignore # mutmut generated

mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['_mutmut_orig'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_1'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_2'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_3'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_4'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_5'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_6'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_7'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_8'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_9'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_10'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_11'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_12'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_13'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_14'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_15'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_16'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_17'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_17 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_18'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_18 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_19'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_19 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_20'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_20 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_21'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_21 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_22'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_22 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_23'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_23 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_24'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_24 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_25'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_25 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_26'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_26 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_27'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_27 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_28'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_28 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_29'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_29 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_30'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_30 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_31'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_31 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_32'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_32 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_33'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_33 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_34'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_34 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_35'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_35 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_36'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_36 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_37'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_37 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_38'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_38 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_39'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_39 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_40'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_40 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_41'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_41 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_42'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_42 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_43'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_43 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_44'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_44 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_45'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_45 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_46'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_46 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_47'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_47 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_48'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_48 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_49'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_49 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_50'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_50 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_51'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_51 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_synthesize_transcript__mutmut['xǁCresmoPipelineǁ_synthesize_transcript__mutmut_52'] = CresmoPipeline.xǁCresmoPipelineǁ_synthesize_transcript__mutmut_52 # type: ignore # mutmut generated

mutants_xǁCresmoPipelineǁrun_for_video__mutmut['_mutmut_orig'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_1'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_2'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_3'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_4'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_5'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_6'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_7'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_8'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_9'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_10'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_11'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_video__mutmut['xǁCresmoPipelineǁrun_for_video__mutmut_12'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_video__mutmut_12 # type: ignore # mutmut generated

mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['_mutmut_orig'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_1'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_2'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_3'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_4'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_5'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_6'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_7'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_8'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_9'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_10'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_11'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_12'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_13'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_14'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_15'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_16'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_17'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_17 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_18'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_18 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_19'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_19 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_20'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_20 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_21'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_21 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_22'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_22 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_23'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_23 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_24'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_24 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_25'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_25 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_26'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_26 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_27'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_27 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_28'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_28 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_29'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_29 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_30'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_30 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_31'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_31 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_32'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_32 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_33'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_33 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_34'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_34 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_35'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_35 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_36'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_36 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_37'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_37 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_38'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_38 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_39'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_39 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_40'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_40 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_41'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_41 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_42'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_42 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_43'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_43 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_44'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_44 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_45'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_45 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_46'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_46 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_47'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_47 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_48'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_48 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_49'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_49 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_50'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_50 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_51'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_51 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_52'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_52 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_53'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_53 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_54'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_54 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_55'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_55 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_56'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_56 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_57'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_57 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_58'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_58 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_59'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_59 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_60'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_60 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_61'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_61 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_62'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_62 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_63'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_63 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_64'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_64 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_65'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_65 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_66'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_66 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_67'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_67 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_68'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_68 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_69'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_69 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_70'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_70 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_71'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_71 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_72'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_72 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_73'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_73 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_74'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_74 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_75'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_75 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_76'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_76 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_77'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_77 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_78'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_78 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_79'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_79 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_80'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_80 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_81'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_81 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_82'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_82 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_83'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_83 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_84'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_84 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_85'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_85 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_86'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_86 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_87'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_87 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_88'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_88 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_89'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_89 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_90'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_90 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_91'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_91 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_92'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_92 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_93'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_93 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_94'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_94 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_95'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_95 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_96'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_96 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_97'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_97 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_98'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_98 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_99'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_99 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_100'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_100 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_101'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_101 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_102'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_102 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_103'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_103 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_104'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_104 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_105'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_105 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_106'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_106 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_107'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_107 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_108'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_108 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_109'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_109 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_110'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_110 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_111'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_111 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_112'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_112 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_113'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_113 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_114'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_114 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_115'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_115 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_116'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_116 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_117'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_117 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_118'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_118 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_119'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_119 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_120'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_120 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_121'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_121 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_122'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_122 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_123'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_123 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_124'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_124 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_125'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_125 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_126'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_126 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_127'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_127 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_128'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_128 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_129'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_129 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_130'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_130 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_131'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_131 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_132'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_132 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_133'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_133 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_134'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_134 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_135'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_135 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_136'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_136 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_137'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_137 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_138'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_138 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_139'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_139 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_140'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_140 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_141'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_141 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_142'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_142 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_143'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_143 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_144'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_144 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_145'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_145 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_146'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_146 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_147'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_147 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_148'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_148 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_149'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_149 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_150'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_150 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_151'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_151 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_152'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_152 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_153'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_153 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_154'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_154 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_155'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_155 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_156'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_156 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_157'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_157 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_158'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_158 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁ_load_transcript_from_file__mutmut['xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_159'] = CresmoPipeline.xǁCresmoPipelineǁ_load_transcript_from_file__mutmut_159 # type: ignore # mutmut generated

mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['_mutmut_orig'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_1'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_2'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_3'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_4'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_5'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_6'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_7'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_8'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_9'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_10'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_text_file__mutmut['xǁCresmoPipelineǁrun_for_text_file__mutmut_11'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_text_file__mutmut_11 # type: ignore # mutmut generated

mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['_mutmut_orig'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_1'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_2'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_3'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_4'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_5'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_6'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_7'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_8'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_9'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_10'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_11'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_12'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_13'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_14'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_15'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_16'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_17'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_17 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_18'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_18 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_19'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_19 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_20'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_20 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_21'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_21 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_22'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_22 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_23'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_23 # type: ignore # mutmut generated
mutants_xǁCresmoPipelineǁrun_for_manifest__mutmut['xǁCresmoPipelineǁrun_for_manifest__mutmut_24'] = CresmoPipeline.xǁCresmoPipelineǁrun_for_manifest__mutmut_24 # type: ignore # mutmut generated
