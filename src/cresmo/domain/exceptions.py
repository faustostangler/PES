"""Domain and Boundary Exceptions for the Cresmo Knowledge Synthesis Bounded Context.

Enforces fail-fast boundary protection and Hexagonal isolation per ADR-001.
Domain invariant violations inherit strictly from CresmoDomainError, ensuring
zero coupling to external HTTP frameworks, databases, or runtime drivers.

Conforms to SPEC-001: §2 (Core Domain Invariants & Exception Hierarchy).
"""

from __future__ import annotations


class CresmoDomainError(Exception):
    """Base domain exception for all invariant, business rule, and ontology violations.

    All business rule exceptions raised in the domain layer inherit from this class,
    allowing application and presentation layers to catch pure domain failures.
    """


class DomainValidationError(CresmoDomainError, ValueError):
    """Raised when an Entity or Value Object receives data violating construction invariants.

    Ensures the 'Always Valid at Construction' principle (SPEC-001: §2.1).
    """


class NoteTypologyError(CresmoDomainError):
    """Raised when an invalid note typology classification is supplied.

    Enforces that note typologies map strictly to authorized Cresmo taxonomic
    categories (concept, entity, event, process) per SPEC-001: §2.1.
    """


class SelfReferentialRelationError(CresmoDomainError):
    """Raised when an Atomic Note includes itself in its direct relations.

    Preserves acyclic knowledge graph invariants by preventing self-loops (SPEC-001: §2.2).
    """


class CompendiumStructureError(CresmoDomainError):
    """Raised when an Enriched Compendium violates fluid prose structural invariants.

    Enforces continuous prose (rejection of raw tables or bullet lists) and the
    mandatory presence of the '## Informações Complementares' section per SPEC-001: §2.2.
    """


class CresmoInfrastructureError(Exception):
    """Base infrastructure exception for external adapters, I/O, and OS failures.

    Used by adapters to wrap low-level system errors (file locks, network timeouts)
    before propagating upwards through the Hexagonal architecture.
    """


class PreflightError(CresmoInfrastructureError):
    """Raised when runtime environment, directory layout, or configuration preflight fails.

    Prevents pipeline startup under invalid operational conditions (ADR-005).
    """


class SecurityViolationError(CresmoInfrastructureError):
    """Raised when a security boundary or filesystem path traversal constraint is violated.

    Prevents unauthorized directory escapes outside configured vault/data roots.
    """


class RateLimitExceededError(CresmoInfrastructureError, CresmoDomainError):
    """Raised when an upstream media source or LLM provider signals HTTP 429 rate limiting.

    Inherits from both Domain and Infrastructure errors to allow use cases to trigger
    retry backoffs or graceful throttling policies (SPEC-004 & EVAL-001).
    """


class IngestionNetworkError(CresmoInfrastructureError, CresmoDomainError):
    """Raised when media crawling, audio extraction, or transcription fails due to I/O errors.

    Indicates network timeouts, missing audio streams, or scraper failures (SPEC-004).
    """


class LLMInfrastructureError(CresmoInfrastructureError):
    """Raised when an external or local LLM inference call fails or becomes unreachable.

    Wraps provider-specific failures (e.g., Google GenAI or Ollama socket errors).
    """
