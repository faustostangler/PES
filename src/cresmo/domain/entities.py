"""Domain Entities and Aggregates for the Cresmo Knowledge Synthesis Bounded Context.

Enforces business invariants strictly at construction time ("Always Valid State").
Zero persistence models or external framework dependencies in this layer.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001 (Modular Monolith Domain Integrity)
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass

from cresmo.domain.exceptions import (
    CompendiumStructureError,
    DomainValidationError,
    SelfReferentialRelationError,
)
from cresmo.domain.value_objects import (
    CausalMatrix,
    ChannelId,
    ChannelName,
    ContentId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)

# Regex matching Markdown tables (| header | header | \n | --- | --- |)
_TABLE_PATTERN = re.compile(r"\|.*\|.*\n\|[\s:-]+\|", re.MULTILINE)


@dataclass(frozen=True)
class RawTranscript:
    """Stage 1 Aggregate: Verbatim spoken transcript and origin metadata.

    Encapsulates raw audio transcription or native subtitle text alongside channel provenance.

    Attributes:
        content_id: Strongly-typed canonical media identifier.
        channel_name: Human-readable creator or source channel name (ChannelName Value Object).
        body: Verbatim text of spoken audio.
        title: Optional original video title.
        source_url: Canonical web URL.
        publication_date: Optional release date.
        upload_date: Backward-compatible alias for publication_date.
        channel_id: Optional platform channel ID.
        channel_category: Macro topic classification.
        video_description: Raw creator description text.

    Invariants:
        channel_name cannot be whitespace or empty (enforced by ChannelName).
        body cannot be whitespace or empty (pure audio silence is rejected per SPEC-001: §2.2).
    """

    content_id: ContentId
    channel_name: ChannelName
    body: str
    title: str = ""
    source_url: str = ""
    publication_date: datetime.date | None = None
    upload_date: datetime.date | None = None
    channel_id: ChannelId | None = None
    channel_category: str = ""
    video_description: str = ""

    def __post_init__(self) -> None:
        # Coerce channel_name to strongly-typed ChannelName Value Object (ADR-019)
        cn = (
            self.channel_name
            if isinstance(self.channel_name, ChannelName)
            else ChannelName.from_string(self.channel_name)
        )
        object.__setattr__(self, "channel_name", cn)

        if self.channel_id is not None and not isinstance(self.channel_id, ChannelId):
            object.__setattr__(self, "channel_id", ChannelId.from_string(self.channel_id))

        # Unify publication_date and upload_date semantics
        pub_date = self.publication_date or self.upload_date
        object.__setattr__(self, "publication_date", pub_date)
        object.__setattr__(self, "upload_date", pub_date)

        # Invariant checks ensuring audio transcription payload is valid
        if not self.body.strip():
            raise DomainValidationError("RawTranscript body cannot be empty or whitespace.")


@dataclass(frozen=True)
class EnrichedCompendium:
    """Stage 2 & 3 Aggregate: Multi-pass enriched fluid prose compendium.

    Represents dense formal prose expanded via Socratic gap-filling (Stage 2) and
    Braudelian longitudinal/Jaspers synchronic cross-sections (Stage 3).

    Attributes:
        content_id: Strongly-typed canonical media identifier.
        channel_name: Origin source channel name (ChannelName Value Object).
        title: Validated NoteTitle of the compendium.
        body: Continuous fluid prose main narrative.
        complementary_info: Encyclopedic context, dates, mini-biographies, and secondary details.
        pass_count: Number of enrichment passes executed (must be >= 1).
        channel_id: Optional platform channel ID.
        channel_category: Macro topic classification.
        source_url: Origin web URL.
        publication_date: Optional release date (datetime.date).
        video_date: Backward-compatible timestamp string.
        video_description: Original creator description.

    Invariants:
        Per SPEC-001: §2.2 and cresmo-style-guide:
        1. body cannot be empty and MUST be continuous prose.
        2. Markdown tables are strictly forbidden in body to preserve narrative density.
        3. complementary_info must be populated (mandating the '## Informações Complementares' section).
        4. pass_count must be at least 1.
    """

    content_id: ContentId
    channel_name: ChannelName
    title: NoteTitle
    body: str
    complementary_info: str
    pass_count: int = 1
    channel_id: ChannelId | None = None
    channel_category: str = ""
    source_url: str = ""
    publication_date: datetime.date | None = None
    video_date: str = ""
    video_description: str = ""

    def __post_init__(self) -> None:
        cn = (
            self.channel_name
            if isinstance(self.channel_name, ChannelName)
            else ChannelName.from_string(self.channel_name)
        )
        object.__setattr__(self, "channel_name", cn)

        if self.channel_id is not None and not isinstance(self.channel_id, ChannelId):
            object.__setattr__(self, "channel_id", ChannelId.from_string(self.channel_id))

        # Harmonize publication_date and video_date
        pub_date = self.publication_date
        if pub_date is None and self.video_date:
            try:
                raw_d = self.video_date.strip()
                if raw_d:
                    pub_date = datetime.date.fromisoformat(raw_d[:10])
            except (ValueError, TypeError):
                pub_date = None
        v_date = self.video_date or (pub_date.isoformat() if pub_date else "")
        object.__setattr__(self, "publication_date", pub_date)
        object.__setattr__(self, "video_date", v_date)

        b = self.body.strip()
        ci = self.complementary_info.strip()

        if not b:
            raise CompendiumStructureError("EnrichedCompendium body cannot be empty.")
        if not ci:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )
        # Structural invariant: reject Markdown tables in primary fluid prose
        if _TABLE_PATTERN.search(b):
            raise CompendiumStructureError(
                "EnrichedCompendium body must be continuous prose and cannot contain Markdown tables."
            )
        if self.pass_count < 1:
            raise CompendiumStructureError("pass_count must be at least 1.")


@dataclass(frozen=True)
class AtomicNote:
    """Stage 4 & 5 Aggregate: Self-contained semantic unit in the Second Brain vault.

    Encapsulates an autonomous concept, entity, event, or dynamic process formatted
    as an Obsidian Markdown note with bidirectional WikiLinks.

    Attributes:
        title: Unique, validated note title.
        note_type: Canonical typology classification (concept, entity, event, process).
        definition: Dense contextual analysis and synthesis (minimum 20 characters).
        content_tags: Associated thematic tags.
        domain: Primary knowledge domain.
        cluster: Thematic cluster or subfield.
        source: Provenance reference link or compendium title.
        aliases: Alternative terminology or synonyms.
        direct_relations: Sequence of related NoteTitles (triples).
        causal_matrix: Optional ternary causality model (cause, effect, attribution).
        cross_context: Optional historical/lateral/consequential triad.

    Invariants:
        1. definition length must be >= 20 characters (rejects vacuous stubs per SPEC-001: §2.2).
        2. title cannot appear in direct_relations (prevents self-referential graph cycles).
    """

    title: NoteTitle
    note_type: NoteType
    definition: str
    content_tags: tuple[str, ...] = ()
    domain: str = ""
    cluster: str = ""
    source: str = ""
    aliases: tuple[str, ...] = ()
    direct_relations: tuple[NoteTitle, ...] = ()
    causal_matrix: CausalMatrix | None = None
    cross_context: CrossContextRelations | None = None

    def __post_init__(self) -> None:
        d = self.definition.strip()
        if len(d) < 20:
            raise DomainValidationError(
                f"AtomicNote definition must contain at least 20 characters of contextual analysis. Got: '{d}'"
            )

        # Graph invariant: enforce acyclic direct relations (no self-loops)
        title_key = self.title.value.lower()
        for rel in self.direct_relations:
            if rel.value.lower() == title_key:
                raise SelfReferentialRelationError(
                    f"AtomicNote '{self.title.value}' cannot contain itself in direct_relations."
                )


@dataclass(frozen=True)
class MapOfContent:
    """Stage 6 Aggregate: Synthesis node reconciling clusters of Atomic Notes.

    Functions as an index anchor (MOC) in the Obsidian vault, organizing
    autonomous atomic notes into coherent thematic hierarchies with zero orphaned notes.

    Attributes:
        title: Validated MOC note title.
        theme: Macro epistemic subject or cluster name.
        overview: Synthetic prose framing the structural relationships of member notes.
        associated_notes: Non-empty sequence of validated NoteTitles.

    Invariants:
        1. associated_notes cannot be empty.
        2. associated_notes cannot contain duplicate titles (case-insensitive).
    """

    title: NoteTitle
    theme: str
    overview: str
    associated_notes: tuple[NoteTitle, ...]

    def __post_init__(self) -> None:
        if not self.associated_notes:
            raise DomainValidationError("MapOfContent must contain at least one associated note.")

        # Invariant check: prevent duplicate node entries in MOC graph
        seen: set[str] = set()
        for note in self.associated_notes:
            key = note.value.lower()
            if key in seen:
                raise DomainValidationError(
                    f"Duplicate associated note '{note.value}' in MapOfContent."
                )
            seen.add(key)


@dataclass(frozen=True)
class PipelineSessionId:
    """Value Object representing the holistic multi-stage content lifecycle session.

    Conforms to ADR-016. Ensures end-to-end Session Replay in Langfuse across all 6 stages.
    Format: content:{channel}:{content_id}
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) != 3 or parts[0] != "content" or not parts[1] or not parts[2]:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected 'content:{channel}:{content_id}'."
            )

    @classmethod
    def create(cls, channel: ChannelName, content_id: ContentId) -> PipelineSessionId:
        ch = channel.value if isinstance(channel, ChannelName) else str(channel).strip()
        c_id = content_id.value if isinstance(content_id, ContentId) else str(content_id).strip()
        return cls(value=f"content:{ch}:{c_id}")

    @property
    def channel_name(self) -> str:
        return self.value.split(":")[1]

    @property
    def content_id(self) -> str:
        return self.value.split(":")[2]


