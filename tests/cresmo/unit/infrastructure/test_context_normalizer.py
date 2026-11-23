"""Hermetic unit tests for PromptVariableSchema and normalize_prompt_context (ADR-071)."""

from __future__ import annotations

from cresmo.domain.value_objects import ChannelName, PromptKey
from cresmo.infrastructure.adapters.prompts.context_normalizer import (
    DEFAULT_LANGUAGE,
    PROMPT_VARIABLE_SCHEMAS,
    normalize_prompt_context,
)


class TestContextNormalizer:
    """Unit tests covering bijective PromptKey coverage, aliases, ChannelName, and GAP_FILLER."""

    def test_schemas_cover_all_prompt_keys_bijectively(self) -> None:
        assert set(PROMPT_VARIABLE_SCHEMAS.keys()) == set(PromptKey)
        assert len(PROMPT_VARIABLE_SCHEMAS) == len(PromptKey)

    def test_channel_name_coercion_and_language_precedence(self) -> None:
        norm_default = normalize_prompt_context(
            PromptKey.RAW_INDEX_SYNTHESIS,
            {
                "channel_name": ChannelName("Tech Channel"),
                "title": "Video Title",
                "summary": "Short summary.",
            },
        )
        assert norm_default["channel_name"] == "Tech Channel"
        assert norm_default["content_title"] == "Video Title"
        assert norm_default["language"] == DEFAULT_LANGUAGE

        norm_override = normalize_prompt_context(
            PromptKey.RAW_INDEX_SYNTHESIS,
            {
                "channel_name": ChannelName("Tech Channel"),
                "content_title": "Explicit Title",
                "title": "Ignored Title",
                "summary": "Short summary.",
                "language": "English",
            },
            default_language="Spanish",
        )
        assert norm_override["content_title"] == "Explicit Title"
        assert norm_override["language"] == "English"

    def test_gap_filler_builds_draft_section_and_prev_pass_num(self) -> None:
        pass1 = normalize_prompt_context(
            PromptKey.GAP_FILLER,
            {"source_text": "Fluid prose.", "pass_num": 1, "channel_name": ChannelName("Ch")},
        )
        assert pass1["raw_text"] == "Fluid prose."
        assert pass1["draft_section"] == ""
        assert pass1["prev_pass_num"] == "0"
        assert pass1["channel_name"] == "Ch"
        assert pass1["language"] == DEFAULT_LANGUAGE

        pass2 = normalize_prompt_context(
            PromptKey.GAP_FILLER,
            {
                "source_text": "Fluid prose.",
                "pass_num": 2,
                "current_text": "Draft from pass 1.",
            },
        )
        assert pass2["prev_pass_num"] == "1"
        assert pass2["draft_section"] == '\n<draft pass="1">\nDraft from pass 1.\n</draft>\n'

    def test_long_and_wide_expander_and_judge_raw_index_aliases(self) -> None:
        long_pass2 = normalize_prompt_context(
            PromptKey.LONG_EXPANDER,
            {
                "source_text": "Expanded draft.",
                "pass_num": 2,
                "current_text": "Long pass 1.",
            },
        )
        assert long_pass2["raw_text"] == "Expanded draft."
        assert long_pass2["prev_pass_num"] == "1"
        assert long_pass2["draft_section"] == '\n<draft pass="1">\nLong pass 1.\n</draft>\n'

        wide = normalize_prompt_context(
            PromptKey.WIDE_EXPANDER,
            {
                "source_text": "Expanded draft.",
                "pass_num": 2,
                "current_text": "Wide pass 1.",
            },
        )
        assert wide["raw_text"] == "Expanded draft."
        assert wide["prev_pass_num"] == "1"
        assert wide["draft_section"] == '\n<draft pass="1">\nWide pass 1.\n</draft>\n'
        assert "language" in wide

        judge_synth = normalize_prompt_context(
            PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
            {"transcript_excerpt": "Excerpt body.", "synthesis": "Synth body."},
        )
        assert judge_synth["summary"] == "Excerpt body."
        assert judge_synth["synthesis"] == "Synth body."

    def test_raw_index_concepts_rewrite_normalizes_language_and_previous_output(self) -> None:
        ctx = normalize_prompt_context(
            PromptKey.RAW_INDEX_CONCEPTS_REWRITE,
            {"previous_output": "Old concepts", "language": "English"},
        )
        assert ctx["previous_output"] == "Old concepts"
        assert ctx["language"] == "English"

    def test_none_values_are_skipped_without_dropping_subsequent_entries(self) -> None:
        normalized = normalize_prompt_context(
            PromptKey.RAW_INDEX_SUMMARY,
            {
                "optional_empty": None,
                "title": "Subsequent Title",
                "transcript_excerpt": "Body excerpt.",
            },
        )
        assert "optional_empty" not in normalized
        assert normalized["title"] == "Subsequent Title"
        assert normalized["content_title"] == "Subsequent Title"
        assert normalized["transcript_excerpt"] == "Body excerpt."

    def test_gap_filler_defaults_pass_num_when_missing_or_invalid(self) -> None:
        missing_pass = normalize_prompt_context(
            PromptKey.GAP_FILLER,
            {"source_text": "Fluid prose.", "current_text": "Draft body."},
        )
        assert missing_pass["prev_pass_num"] == "0"
        assert missing_pass["draft_section"] == '\n<draft pass="0">\nDraft body.\n</draft>\n'

        invalid_value_pass = normalize_prompt_context(
            PromptKey.GAP_FILLER,
            {"source_text": "Fluid prose.", "pass_num": "not-an-int", "current_text": "Draft."},
        )
        assert invalid_value_pass["prev_pass_num"] == "0"
        assert invalid_value_pass["draft_section"] == '\n<draft pass="0">\nDraft.\n</draft>\n'

        invalid_type_pass = normalize_prompt_context(
            PromptKey.GAP_FILLER,
            {"source_text": "Fluid prose.", "pass_num": ["bad"], "current_text": "Draft."},
        )
        assert invalid_type_pass["prev_pass_num"] == "0"
        assert invalid_type_pass["draft_section"] == '\n<draft pass="0">\nDraft.\n</draft>\n'
