"""Unit tests for ConcatMasterUseCase adhering to the Doctor Stangler Method."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.use_cases.concat_master import (
    SENTINEL_FALLBACK_SORT_DATE,
    ConcatMasterUseCase,
    count_words,
    parse_metadata_from_content,
)
from cresmo.domain.value_objects import ChannelName, ContentId, MasterDocumentResult
from cresmo.infrastructure.config import CresmoSettings
from tests.doubles.mock_adapters import InMemoryVaultAdapter


class TestConcatMasterUseCase:
    """Test suite verifying chronological ordering, word chunking, and master file generation."""

    def test_count_words(self) -> None:
        assert count_words("") == 0
        assert count_words("hello world") == 2
        assert count_words("   one   two   three   ") == 3

    def test_parse_metadata_all_permutations(self) -> None:
        # 1. Complete metadata
        content = (
            "---\n"
            "video_id: vid_custom_123\n"
            "video_date: 20240101\n"
            "channel_category: history\n"
            "---\n"
            "Body"
        )
        sort_date, cat, vid = parse_metadata_from_content(
            content, channel_name=ChannelName("TestChan"), fallback_stem="fallback_stem"
        )
        assert sort_date == 20240101
        assert cat == "history"
        assert isinstance(vid, ContentId)
        assert vid.value == "vid_custom_123"

        # 2. Missing video_date falls back to sentinel date
        content_no_date = "---\nvideo_id: vid_1\nchannel_category: science\n---\nBody"
        sort_date_fallback, _, _ = parse_metadata_from_content(
            content_no_date, channel_name=ChannelName("TestChan"), fallback_stem="fallback"
        )
        assert sort_date_fallback == SENTINEL_FALLBACK_SORT_DATE
        assert sort_date_fallback == 99_999_999

        # 3. Missing channel_category falls back to taxonomy classification (3blue1brown -> engineering)
        content_no_cat = "---\nvideo_id: vid_1\nvideo_date: 20230101\n---\nBody"
        _, fallback_cat, _ = parse_metadata_from_content(
            content_no_cat, channel_name=ChannelName("3blue1brown"), fallback_stem="fallback"
        )
        assert fallback_cat == "engineering"

        # 4. Missing video_id falls back to fallback_stem
        content_no_vid = "---\nvideo_date: 20230101\nchannel_category: tech\n---\nBody"
        _, _, vid_fallback = parse_metadata_from_content(
            content_no_vid, channel_name=ChannelName("TestChan"), fallback_stem="stem_from_path"
        )
        assert vid_fallback == ContentId("stem_from_path")

        # 5. Whitespace-only video_id falls back to fallback_stem
        content_blank_vid = (
            "---\nvideo_id: '   '\nvideo_date: 20230101\nchannel_category: tech\n---\nBody"
        )
        _, _, vid_blank_fallback = parse_metadata_from_content(
            content_blank_vid,
            channel_name=ChannelName("TestChan"),
            fallback_stem="stem_blank_fallback",
        )
        assert vid_blank_fallback == ContentId("stem_blank_fallback")

    def test_empty_channel_returns_empty_list(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)

        results = use_case.execute_for_channel(channel_name=ChannelName("EmptyChannel"))
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
        results = use_case.execute_for_channel(ChannelName("HistoryChannel"))

        assert len(results) == 1
        res = results[0]
        assert isinstance(res, MasterDocumentResult)
        assert res.channel_name == ChannelName("HistoryChannel")
        assert res.channel_category == "history"
        assert res.part_number == 1
        assert res.document_count == 3
        assert res.video_ids == ("vid_2021", "vid_2023", "vid_2024")
        assert all(isinstance(vid, ContentId) for vid in res.video_ids)
        assert res.output_path is not None
        assert res.output_path == Path("/mock/master/history/HistoryChannel_001.md")

        # Verify content order and exact structure in master document
        content = vault.master_documents[("HistoryChannel", "history", 1)]
        idx_oldest = content.find("Oldest content 2021")
        idx_mid = content.find("Middle content 2023")
        idx_newest = content.find("Newest content 2024")
        assert 0 <= idx_oldest < idx_mid < idx_newest
        assert content.endswith("\n")
        assert not content.endswith("XX\nXX")

    def test_chronological_sorting_not_reversed_by_filename_or_content_tie_breaker(
        self, tmp_path: Path
    ) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "OrderChannel"
        ch_dir.mkdir(parents=True)

        # 1. Distinct dates with reverse alphabetical filenames
        f_old = ch_dir / "z_old.md"
        f_old.write_text(
            "---\nvideo_id: z_old\nvideo_date: 20210101\nchannel_category: science\n---\n\nOld content",
            encoding="utf-8",
        )
        f_new = ch_dir / "a_new.md"
        f_new.write_text(
            "---\nvideo_id: a_new\nvideo_date: 20240101\nchannel_category: science\n---\n\nNew content",
            encoding="utf-8",
        )

        vault.channel_enriched_files["OrderChannel"] = [f_new, f_old]
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        res = use_case.execute(ChannelName("OrderChannel"))
        assert len(res) == 1
        assert res[0].video_ids == (ContentId("z_old"), ContentId("a_new"))

        # 2. Identical dates with distinct filenames and opposite content order
        f_tie1 = ch_dir / "a_tie.md"
        f_tie1.write_text(
            "---\nvideo_id: a_tie\nvideo_date: 20230101\nchannel_category: science\n---\n\nZebra",
            encoding="utf-8",
        )
        f_tie2 = ch_dir / "b_tie.md"
        f_tie2.write_text(
            "---\nvideo_id: b_tie\nvideo_date: 20230101\nchannel_category: science\n---\n\nApple",
            encoding="utf-8",
        )

        vault.channel_enriched_files["OrderChannel"] = [f_tie2, f_tie1]
        res_tie = use_case.execute(ChannelName("OrderChannel"))
        assert len(res_tie) == 1
        assert res_tie[0].video_ids == (ContentId("a_tie"), ContentId("b_tie"))

        # 3. Stable sort when filename and date are identical (preserves input order against content sort)
        # mock_p1 has content 'Zebra' (starts with 'z_id1'), mock_p2 has content 'Apple' (starts with 'a_id2')
        # If sorted by content (mutmut_29 key=None or mutmut_32 doc_tuple[2]), mock_p2 would be sorted before mock_p1!
        # With key=(doc[0], doc[1]), Python's sort is stable and keeps mock_p1 first!
        mock_p1 = MagicMock()
        mock_p1.name = "same.md"
        mock_p1.stem = "stem1"
        mock_p1.read_text.return_value = (
            "---\nvideo_id: z_id1\nvideo_date: 20230101\nchannel_category: science\n---\n\nZebra"
        )

        mock_p2 = MagicMock()
        mock_p2.name = "same.md"
        mock_p2.stem = "stem2"
        mock_p2.read_text.return_value = (
            "---\nvideo_id: a_id2\nvideo_date: 20230101\nchannel_category: science\n---\n\nApple"
        )

        vault.channel_enriched_files["OrderChannel"] = [mock_p1, mock_p2]
        res_stable = use_case.execute(ChannelName("OrderChannel"))
        assert len(res_stable) == 1
        assert res_stable[0].video_ids == (ContentId("z_id1"), ContentId("a_id2"))

    def test_execute_uses_file_stem_when_video_id_is_absent(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "StemChannel"
        ch_dir.mkdir(parents=True)

        f_no_vid = ch_dir / "unidentified_document_stem.md"
        f_no_vid.write_text(
            "---\nvideo_date: 20230101\nchannel_category: tech\n---\n\nNo video_id present",
            encoding="utf-8",
        )

        vault.channel_enriched_files["StemChannel"] = [f_no_vid]
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        results = use_case.execute(ChannelName("StemChannel"))

        assert len(results) == 1
        assert results[0].video_ids == (ContentId("unidentified_document_stem"),)

    def test_read_file_error_and_empty_content_are_skipped_via_continue(
        self, tmp_path: Path
    ) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        # File 1: raises OSError on read_text
        mock_f_err = MagicMock()
        mock_f_err.read_text.side_effect = OSError("Read failed")

        # File 2: empty content string
        mock_f_empty = MagicMock()
        mock_f_empty.read_text.return_value = "   \n\n  "

        # File 3: valid content
        mock_f_valid = MagicMock()
        mock_f_valid.name = "valid.md"
        mock_f_valid.stem = "valid"
        mock_f_valid.read_text.return_value = (
            "---\nvideo_id: valid\nvideo_date: 20230101\nchannel_category: tech\n---\n\nValid text"
        )

        vault.channel_enriched_files["SkipChannel"] = [mock_f_err, mock_f_empty, mock_f_valid]
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        results = use_case.execute(ChannelName("SkipChannel"))

        assert len(results) == 1
        assert results[0].document_count == 1
        assert results[0].video_ids == (ContentId("valid"),)
        mock_f_valid.read_text.assert_called_with(encoding="utf-8")

    def test_execute_channel_category_fallback_when_files_omit_it(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "3blue1brown"
        ch_dir.mkdir(parents=True)

        f = ch_dir / "doc.md"
        f.write_text(
            "---\nvideo_id: doc1\nvideo_date: 20230101\n---\n\nMath physics content",
            encoding="utf-8",
        )

        vault.channel_enriched_files["3blue1brown"] = [f]
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        results = use_case.execute(ChannelName("3blue1brown"))

        assert len(results) == 1
        assert results[0].channel_category == "engineering"

    def test_word_limit_exact_boundary_fits_in_single_part(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "BoundaryChannel"
        ch_dir.mkdir(parents=True)

        words_100 = " ".join(["word"] * 100)
        words_300 = " ".join(["word"] * 300)

        f1 = ch_dir / "f1.md"
        f1.write_text(
            f"---\nvideo_id: f1\nvideo_date: 20230101\nchannel_category: tech\n---\n\n{words_100}",
            encoding="utf-8",
        )
        f2 = ch_dir / "f2.md"
        f2.write_text(
            f"---\nvideo_id: f2\nvideo_date: 20230201\nchannel_category: tech\n---\n\n{words_300}",
            encoding="utf-8",
        )

        w1 = count_words(f1.read_text(encoding="utf-8").strip())
        w2 = count_words(f2.read_text(encoding="utf-8").strip())
        exact_total = w1 + w2

        vault.channel_enriched_files["BoundaryChannel"] = [f1, f2]
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        results = use_case.execute(ChannelName("BoundaryChannel"), max_words=exact_total)

        assert len(results) == 1
        assert results[0].part_number == 1
        assert results[0].document_count == 2
        assert results[0].video_ids == (ContentId("f1"), ContentId("f2"))

    def test_multi_file_accumulation_rolls_over_and_accumulates_in_part_two(
        self, tmp_path: Path
    ) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "MultiAccumChannel"
        ch_dir.mkdir(parents=True)

        # 4 files:
        # f1: 300 words
        # f2: 100 words
        # f3: 100 words
        # f4: 100 words
        # Effective max: max(w1, w2 + w3) = ~308 words.
        # f1 (308) fills Part 1.
        # f2 (108) rolls over to Part 2 -> current_part_words must be 108 (an int, not None!).
        # f3 (108) -> 108 + 108 = 216 <= 308 -> added to Part 2 via += (so current_part_words becomes 216!).
        # f4 (108) -> 216 + 108 = 324 > 308 -> rolls over to Part 3!
        # If current_part_words = doc_words instead of +=, current_part_words on f3 is set to 108,
        # so f4 (108 + 108 = 216 <= 308) would incorrectly be added to Part 2!
        words_300 = " ".join(["word"] * 300)
        words_100 = " ".join(["word"] * 100)

        f1 = ch_dir / "f1.md"
        f1.write_text(
            f"---\nvideo_id: f1\nvideo_date: 20230101\nchannel_category: tech\n---\n\n{words_300}",
            encoding="utf-8",
        )
        f2 = ch_dir / "f2.md"
        f2.write_text(
            f"---\nvideo_id: f2\nvideo_date: 20230201\nchannel_category: tech\n---\n\n{words_100}",
            encoding="utf-8",
        )
        f3 = ch_dir / "f3.md"
        f3.write_text(
            f"---\nvideo_id: f3\nvideo_date: 20230301\nchannel_category: tech\n---\n\n{words_100}",
            encoding="utf-8",
        )
        f4 = ch_dir / "f4.md"
        f4.write_text(
            f"---\nvideo_id: f4\nvideo_date: 20230401\nchannel_category: tech\n---\n\n{words_100}",
            encoding="utf-8",
        )

        w1 = count_words(f1.read_text(encoding="utf-8").strip())
        w2 = count_words(f2.read_text(encoding="utf-8").strip())
        w3 = count_words(f3.read_text(encoding="utf-8").strip())

        effective_limit = max(w1, w2 + w3)

        vault.channel_enriched_files["MultiAccumChannel"] = [f1, f2, f3, f4]
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)
        results = use_case.execute(ChannelName("MultiAccumChannel"), max_words=effective_limit)

        assert len(results) == 3
        assert results[0].part_number == 1
        assert results[0].document_count == 1
        assert results[0].video_ids == (ContentId("f1"),)
        assert results[1].part_number == 2
        assert results[1].document_count == 2
        assert results[1].video_ids == (ContentId("f2"), ContentId("f3"))
        assert results[2].part_number == 3
        assert results[2].document_count == 1
        assert results[2].video_ids == (ContentId("f4"),)

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
        results = use_case.execute(ChannelName("BigDocChannel"), max_words=500)

        assert len(results) == 1
        assert results[0].part_number == 1
        assert results[0].video_ids == (ContentId("big"),)
        assert results[0].word_count >= 1000

    def test_execute_for_channel_propagates_max_words(self, tmp_path: Path) -> None:
        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        ch_dir = tmp_path / "enriched" / "ForwardChannel"
        ch_dir.mkdir(parents=True)

        words_100 = " ".join(["word"] * 100)
        f1 = ch_dir / "f1.md"
        f1.write_text(
            f"---\nvideo_id: f1\nvideo_date: 20230101\nchannel_category: tech\n---\n\n{words_100}",
            encoding="utf-8",
        )
        f2 = ch_dir / "f2.md"
        f2.write_text(
            f"---\nvideo_id: f2\nvideo_date: 20230201\nchannel_category: tech\n---\n\n{words_100}",
            encoding="utf-8",
        )

        vault.channel_enriched_files["ForwardChannel"] = [f1, f2]
        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)

        # When max_words=150 is passed, it must split into 2 parts (each file is ~108 words)
        # If mutated to max_words=None or omitted, it uses settings.concat_max_words (50000) and produces 1 part!
        results = use_case.execute_for_channel(ChannelName("ForwardChannel"), max_words=150)
        assert len(results) == 2

    def test_execute_all_filters_directories_and_propagates_parameters(
        self, tmp_path: Path
    ) -> None:
        enriched_root = tmp_path / "data" / "enriched"
        enriched_root.mkdir(parents=True)

        # 1. Valid channel directories
        (enriched_root / "ChannelA").mkdir()
        (enriched_root / "ChannelB").mkdir()

        # 2. Hidden directory starting with '.'
        (enriched_root / ".hidden_cache").mkdir()

        # 3. System directory starting with '_'
        (enriched_root / "_system_templates").mkdir()

        # 4. Stray regular file (not directory)
        (enriched_root / "stray_notes.md").write_text("Stray notes", encoding="utf-8")

        settings = CresmoSettings(data_dir=tmp_path / "data", vault_dir=tmp_path / "vault")
        vault = InMemoryVaultAdapter()

        words_100 = " ".join(["word"] * 100)
        fA1 = enriched_root / "ChannelA" / "a1.md"
        fA1.write_text(
            f"---\nvideo_id: a1\nvideo_date: 20230101\n---\n\n{words_100}", encoding="utf-8"
        )
        fA2 = enriched_root / "ChannelA" / "a2.md"
        fA2.write_text(
            f"---\nvideo_id: a2\nvideo_date: 20230201\n---\n\n{words_100}", encoding="utf-8"
        )

        fB1 = enriched_root / "ChannelB" / "b1.md"
        fB1.write_text(
            f"---\nvideo_id: b1\nvideo_date: 20230101\n---\n\n{words_100}", encoding="utf-8"
        )
        fB2 = enriched_root / "ChannelB" / "b2.md"
        fB2.write_text(
            f"---\nvideo_id: b2\nvideo_date: 20230201\n---\n\n{words_100}", encoding="utf-8"
        )

        vault.channel_enriched_files["ChannelA"] = [fA1, fA2]
        vault.channel_enriched_files["ChannelB"] = [fB1, fB2]

        # Also register mock files for the ignored targets so if the filtering fails,
        # execute_for_channel would produce results and contaminate all_results!
        vault.channel_enriched_files[".hidden_cache"] = [fA1]
        vault.channel_enriched_files["_system_templates"] = [fA1]
        vault.channel_enriched_files["stray_notes.md"] = [fA1]

        use_case = ConcatMasterUseCase(vault_port=vault, settings=settings)

        # Execute with explicit max_words=150
        all_results = use_case.execute_all(max_words=150)

        # Verify exact channel keys discovered (no stray files, no hidden or underscore dirs)
        assert sorted(all_results.keys()) == ["ChannelA", "ChannelB"]
        assert ".hidden_cache" not in all_results
        assert "_system_templates" not in all_results
        assert "stray_notes.md" not in all_results

        # Verify max_words=150 was propagated: each channel has 2 files of ~108 words,
        # so limit 150 forces 2 parts per channel. If max_words was None, len would be 1!
        assert len(all_results["ChannelA"]) == 2
        assert len(all_results["ChannelB"]) == 2

        # Test when enriched_root is a regular file (not directory)
        file_env = tmp_path / "file_env"
        file_env.mkdir()
        (file_env / "enriched").write_text("I am a file", encoding="utf-8")
        settings_file_root = CresmoSettings(data_dir=file_env, vault_dir=tmp_path / "vault")
        use_case_file_root = ConcatMasterUseCase(vault_port=vault, settings=settings_file_root)
        assert use_case_file_root.execute_all() == {}

        # Test when enriched_root does not exist
        settings_non_existent = CresmoSettings(
            data_dir=tmp_path / "does_not_exist",
            vault_dir=tmp_path / "vault",
        )
        use_case_non_existent = ConcatMasterUseCase(
            vault_port=vault, settings=settings_non_existent
        )
        assert use_case_non_existent.execute_all() == {}
