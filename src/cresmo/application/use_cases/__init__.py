"""Use Cases for the Cresmo Knowledge Synthesis pipeline.

Core domain orchestration use cases:
- IngestRawTranscriptUseCase (Media ingestion and audio transcription)
- IndexRawTranscriptsUseCase (Catalog conceptual indexing and LLM-as-a-judge quality loops)  # FUTURE / DEFERRED
- ExpandCompendiumUseCase (Braudelian longue durée and Jaspers synchronic expansion)  # FUTURE / DEFERRED
- DiscoverAtomicInventoryUseCase (Holistic candidate entity inventory discovery)  # FUTURE / DEFERRED
- SynthesizeAtomicBatchUseCase (Batched atomic note synthesis and causal matrix modeling)  # FUTURE / DEFERRED
- ReconcileMOCsUseCase (Thematic Map of Content graph clustering and reconciliation)  # FUTURE / DEFERRED
- UnifyDuplicateNotesUseCase (Graph entity resolution, deduplication, and link rewriting)
"""

from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
from cresmo.application.use_cases.discover_atomic_inventory import (  # FUTURE / DEFERRED
    DiscoverAtomicInventoryUseCase,
    is_valid_inventory_json_structure,
)
from cresmo.application.use_cases.discovery import (
    BatchDiscoveryQuery,
    BatchSource,
    DiscoverBatchSourcesUseCase,
)
from cresmo.application.use_cases.expand_compendium import (  # FUTURE / DEFERRED
    ExpandCompendiumUseCase,
)
from cresmo.application.use_cases.indexing import (  # FUTURE / DEFERRED
    IndexRawTranscriptsUseCase,
)
from cresmo.application.use_cases.ingest_raw_transcript import (
    IngestRawTranscriptUseCase,
)
from cresmo.application.use_cases.reconcile_mocs import (  # FUTURE / DEFERRED
    ReconcileMOCsUseCase,
)
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.synthesize_atomic_batch import (  # FUTURE / DEFERRED
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
    "ExpandCompendiumUseCase",
    "IndexRawTranscriptsUseCase",
    "IngestRawTranscriptUseCase",
    "ReconcileMOCsUseCase",
    "SyncChannelUseCase",
    "SynthesizeAtomicBatchUseCase",
    "UnifyDuplicateNotesUseCase",
    "is_valid_inventory_json_structure",
]
