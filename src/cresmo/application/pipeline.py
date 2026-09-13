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

from dataclasses import dataclass

from cresmo.application.ports import (
    LedgerRepositoryPort,
    LLMTransformationPort,
    MediaIngestionPort,
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
from cresmo.domain.entities import AtomicNote, MapOfContent
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import ContentId


@dataclass(frozen=True)
class PipelineResult:
    """Immutable execution outcome of the 7-stage synthesis pipeline."""

    content_id: ContentId
    success: bool
    synthesized_notes: tuple[AtomicNote, ...]
    reconciled_mocs: tuple[MapOfContent, ...]
    duplicates_unified: int = 0
    already_processed: bool = False
    error_message: str | None = None


class CresmoPipeline:
    """Hexagonal Modular Monolith orchestrator for the Cresmo synthesis engine."""

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port
        self.llm_port = llm_port
        self.vault_port = vault_port
        self.ledger_port = ledger_port

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
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )

    def run_for_video(
        self,
        video_url: str,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        # Raw Transcript Ingestion
        raw = self.ingest_raw_transcript.execute(
            video_url=video_url,
        )
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

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
