"""Domain Value Objects for the Cresmo Knowledge Synthesis Bounded Context.

Implements immutable, self-validating Value Objects adhering to the Doctor Stangler Method
(Zero Primitive Obsession, construction-time invariant enforcement).

Conforms to:
- SPEC-001: §2.1 (Domain Invariants & Value Object Contracts)
- SPEC-003: §2 (Channel Sync Models & Normalization Rules)
- ADR-001 (Modular Monolith Domain Integrity)
"""

from __future__ import annotations

from cresmo.domain.value_objects.constants import (
    DEFAULT_LANGUAGE,
    EXTRA_INFO_HEADING_PATTERN,
    MAX_CHANNEL_ID_LENGTH,
    MAX_CHANNEL_NAME_LENGTH,
    MAX_CONTENT_ID_LENGTH,
    MAX_NOTE_TITLE_LENGTH,
    MIN_CANONICAL_CHANNEL_ID_LENGTH,
    MIN_CHANNEL_ID_LENGTH,
    MIN_CONTENT_ID_LENGTH,
    RESERVED_DERIVED_DIRS,
    RESERVED_SYSTEM_FILENAMES,
    TITLE_H1_PATTERN,
    is_processable_transcript_file,
)
from cresmo.domain.value_objects.convergence import (
    ConvergenceMode,
    SaturationPolicy,
    SaturationReason,
    SaturationThresholds,
    SaturationVerdict,
    never_saturate,
)
from cresmo.domain.value_objects.identity import (
    BatchId,
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    SourceModality,
)
from cresmo.domain.value_objects.ledger import (
    LedgerEntry,
    MasterDocumentResult,
    RawIndexEntry,
)
from cresmo.domain.value_objects.media import (
    DEFAULT_FEED_LOOKBACK_DAYS,
    DEFAULT_FEED_MAX_VIDEOS,
    ChannelFeedQuery,
    DiscoveredMediaItem,
    MediaProvenance,
    PipelineStatus,
    normalize_to_uploads_playlist_url,
)
from cresmo.domain.value_objects.notes import (
    AtomicEntityInventory,
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)
from cresmo.domain.value_objects.policies import (
    CompendiumRolloverPolicy,
    DiscoveryPolicy,
    StageExecutionPolicy,
)
from cresmo.domain.value_objects.prompt import (
    ChatMessage,
    ChatPrompt,
    MessageRole,
    PromptKey,
)
from cresmo.domain.value_objects.quality import (
    DEFAULT_FLUID_PROSE_WEIGHTS,
    DEFAULT_MECHANICAL_VETO_CRITERIA,
    GAP_FILLER_CANONICAL_WEIGHTS,
    GAP_FILLER_MECHANICAL_VETO_CRITERIA,
    LONG_EXPANDER_CANONICAL_WEIGHTS,
    LONG_EXPANDER_MECHANICAL_VETO_CRITERIA,
    WIDE_EXPANDER_CANONICAL_WEIGHTS,
    WIDE_EXPANDER_MECHANICAL_VETO_CRITERIA,
    CandidateText,
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
    StageEvaluationSpec,
    compute_composite_verdict,
    resolve_stage_scoring_policy,
)
from cresmo.domain.value_objects.sync import (
    SyncFilterCriteria,
    SyncSummary,
)

__all__ = [
    "DEFAULT_FEED_LOOKBACK_DAYS",
    "DEFAULT_FEED_MAX_VIDEOS",
    "DEFAULT_FLUID_PROSE_WEIGHTS",
    "DEFAULT_LANGUAGE",
    "DEFAULT_MECHANICAL_VETO_CRITERIA",
    "EXTRA_INFO_HEADING_PATTERN",
    "GAP_FILLER_CANONICAL_WEIGHTS",
    "GAP_FILLER_MECHANICAL_VETO_CRITERIA",
    "LONG_EXPANDER_CANONICAL_WEIGHTS",
    "LONG_EXPANDER_MECHANICAL_VETO_CRITERIA",
    "MAX_CHANNEL_ID_LENGTH",
    "MAX_CHANNEL_NAME_LENGTH",
    "MAX_CONTENT_ID_LENGTH",
    "MAX_NOTE_TITLE_LENGTH",
    "MIN_CANONICAL_CHANNEL_ID_LENGTH",
    "MIN_CHANNEL_ID_LENGTH",
    "MIN_CONTENT_ID_LENGTH",
    "RESERVED_DERIVED_DIRS",
    "RESERVED_SYSTEM_FILENAMES",
    "TITLE_H1_PATTERN",
    "WIDE_EXPANDER_CANONICAL_WEIGHTS",
    "WIDE_EXPANDER_MECHANICAL_VETO_CRITERIA",
    "AtomicEntityInventory",
    "BatchId",
    "CandidateText",
    "CausalMatrix",
    "Channel",
    "ChannelFeedQuery",
    "ChannelId",
    "ChannelName",
    "ChatMessage",
    "ChatPrompt",
    "CompendiumRolloverPolicy",
    "Content",
    "ContentId",
    "ConvergenceMode",
    "CriterionScore",
    "CrossContextRelations",
    "DiscoveredMediaItem",
    "DiscoveryPolicy",
    "EvaluationContext",
    "JudgeCriterion",
    "JudgeEvaluation",
    "LedgerEntry",
    "MasterDocumentResult",
    "MediaProvenance",
    "MessageRole",
    "NoteTitle",
    "NoteType",
    "PipelineStatus",
    "PromptKey",
    "RawIndexEntry",
    "SaturationPolicy",
    "SaturationReason",
    "SaturationThresholds",
    "SaturationVerdict",
    "SourceModality",
    "StageEvaluationSpec",
    "StageExecutionPolicy",
    "SyncFilterCriteria",
    "SyncSummary",
    "compute_composite_verdict",
    "is_processable_transcript_file",
    "never_saturate",
    "normalize_to_uploads_playlist_url",
    "resolve_stage_scoring_policy",
]
