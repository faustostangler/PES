"""EnrichedCompendium domain aggregate.

Conforms to:
- SPEC-001: §2.2 (Entities & Aggregates Lifecycle and Invariants)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass

from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import (
    ChannelId,
    ChannelName,
    ContentId,
    NoteTitle,
)

# Regex matching Markdown tables (| header | header | \n | --- | --- |)
_TABLE_PATTERN = re.compile(r"\|.*\|.*\n\|[\s:-]+\|", re.MULTILINE)


@dataclass(frozen=True)
class EnrichedCompendium:
    """EnrichedCompendium Aggregate: Multi-pass enriched fluid prose compendium.

    Represents dense formal prose expanded via Socratic gap-filling and
    Braudelian longitudinal/Jaspers synchronic cross-sections.

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
    channel_name: ChannelName | str
    title: NoteTitle
    body: str
    complementary_info: str
    pass_count: int = 1
    channel_id: ChannelId | str | None = None
    channel_category: str = ""
    source_url: str = ""
    publication_date: datetime.date | None = None
    video_date: str = ""
    video_description: str = ""

    def __post_init__(self) -> None:
        resolved_channel_name = (
            self.channel_name
            if isinstance(self.channel_name, ChannelName)
            else ChannelName.from_string(self.channel_name)
        )
        object.__setattr__(self, "channel_name", resolved_channel_name)

        if self.channel_id is not None and not isinstance(self.channel_id, ChannelId):
            object.__setattr__(self, "channel_id", ChannelId.from_string(self.channel_id))

        # Harmonize publication_date and video_date
        pub_date = self.publication_date
        if pub_date is None and self.video_date:
            try:
                raw_video_date = self.video_date.strip()
                if raw_video_date:
                    pub_date = datetime.date.fromisoformat(raw_video_date[:10])
            except (ValueError, TypeError):
                pub_date = None
        resolved_video_date = self.video_date or (pub_date.isoformat() if pub_date else "")
        object.__setattr__(self, "publication_date", pub_date)
        object.__setattr__(self, "video_date", resolved_video_date)

        cleaned_body = self.body.strip()
        cleaned_complementary_info = self.complementary_info.strip()

        if not cleaned_body:
            raise CompendiumStructureError("EnrichedCompendium body cannot be empty.")
        if not cleaned_complementary_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )
        # Structural invariant: reject Markdown tables in primary fluid prose
        if _TABLE_PATTERN.search(cleaned_body):
            raise CompendiumStructureError(
                "EnrichedCompendium body must be continuous prose and cannot contain Markdown tables."
            )
        if self.pass_count < 1:
            raise CompendiumStructureError("pass_count must be at least 1.")
