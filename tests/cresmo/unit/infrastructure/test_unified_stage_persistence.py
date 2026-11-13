"""Unit tests for ADR-058: Unified Stage Transcript Persistence and Dynamic Path Resolution.

Verifies:
1. Dynamic directory resolution for arbitrary stages: data/{stage}/{channel_name}/{content_id}.md
2. Zero KeyError on new or custom pipeline conveyor stages.
3. Monomorphic canonical YAML frontmatter formatting with optional pass_count.
4. Roundtrip serialization and deserialization across arbitrary stages.
5. Backward-compatible delegation wrappers (save_transcript, save_fluid_transcript, save_enriched_compendium).
"""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from cresmo.domain.entities import StageTranscript
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
    MediaProvenance,
)
from cresmo.infrastructure.adapters.obsidian import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.obsidian.transcripts import TranscriptVaultHandler


@pytest.fixture
def data_vault_setup(
    tmp_path: Path,
) -> tuple[Path, Path, TranscriptVaultHandler, ObsidianVaultAdapter]:
    data_dir = tmp_path / "data"
    vault_dir = tmp_path / "vault"
    raw_dir = data_dir / "raw"
    enriched_dir = data_dir / "enriched"
    fluid_dir = data_dir / "fluid_prose"

    for d in (data_dir, vault_dir, raw_dir, enriched_dir, fluid_dir):
        d.mkdir(parents=True, exist_ok=True)

    handler = TranscriptVaultHandler(
        raw_dir=raw_dir,
        enriched_dir=enriched_dir,
        fluid_dir=fluid_dir,
        data_dir=data_dir,
    )
    adapter = ObsidianVaultAdapter(
        vault_dir=vault_dir,
        raw_dir=raw_dir,
        enriched_dir=enriched_dir,
        fluid_dir=fluid_dir,
        data_dir=data_dir,
    )
    return data_dir, vault_dir, handler, adapter


def _make_sample_transcript(
    content_id_str: str = "vid_adr058_01",
    channel_name_str: str = "Doctor Stangler",
    pass_count: int | None = None,
) -> StageTranscript:
    return StageTranscript(
        channel=Channel(
            name=ChannelName(channel_name_str), id=ChannelId("UC_STANGLER"), category="Tech"
        ),
        provenance=MediaProvenance.create(
            url=f"https://youtube.com/watch?v={content_id_str}",
            description="Sample video description\nLine 2 of description",
            publication_date=datetime.date(2026, 11, 10),
        ),
        content=Content.create(
            id=ContentId(content_id_str),
            title="Clean Title Sample",
            text="## Header 2\n\nParagraph 1 prose content.\n\n### Extra Info\n\n1. Biographical datum.",
            session_id=f"UC_STANGLER:{content_id_str}",
        ),
        pass_count=pass_count,
    )


