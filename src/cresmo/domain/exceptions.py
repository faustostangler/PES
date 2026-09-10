"""Domain exceptions for the Cresmo Knowledge Synthesis context.

Enforces fail-fast domain boundary errors when construction invariants are violated.
"""

from __future__ import annotations


class CresmoDomainError(Exception):
    """Base exception for all domain invariant and business rule violations."""


class DomainValidationError(CresmoDomainError):
    """Raised when an Entity or Value Object receives data violating construction invariants."""


class NoteTypologyError(CresmoDomainError):
    """Raised when an invalid note typology classification is supplied."""


class SelfReferentialRelationError(CresmoDomainError):
    """Raised when an Atomic Note includes itself in its direct relations."""


class CompendiumStructureError(CresmoDomainError):
    """Raised when an Enriched Compendium lacks continuous prose or complementary information."""


class RateLimitExceededError(CresmoDomainError):
    """Raised when an upstream media source or LLM returns HTTP 429 rate limit."""


class IngestionNetworkError(CresmoDomainError):
    """Raised when media crawling or download fails due to network/transcription errors."""
