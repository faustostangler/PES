"""Domain Value Objects for Pass Convergence and Hybrid Semantic Saturation.

Conforms to:
    - ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters
    - SPEC-066: §2.2 (Convergence Value Objects)
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from cresmo.domain.exceptions import DomainValidationError


def _validate_unit_float(value: float, field_name: str, *, allow_zero: bool) -> None:
    """Validate finite non-boolean numeric value within (0.0, 1.0] or [0.0, 1.0]."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DomainValidationError(f"{field_name} must be a finite float, got {value!r}.")
    if not math.isfinite(value):
        raise DomainValidationError(f"{field_name} must be finite, got {value!r}.")
    if allow_zero:
        if not (0.0 <= value <= 1.0):
            raise DomainValidationError(f"{field_name} must be within [0.0, 1.0], got {value!r}.")
    elif not (0.0 < value <= 1.0):
        raise DomainValidationError(f"{field_name} must be within (0.0, 1.0], got {value!r}.")


def _validate_non_negative_int(value: int, field_name: str) -> None:
    """Validate non-boolean integer >= 0."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DomainValidationError(f"{field_name} must be a non-negative integer, got {value!r}.")


class ConvergenceMode(StrEnum):
    """Declarative convergence evaluation strategy for multi-pass synthesis stages."""

    NONE = "none"
    HYBRID_SEMANTIC = "hybrid_semantic"


class SaturationReason(StrEnum):
    """Canonical termination or continuation reason returned by convergence evaluation."""

    DISABLED = "disabled"
    EXPLICIT_SENTINEL = "explicit_sentinel"
    LEXICAL_IDENTITY = "lexical_identity"
    SEMANTIC_PLATEAU = "semantic_plateau"
    NOVEL_CONTENT = "novel_content"


@dataclass(frozen=True, slots=True)
class SaturationThresholds:
    """Immutable threshold bundle governing lexical and semantic convergence evaluation.

    Attributes:
        lexical_identity_threshold: Minimum n-gram Jaccard similarity for lexical short-circuit.
        max_lexical_word_delta: Maximum relative word-count delta allowed for lexical short-circuit.
        semantic_similarity_threshold: Minimum cosine similarity to consider a unit semantically covered.
        max_novel_paragraphs_for_saturation: Maximum count of novel units tolerated while still saturated.
    """

    lexical_identity_threshold: float = 0.95
    max_lexical_word_delta: float = 0.03
    semantic_similarity_threshold: float = 0.88
    max_novel_paragraphs_for_saturation: int = 0

    def __post_init__(self) -> None:
        """Enforce construction-time numerical bounds and type invariants."""
        _validate_unit_float(
            self.lexical_identity_threshold,
            "lexical_identity_threshold",
            allow_zero=False,
        )
        _validate_unit_float(
            self.max_lexical_word_delta,
            "max_lexical_word_delta",
            allow_zero=True,
        )
        _validate_unit_float(
            self.semantic_similarity_threshold,
            "semantic_similarity_threshold",
            allow_zero=False,
        )
        _validate_non_negative_int(
            self.max_novel_paragraphs_for_saturation,
            "max_novel_paragraphs_for_saturation",
        )


@dataclass(frozen=True, slots=True)
class SaturationVerdict:
    """Immutable convergence evaluation verdict guiding loop termination and baseline retention.

    Attributes:
        is_saturated: Whether the pass converged and iterative refinement may halt.
        reason: Canonical classification explaining why saturation occurred or continued.
        lexical_jaccard: Computed n-gram Jaccard similarity in [0.0, 1.0].
        word_delta_ratio: Relative word-count delta ratio in [0.0, 1.0].
        max_novelty: Maximum unit-level semantic novelty observed in [0.0, 1.0].
        novel_paragraphs: Number of candidate units falling below semantic similarity threshold.
        total_paragraphs: Total number of segmented candidate semantic units.
        preserve_baseline: Whether caller must restore baseline_text instead of keeping candidate output.
        provider: Identifier of the layer or embedding backend that produced the verdict.
    """

    is_saturated: bool
    reason: SaturationReason
    lexical_jaccard: float
    word_delta_ratio: float
    max_novelty: float = 1.0
    novel_paragraphs: int = 0
    total_paragraphs: int = 0
    preserve_baseline: bool = False
    provider: str = ""

    def __post_init__(self) -> None:
        """Enforce scalar domain bounds and cross-field verdict invariants."""
        if not isinstance(self.is_saturated, bool):
            raise DomainValidationError(f"is_saturated must be a bool, got {self.is_saturated!r}.")
        if not isinstance(self.preserve_baseline, bool):
            raise DomainValidationError(
                f"preserve_baseline must be a bool, got {self.preserve_baseline!r}."
            )
        if not isinstance(self.reason, SaturationReason):
            raise DomainValidationError(f"reason must be a SaturationReason, got {self.reason!r}.")
        if not isinstance(self.provider, str):
            raise DomainValidationError(f"provider must be a str, got {self.provider!r}.")

        _validate_unit_float(self.lexical_jaccard, "lexical_jaccard", allow_zero=True)
        _validate_unit_float(self.word_delta_ratio, "word_delta_ratio", allow_zero=True)
        _validate_unit_float(self.max_novelty, "max_novelty", allow_zero=True)
        _validate_non_negative_int(self.novel_paragraphs, "novel_paragraphs")
        _validate_non_negative_int(self.total_paragraphs, "total_paragraphs")

        if self.novel_paragraphs > self.total_paragraphs:
            raise DomainValidationError(
                f"novel_paragraphs ({self.novel_paragraphs}) cannot exceed "
                f"total_paragraphs ({self.total_paragraphs})."
            )

        if self.reason in (
            SaturationReason.DISABLED,
            SaturationReason.NOVEL_CONTENT,
        ) and (self.is_saturated or self.preserve_baseline):
            raise DomainValidationError(
                f"Non-saturated reason '{self.reason.value}' requires "
                "is_saturated=False and preserve_baseline=False."
            )
        if (
            self.reason
            in (
                SaturationReason.EXPLICIT_SENTINEL,
                SaturationReason.LEXICAL_IDENTITY,
                SaturationReason.SEMANTIC_PLATEAU,
            )
            and not self.is_saturated
        ):
            raise DomainValidationError(
                f"Saturated reason '{self.reason.value}' requires is_saturated=True."
            )

    def to_metadata_dict(self) -> dict[str, Any]:
        """Serialize verdict fields into a JSON-compatible dictionary for telemetry and metadata.

        Returns:
            dict[str, Any]: Scalar verdict attributes suitable for trace spans and candidate metadata.
        """
        return {
            "is_saturated": self.is_saturated,
            "reason": str(self.reason.value),
            "lexical_jaccard": float(self.lexical_jaccard),
            "word_delta_ratio": float(self.word_delta_ratio),
            "max_novelty": float(self.max_novelty),
            "novel_paragraphs": self.novel_paragraphs,
            "total_paragraphs": self.total_paragraphs,
            "preserve_baseline": self.preserve_baseline,
            "provider": self.provider,
        }


SaturationPolicy = Callable[[str, str, int], SaturationVerdict]


def never_saturate(
    baseline_text: str,
    current_text: str,
    pass_index: int = 1,
) -> SaturationVerdict:
    """Return a disabled convergence verdict that never terminates multi-pass refinement early.

    Args:
        baseline_text: Reference baseline text from source or prior pass.
        current_text: Newly generated candidate text from the current pass.
        pass_index: One-based pass number being evaluated.

    Returns:
        SaturationVerdict: Disabled verdict indicating refinement should continue.
    """
    return SaturationVerdict(
        is_saturated=False,
        reason=SaturationReason.DISABLED,
        lexical_jaccard=0.0,
        word_delta_ratio=0.0,
        max_novelty=1.0,
        novel_paragraphs=0,
        total_paragraphs=0,
        preserve_baseline=False,
        provider="disabled",
    )