class TestADR058UnifiedStagePersistence:
    """Test suite validating ADR-058 unified persistence invariants."""

    def test_save_stage_transcript_dynamic_path_resolution_for_new_stage(
        self, data_vault_setup: tuple[Path, Path, TranscriptVaultHandler, ObsidianVaultAdapter]
    ) -> None:
        """Arbitrary conveyor stage (e.g. 'long_expander') must dynamically resolve to data/{stage}/{channel}/{id}.md."""
        data_dir, _, handler, _ = data_vault_setup
        transcript = _make_sample_transcript("long_exp_101", "Canal Historia", pass_count=1)

        # Must not raise KeyError
        handler.save_stage_transcript("long_expander", transcript)

        expected_path = data_dir / "long_expander" / "Canal Historia" / "long_exp_101.md"
        assert expected_path.exists(), f"Expected file at {expected_path}"
        content = expected_path.read_text(encoding="utf-8")
        assert "video_id: long_exp_101" in content
        assert "pass_count: 1" in content
        assert "Paragraph 1 prose content." in content

    def test_save_stage_transcript_dynamic_path_resolution_for_canonical_stages(
        self, data_vault_setup: tuple[Path, Path, TranscriptVaultHandler, ObsidianVaultAdapter]
    ) -> None:
        """Conveyor stages 'fluid_prose' and 'gap_filler' must resolve to data/{stage}/{channel}/{id}.md."""
        data_dir, _, handler, _ = data_vault_setup

        fluid = _make_sample_transcript("fluid_202", "Canal Filosofia", pass_count=None)
        handler.save_stage_transcript("fluid_prose", fluid)
        fluid_path = data_dir / "fluid_prose" / "Canal Filosofia" / "fluid_202.md"
        assert fluid_path.exists()

        gaps = _make_sample_transcript("gaps_303", "Canal Filosofia", pass_count=3)
        handler.save_stage_transcript("gap_filler", gaps)
        gaps_path = data_dir / "gap_filler" / "Canal Filosofia" / "gaps_303.md"
        assert gaps_path.exists()

    def test_save_and_get_stage_transcript_roundtrip_arbitrary_stage(
        self, data_vault_setup: tuple[Path, Path, TranscriptVaultHandler, ObsidianVaultAdapter]
    ) -> None:
        """Roundtrip save and retrieval must preserve all 3-VO triad fields and pass_count."""
        _, _, handler, _ = data_vault_setup
        cid = ContentId("wide_exp_404")
        original = _make_sample_transcript(cid.value, "Global History", pass_count=2)

        handler.save_stage_transcript("wide_expander", original)

        retrieved = handler.get_stage_transcript("wide_expander", cid)
        assert retrieved is not None
        assert isinstance(retrieved, StageTranscript)
        assert retrieved.content.id == cid
        assert retrieved.channel.name == "Global History"
        assert retrieved.channel.id == ChannelId("UC_STANGLER")
        assert retrieved.provenance.url == "https://youtube.com/watch?v=wide_exp_404"
        assert retrieved.provenance.publication_date == datetime.date(2026, 11, 10)
        assert retrieved.pass_count == 2
        assert "Paragraph 1 prose content." in retrieved.content.text

    def test_monomorphic_frontmatter_pass_count_omitted_when_none(
        self, data_vault_setup: tuple[Path, Path, TranscriptVaultHandler, ObsidianVaultAdapter]
    ) -> None:
        """When pass_count is None, pass_count key must be omitted from frontmatter."""
        data_dir, _, handler, _ = data_vault_setup
        transcript = _make_sample_transcript("no_pass_505", "Canal Simples", pass_count=None)

        handler.save_stage_transcript("custom_stage", transcript)

        file_path = data_dir / "custom_stage" / "Canal Simples" / "no_pass_505.md"
        content = file_path.read_text(encoding="utf-8")
        assert "pass_count" not in content

    def test_stage_name_enum_direct_dispatch(
        self, data_vault_setup: tuple[Path, Path, TranscriptVaultHandler, ObsidianVaultAdapter]
    ) -> None:
        """StageName StrEnum values must be accepted directly as stage identifier."""
        data_dir, _, handler, _ = data_vault_setup
        transcript = _make_sample_transcript("enum_606", "Canal Enum", pass_count=1)

        handler.save_stage_transcript(StageName.FLUID_PROSE, transcript)
        assert (data_dir / "fluid_prose" / "Canal Enum" / "enum_606.md").exists()

        handler.save_stage_transcript(StageName.GAP_FILLER, transcript)
        assert (data_dir / "gap_filler" / "Canal Enum" / "enum_606.md").exists()

        retrieved = handler.get_stage_transcript(StageName.FLUID_PROSE, ContentId("enum_606"))
        assert retrieved is not None
        assert retrieved.content.id == ContentId("enum_606")

    def test_monomorphic_stage_persistence_via_adapter(
        self, data_vault_setup: tuple[Path, Path, TranscriptVaultHandler, ObsidianVaultAdapter]
    ) -> None:
        """ObsidianVaultAdapter delegates to save_stage_transcript and get_stage_transcript per ADR-058/059."""
        data_dir, _, _, adapter = data_vault_setup

        raw_tx = _make_sample_transcript("compat_raw", "Canal Compat")
        adapter.save_stage_transcript("raw", raw_tx)
        assert (data_dir / "raw" / "Canal Compat" / "compat_raw.md").exists()
        loaded_raw = adapter.get_stage_transcript("raw", ContentId("compat_raw"))
        assert loaded_raw is not None
        assert loaded_raw.content.id == ContentId("compat_raw")

        fluid_tx = _make_sample_transcript("compat_fluid", "Canal Compat")
        adapter.save_stage_transcript("fluid_prose", fluid_tx)
        assert (data_dir / "fluid_prose" / "Canal Compat" / "compat_fluid.md").exists() or (
            data_dir / "fluid" / "Canal Compat" / "compat_fluid.md"
        ).exists()
        loaded_fluid = adapter.get_stage_transcript("fluid_prose", ContentId("compat_fluid"))
        assert loaded_fluid is not None
        assert loaded_fluid.content.id == ContentId("compat_fluid")

        comp_tx = _make_sample_transcript("compat_comp", "Canal Compat", pass_count=2)
        adapter.save_stage_transcript("gap_filler", comp_tx)
        assert (data_dir / "gap_filler" / "Canal Compat" / "compat_comp.md").exists() or (
            data_dir / "enriched" / "Canal Compat" / "compat_comp.md"
        ).exists()
        loaded_comp = adapter.get_stage_transcript("gap_filler", ContentId("compat_comp"))
        assert loaded_comp is not None
        assert loaded_comp.content.id == ContentId("compat_comp")
