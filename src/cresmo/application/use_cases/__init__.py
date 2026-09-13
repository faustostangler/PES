"""Use Cases for the Cresmo Knowledge Synthesis pipeline.

Organized across the 6 incremental integer stages:
- Stage 1: IngestRawTranscriptUseCase
- Stage 2: FillGapsFluidProseUseCase
- Stage 3: ExpandLongitudinalSynchronicUseCase
- Stage 4: DiscoverAtomicInventoryUseCase
- Stage 5: SynthesizeAtomicBatchUseCase
- Stage 6: ReconcileMOCsUseCase
"""

from cresmo.application.use_cases.discover_atomic_inventory import (
    DiscoverAtomicInventoryUseCase,
)
from cresmo.application.use_cases.expand_longitudinal_synchronic import (
    ExpandLongitudinalSynchronicUseCase,
)
from cresmo.application.use_cases.fill_gaps_fluid_prose import FillGapsFluidProseUseCase
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
    "DeduplicationReport",
    "DiscoverAtomicInventoryUseCase",
    "DuplicateCluster",
    "ExpandLongitudinalSynchronicUseCase",
    "FillGapsFluidProseUseCase",
    "IngestRawTranscriptUseCase",
    "ReconcileMOCsUseCase",
    "SyncChannelUseCase",
    "SynthesizeAtomicBatchUseCase",
    "UnifyDuplicateNotesUseCase",
]
