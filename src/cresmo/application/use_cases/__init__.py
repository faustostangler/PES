"""Use Cases for the Cresmo Knowledge Synthesis pipeline.

Core domain orchestration use cases:
- IngestRawTranscriptUseCase (Media ingestion and audio transcription)
- IndexRawTranscriptsUseCase (Catalog conceptual indexing and LLM-as-a-judge quality loops)
- FillGapsFluidProseUseCase (Socratic gap filling and multi-pass fluid prose expansion)
- ExpandLongitudinalSynchronicUseCase (Braudelian longue durée and Jaspers synchronic expansion)
- DiscoverAtomicInventoryUseCase (Holistic candidate entity inventory discovery)
- SynthesizeAtomicBatchUseCase (Batched atomic note synthesis and causal matrix modeling)
- ReconcileMOCsUseCase (Thematic Map of Content graph clustering and reconciliation)
- UnifyDuplicateNotesUseCase (Graph entity resolution, deduplication, and link rewriting)
"""

from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discover_atomic_inventory import (
    DiscoverAtomicInventoryUseCase,
)
from cresmo.application.use_cases.discover_batch_sources import (
    BatchDiscoveryQuery,
    BatchSource,
    DiscoverBatchSourcesUseCase,
)
from cresmo.application.use_cases.expand_longitudinal_synchronic import (
    ExpandLongitudinalSynchronicUseCase,
)
from cresmo.application.use_cases.fill_gaps_fluid_prose import FillGapsFluidProseUseCase
from cresmo.application.use_cases.index_raw_transcripts import IndexRawTranscriptsUseCase
from cresmo.application.use_cases.ingest_raw_transcript import (
    IngestRawTranscriptUseCase,
)
from cresmo.application.use_cases.reconcile_mocs import ReconcileMOCsUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.synthesize_atomic_batch import (
    SynthesizeAtomicBatchUseCase,
)
from cresmo.application.use_cases.unify_duplicate_notes import (
    DeduplicationReport,
    DuplicateCluster,
    UnifyDuplicateNotesUseCase,
)

__all__ = [
    "BatchDiscoveryQuery",
    "BatchSource",
    "ConcatMasterUseCase",
    "DeduplicationReport",
    "DiscoverAtomicInventoryUseCase",
    "DiscoverBatchSourcesUseCase",
    "DuplicateCluster",
    "ExpandLongitudinalSynchronicUseCase",
    "FillGapsFluidProseUseCase",
    "IndexRawTranscriptsUseCase",
    "IngestRawTranscriptUseCase",
    "ReconcileMOCsUseCase",
    "SyncChannelUseCase",
    "SynthesizeAtomicBatchUseCase",
    "UnifyDuplicateNotesUseCase",
]