@dataclass(frozen=True)
class ChannelTenantId:
    """Value Object representing the source channel as cost center / tenant.

    Conforms to ADR-016. Maps the channel as the primary user entity in Langfuse for FinOps.
    Format: channel:{channel_name}
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("ChannelTenantId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) != 2 or parts[0] != "channel" or not parts[1]:
            raise ValueError(
                f"Invalid ChannelTenantId format: '{self.value}'. "
                "Expected 'channel:{channel_name}'."
            )

    @classmethod
    def create(cls, channel: ChannelName) -> ChannelTenantId:
        ch = channel.value if isinstance(channel, ChannelName) else str(channel).strip()
        return cls(value=f"channel:{ch}")

    @property
    def channel_name(self) -> str:
        return self.value.split(":")[1]


@dataclass(frozen=True)
class UserIdentity:
    """Value Object representing the user/operator executing the synthesis pipeline.

    Supports forward-compatible identity modalities:
    - Anonymous (unauthenticated, guest, CLI)
    - Identified (authenticated via OAuth/OIDC login)
    - Channel fallback (headless background worker pipelines)

    Conforms to ADR-016 and Langfuse Users taxonomy.
    """

    value: str
    is_anonymous: bool = True
    provider: str = "anonymous"
    subject: str = ""

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("UserIdentity cannot be empty.")

    @classmethod
    def anonymous(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        val = f"anon:{token}" if token else "anonymous"
        return cls(value=val, is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def identified(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        prov = provider.strip().lower() or "oauth"
        val = f"user:{prov}:{subject.strip()}"
        return cls(value=val, is_anonymous=False, provider=prov, subject=subject.strip())

    @classmethod
    def from_channel(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )


@dataclass(frozen=True)
class JudgeFrictionMetric:
    """Value Object calculating LLM-as-a-judge retry friction per ADR-013 & ADR-016.

    Friction ratio = (iterations - 1) / (max_iterations - 1).
    0.0 = perfect first pass; 1.0 = all retries exhausted.
    """

    iterations: int
    max_iterations: int
    verdict: str

    def __post_init__(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    @property
    def friction_ratio(self) -> float:
        if self.iterations <= 1 or self.max_iterations <= 1:
            return 0.0
        return min(1.0, (self.iterations - 1) / (self.max_iterations - 1))
