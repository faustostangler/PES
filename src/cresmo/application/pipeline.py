"""Cresmo Knowledge Synthesis Pipeline Orchestrator.

Orchestrates the 6 incremental integer stages:
- Stage 1: Raw Transcript Ingestion (MediaIngestionPort ACL)
- Stage 2: Socratic Gap Filler (FillGapsFluidProseUseCase)
- Stage 3: Longitudinal & Synchronic Expander (ExpandLongitudinalSynchronicUseCase)
- Stage 4: Holistic Inventory Discovery (DiscoverAtomicInventoryUseCase)
- Stage 5: Batched Atomic Synthesis (SynthesizeAtomicBatchUseCase)
- Stage 6: Map of Content Reconciliation (ReconcileMOCsUseCase)
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
)
from cresmo.domain.entities import AtomicNote, MapOfContent
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import ContentId


@dataclass(frozen=True)
class PipelineResult:
    """Immutable execution outcome of the 6-stage synthesis pipeline."""

    content_id: ContentId
    success: bool
    synthesized_notes: tuple[AtomicNote, ...]
    reconciled_mocs: tuple[MapOfContent, ...]
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

        # Stage Use Cases instantiation
        self.stage_1_ingest = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.stage_2_gap_filler = FillGapsFluidProseUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
        )
        self.stage_3_expander = ExpandLongitudinalSynchronicUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
        )
        self.stage_4_inventory = DiscoverAtomicInventoryUseCase(
            llm_port=self.llm_port,
        )
        self.stage_5_batch = SynthesizeAtomicBatchUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
        )
        self.stage_6_moc = ReconcileMOCsUseCase(
            llm_port=self.llm_port,
            vault_port=self.vault_port,
        )

    def run_for_video(
        self,
        video_url: str,
        gap_filler_passes: int = 1,
    ) -> PipelineResult:
        """Run the end-to-end 6-stage pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for Stage 2.

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        # Stage 1: Raw Transcript Ingestion
        raw = self.stage_1_ingest.execute(
            video_url=video_url,
        )
        if raw is None:
            raise CresmoDomainError(f"Stage 1 Ingestion failed to retrieve transcript for: {video_url}")

        content_id = raw.content_id

        # Idempotency check
        if self.ledger_port and self.ledger_port.is_processed(content_id):
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                error_message="Content already marked processed in ledger.",
            )

        # Stage 2: Socratic Gap Filler
        compendium = self.stage_2_gap_filler.execute(
            raw_transcript=raw,
            passes=gap_filler_passes,
        )

        # Stage 3: Longitudinal & Synchronic Expander
        expanded_compendium = self.stage_3_expander.execute(
            compendium=compendium,
        )

        # Stage 4: Holistic Inventory Discovery
        inventory = self.stage_4_inventory.execute(
            compendium=expanded_compendium,
        )

        # Stage 5: Batched Atomic Synthesis
        notes = self.stage_5_batch.execute(
            inventory=inventory,
            compendium=expanded_compendium,
        )

        # Stage 6: Map of Content Reconciliation
        mocs = self.stage_6_moc.execute()

        # Mark processed in ledger
        if self.ledger_port:
            self.ledger_port.mark_processed(content_id)

        return PipelineResult(
            content_id=content_id,
            success=True,
            synthesized_notes=tuple(notes),
            reconciled_mocs=tuple(mocs),
        )
