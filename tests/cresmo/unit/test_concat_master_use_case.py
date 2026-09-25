"""Unit tests for ConcatMasterUseCase adhering to the Doctor Stangler Method."""

from __future__ import annotations

from pathlib import Path

from cresmo.application.use_cases.concat_master import (
    ConcatMasterUseCase,
    parse_metadata_from_content,
)
from cresmo.domain.value_objects import ContentId, MasterDocumentResult
from cresmo.infrastructure.config import CresmoSettings
from tests.doubles.mock_adapters import InMemoryVaultAdapter


class TestConcatMasterUseCase:
    """Test suite verifying chronological ordering, word chunking, and master file generation."""

    def test_empty_channel_returns_empty_list(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)

        results = use_case.execute_for_channel(channel_name="EmptyChannel")
        assert results == []

    def test_chronological_sorting_oldest_first(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "HistoryChannel"
        ch_dir.mkdir(parents=True)

        f_newest = ch_dir / "vid_2024.md"
        f_newest.write_text(
            "---\nvideo_title: Newest\nvideo_id: vid_2024\nvideo_date: 20240101\nchannel_category: history\n---\n\nNewest content 2024",
            encoding="utf-8",
        )

        f_oldest = ch_dir / "vid_2021.md"
        f_oldest.write_text(
            "---\nvideo_title: Oldest\nvideo_id: vid_2021\nvideo_date: 20210510\nchannel_category: history\n---\n\nOldest content 2021",
            encoding="utf-8",
        )

        f_mid = ch_dir / "vid_2023.md"
        f_mid.write_text(
            "---\nvideo_title: Middle\nvideo_id: vid_2023\nvideo_date: 20230815\nchannel_category: history\n---\n\nMiddle content 2023",
            encoding="utf-8",
        )

        vault.channel_enriched_files["HistoryChannel"] = [f_newest, f_oldest, f_mid]

        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        results = use_case.execute_for_channel("HistoryChannel")

        assert len(results) == 1
        res = results[0]
        assert isinstance(res, MasterDocumentResult)
        assert res.channel_name == "HistoryChannel"
        assert res.channel_category == "history"
        assert res.part_number == 1
        assert res.document_count == 3
        assert res.video_ids == ("vid_2021", "vid_2023", "vid_2024")
        assert all(isinstance(vid, ContentId) for vid in res.video_ids)

        # Verify content order in master document
        content = vault.master_documents[("HistoryChannel", "history", 1)]
        idx_oldest = content.find("Oldest content 2021")
        idx_mid = content.find("Middle content 2023")
        idx_newest = content.find("Newest content 2024")
        assert 0 <= idx_oldest < idx_mid < idx_newest

    def test_word_limit_never_splits_file_and_rolls_over(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "TechChannel"
        ch_dir.mkdir(parents=True)

        # 3 files with word counts: 250 words, 300 words, 150 words.
        # Limit set to 400 words.
        # File 1 (250) + File 2 (300) = 550 > 400.
        # So Part 1 contains File 1 (250 words).
        # Part 2 contains File 2 (300 words) + File 3 (150 words) = 450 > 400.
        # So Part 2 contains File 2 (300 words).
        # Part 3 contains File 3 (150 words).
        words_250 = " ".join(["word"] * 250)
        words_300 = " ".join(["word"] * 300)
        words_150 = " ".join(["word"] * 150)

        f1 = ch_dir / "f1.md"
        f1.write_text(
            f"---\nvideo_id: f1\nvideo_date: 20230101\nchannel_category: tech\n---\n\n{words_250}",
            encoding="utf-8",
        )
        f2 = ch_dir / "f2.md"
        f2.write_text(
            f"---\nvideo_id: f2\nvideo_date: 20230201\nchannel_category: tech\n---\n\n{words_300}",
            encoding="utf-8",
        )
        f3 = ch_dir / "f3.md"
        f3.write_text(
            f"---\nvideo_id: f3\nvideo_date: 20230301\nchannel_category: tech\n---\n\n{words_150}",
            encoding="utf-8",
        )

        vault.channel_enriched_files["TechChannel"] = [f1, f2, f3]

        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        results = use_case.execute_for_channel("TechChannel", max_words=400)

        assert len(results) == 3
        assert results[0].part_number == 1
        assert results[0].video_ids == ("f1",)
        assert results[1].part_number == 2
        assert results[1].video_ids == ("f2",)
        assert results[2].part_number == 3
        assert results[2].video_ids == ("f3",)

    def test_single_large_file_stays_whole_without_split(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "BigDocChannel"
        ch_dir.mkdir(parents=True)

        large_words = " ".join(["epic"] * 1000)
        f_big = ch_dir / "big.md"
        f_big.write_text(
            f"---\nvideo_id: big\nvideo_date: 20230101\nchannel_category: science\n---\n\n{large_words}",
            encoding="utf-8",
        )

        vault.channel_enriched_files["BigDocChannel"] = [f_big]

        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        # Limit 500 words, but file is 1000 words. Must remain whole in Part 1!
        results = use_case.execute_for_channel("BigDocChannel", max_words=500)

        assert len(results) == 1
        assert results[0].part_number == 1
        assert results[0].video_ids == ("big",)
        assert results[0].word_count >= 1000

    def test_execute_all_discovers_all_channels(self, tmp_path: Path) -> None:
        enriched_root = tmp_path / "data" / "enriched"
        (enriched_root / "ChannelA").mkdir(parents=True)
        (enriched_root / "ChannelB").mkdir(parents=True)

        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        fA = enriched_root / "ChannelA" / "a.md"
        fA.write_text("---\nvideo_id: va\nvideo_date: 20230101\n---\n\nContent A", encoding="utf-8")
        fB = enriched_root / "ChannelB" / "b.md"
        fB.write_text("---\nvideo_id: vb\nvideo_date: 20230101\n---\n\nContent B", encoding="utf-8")

        vault.channel_enriched_files["ChannelA"] = [fA]
        vault.channel_enriched_files["ChannelB"] = [fB]

        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        all_results = use_case.execute_all()

        assert "ChannelA" in all_results
        assert "ChannelB" in all_results
        assert len(all_results["ChannelA"]) == 1
        assert len(all_results["ChannelB"]) == 1

    def test_parse_metadata_returns_strongly_typed_content_id(self) -> None:
        content = "---\nvideo_id: vid_custom_123\nvideo_date: 20240101\n---\nBody"
        _sort_date, _cat, vid = parse_metadata_from_content(
            content, channel_name="TestChan", fallback_stem="fallback_stem"
        )
        assert isinstance(vid, ContentId)
        assert vid.value == "vid_custom_123"
        assert vid == "vid_custom_123"
