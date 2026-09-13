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


class CresmoPipeline:
    """Hexagonal Modular Monolith orchestrator for the Cresmo synthesis engine."""

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

        # Idempotency guard
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            return PipelineResult(
                content_id=content_id,
                success=True,
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )

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

        raw = RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id,
            channel_category=channel_category,
            video_description=video_description,
        )
        self.vault_port.save_raw_transcript(raw)

        # Socratic Gap Filler & Longitudinal Expander
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
