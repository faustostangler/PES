"""Unit tests validating Polyfactory domain aggregate generators."""

from __future__ import annotations

from cresmo.application.use_cases.discovery.models import BatchSource
from cresmo.domain.entities.compendium import EnrichedCompendium
from cresmo.domain.entities.transcripts import SourceTranscript
from cresmo.domain.value_objects import LedgerEntry, PipelineStatus, SourceModality
from tests.factories import (
    BatchSourceFactory,
    EnrichedCompendiumFactory,
    LedgerEntryFactory,
    SourceTranscriptFactory,
)


def test_batch_source_factory() -> None:
    """Verify that BatchSourceFactory generates valid BatchSource instances."""
    batch_source = BatchSourceFactory.build()
    assert isinstance(batch_source, BatchSource)
    assert batch_source.kind in (SourceModality.URL, SourceModality.FILE)
    assert batch_source.content_id is not None
    assert batch_source.target != ""


def test_source_transcript_factory() -> None:
    """Verify that SourceTranscriptFactory generates valid SourceTranscript aggregates."""
    transcript = SourceTranscriptFactory.build()
    assert isinstance(transcript, SourceTranscript)
    assert transcript.channel.name != ""
    assert transcript.content.body != ""
    assert transcript.provenance.url != ""


def test_enriched_compendium_factory() -> None:
    """Verify that EnrichedCompendiumFactory honors domain invariants."""
    compendium = EnrichedCompendiumFactory.build()
    assert isinstance(compendium, EnrichedCompendium)
    assert compendium.pass_count >= 1
    assert compendium.body != ""
    assert "|" not in compendium.body or "---" not in compendium.body
    assert "Informações Complementares" in compendium.complementary_info


def test_ledger_entry_factory() -> None:
    """Verify that LedgerEntryFactory generates immutable LedgerEntry value objects."""
    entry = LedgerEntryFactory.build(status=PipelineStatus.COMPLETED)
    assert isinstance(entry, LedgerEntry)
    assert entry.status == PipelineStatus.COMPLETED
    assert entry.content_id.value != ""
    assert entry.started_at is not None
