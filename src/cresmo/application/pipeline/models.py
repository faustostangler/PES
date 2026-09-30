"""Pipeline outcome models and execution result aggregates."""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.application.use_cases import DeduplicationReport
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    RawTranscript,
)
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    ContentId,
    RawIndexEntry,
)


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
        raw_transcript: Optional RawTranscript aggregate root from raw ingestion.
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
    raw_transcript: RawTranscript | None = None
    index_entry: RawIndexEntry | None = None
    compendium: EnrichedCompendium | None = None
    inventory: AtomicEntityInventory | None = None
    dedup_report: DeduplicationReport | None = None
    duplicates_unified: int = 0
    already_processed: bool = False
    error_message: str | None = None
