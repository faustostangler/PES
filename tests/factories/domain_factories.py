"""Polyfactory domain entity and value object test factories for Cresmo.

Eliminates brittle manual mocks by dynamically synthesizing strongly-typed
domain aggregates, entities, and value objects adhering to domain invariants.
"""

from __future__ import annotations

from datetime import UTC, datetime

from polyfactory.factories import DataclassFactory

from cresmo.application.use_cases.discovery.models import BatchSource
from cresmo.domain.entities.compendium import EnrichedCompendium
from cresmo.domain.entities.transcripts import SourceTranscript
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    LedgerEntry,
    MediaProvenance,
    NoteTitle,
    PipelineStatus,
    SourceModality,
)


class ContentIdFactory(DataclassFactory[ContentId]):
    """Factory generating strongly-typed ContentId value objects."""

    __model__ = ContentId

    @classmethod
    def value(cls) -> str:
        return f"vid_{cls.__faker__.hexify(text='^^^^^^^^^^')}"


class ChannelFactory(DataclassFactory[Channel]):
    """Factory generating strongly-typed Channel value objects."""

    __model__ = Channel

    @classmethod
    def id(cls) -> ChannelId:
        return ChannelId(f"UC_{cls.__faker__.hexify(text='^^^^^^^^^^^^')}")

    @classmethod
    def name(cls) -> str:
        return cls.__faker__.company()


class ContentFactory(DataclassFactory[Content]):
    """Factory generating Content value objects."""

    __model__ = Content

    @classmethod
    def id(cls) -> ContentId:
        return ContentId(f"vid_{cls.__faker__.hexify(text='^^^^^^^^^^')}")

    @classmethod
    def title(cls) -> str:
        return cls.__faker__.sentence(nb_words=4)

    @classmethod
    def body(cls) -> str:
        return cls.__faker__.paragraph(nb_sentences=3)


class BatchSourceFactory(DataclassFactory[BatchSource]):
    """Polyfactory generating BatchSource instances for ingestion and batch discovery."""

    __model__ = BatchSource

    @classmethod
    def kind(cls) -> SourceModality:
        return SourceModality.URL

    @classmethod
    def target(cls) -> str:
        cid = cls.__faker__.hexify(text="^^^^^^^^^^")
        return f"https://www.youtube.com/watch?v={cid}"

    @classmethod
    def content_id(cls) -> ContentId:
        return ContentId(f"vid_{cls.__faker__.hexify(text='^^^^^^^^^^')}")


class SourceTranscriptFactory(DataclassFactory[SourceTranscript]):
    """Polyfactory generating valid SourceTranscript domain aggregates."""

    __model__ = SourceTranscript

    @classmethod
    def channel(cls) -> Channel:
        return ChannelFactory.build()

    @classmethod
    def provenance(cls) -> MediaProvenance:
        return MediaProvenance(
            url=f"https://youtube.com/watch?v={cls.__faker__.hexify(text='^^^^^^^^^^')}",
            description="Sample transcript metadata",
            publication_date=datetime.now(UTC).date(),
        )

    @classmethod
    def content(cls) -> Content:
        return ContentFactory.build()


class EnrichedCompendiumFactory(DataclassFactory[EnrichedCompendium]):
    """Polyfactory generating valid EnrichedCompendium aggregates honoring all invariants.

    Invariants enforced:
    - Non-empty fluid prose body without markdown tables.
    - Non-empty complementary information section.
    - pass_count >= 1.
    """

    __model__ = EnrichedCompendium

    @classmethod
    def content_id(cls) -> ContentId:
        return ContentId(f"comp_{cls.__faker__.hexify(text='^^^^^^^^^^')}")

    @classmethod
    def channel_name(cls) -> ChannelName:
        return ChannelName(cls.__faker__.company())

    @classmethod
    def title(cls) -> NoteTitle:
        return NoteTitle(cls.__faker__.sentence(nb_words=5))

    @classmethod
    def body(cls) -> str:
        return (
            "Esta é uma narrativa contínua sem tabelas markdown, "
            "estruturada de acordo com os princípios da longa duração e rigor historiográfico."
        )

    @classmethod
    def complementary_info(cls) -> str:
        return "## Informações Complementares\nContexto histórico enciclopédico e notas prosopográficas."

    @classmethod
    def pass_count(cls) -> int:
        return 2


class LedgerEntryFactory(DataclassFactory[LedgerEntry]):
    """Polyfactory generating immutable LedgerEntry value objects."""

    __model__ = LedgerEntry

    @classmethod
    def content_id(cls) -> ContentId:
        return ContentId(f"ledg_{cls.__faker__.hexify(text='^^^^^^^^^^')}")

    @classmethod
    def media_url(cls) -> str:
        return f"https://youtube.com/watch?v={cls.__faker__.hexify(text='^^^^^^^^^^')}"

    @classmethod
    def title(cls) -> str:
        return cls.__faker__.sentence(nb_words=4)

    @classmethod
    def channel_name(cls) -> ChannelName:
        return ChannelName(cls.__faker__.company())

    @classmethod
    def status(cls) -> PipelineStatus:
        return PipelineStatus.COMPLETED

    @classmethod
    def notes_count(cls) -> int:
        return cls.__faker__.random_int(min=1, max=50)

    @classmethod
    def started_at(cls) -> datetime:
        return datetime.now(UTC)

    @classmethod
    def completed_at(cls) -> datetime:
        return datetime.now(UTC)
