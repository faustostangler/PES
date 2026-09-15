"""Unit tests for json_parser utility.

Tests direct JSON parsing, markdown code fences, outermost array/object bracket extraction,
and error handling.
"""

from __future__ import annotations

import pytest

from cresmo.application.json_parser import (
    _TRAILING_COMMA_PATTERN,
    _extract_individual_objects,
    extract_json_data,
)


class TestJsonParser:
    """Hermetic unit tests for extract_json_data."""

    def test_direct_json_array(self) -> None:
        raw = '[{"title": "Test Entity", "type": "entity"}]'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert result[0]["title"] == "Test Entity"

    def test_markdown_code_fence_json(self) -> None:
        raw = 'Here is the extracted inventory:\n```json\n[{"title": "Pareto", "type": "entity"}]\n```\nDone.'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert result[0]["title"] == "Pareto"

    def test_markdown_code_fence_without_tag(self) -> None:
        raw = 'Output:\n```\n[{"title": "Mosca", "type": "entity"}]\n```'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert result[0]["title"] == "Mosca"

    def test_outermost_brackets_in_prose(self) -> None:
        raw = 'Prefix text [{"title": "Elitism", "type": "concept"}] Suffix text.'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert result[0]["title"] == "Elitism"

    def test_outermost_object_in_prose(self) -> None:
        raw = 'Prefix text {"title": "Object", "type": "concept"} Suffix text.'
        result = extract_json_data(raw)
        assert isinstance(result, dict)
        assert result["title"] == "Object"

    def test_invalid_json_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Failed to extract valid JSON payload"):
            extract_json_data("This is purely conversational text without brackets.")

    def test_json_array_with_trailing_comma(self) -> None:
        raw = '[{"title": "Trailing", "type": "concept"}, ]'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Trailing"

    def test_json_object_with_trailing_comma(self) -> None:
        raw = '{"title": "Object Trailing", "type": "concept", }'
        result = extract_json_data(raw)
        assert isinstance(result, dict)
        assert result["title"] == "Object Trailing"

    def test_truncated_array_extracts_individual_objects(self) -> None:
        raw = '[{"title": "Item 1", "type": "concept"}, {"title": "Item 2", "type": "entity"}, {"title": "Item 3'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "Item 1"
        assert result[1]["title"] == "Item 2"

    def test_markdown_fence_with_trailing_comma(self) -> None:
        raw = 'Explanation:\n```json\n[{"title": "Note 1", "type": "concept"}, ]\n```\nDone.'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Note 1"

    def test_markdown_multiple_fences_skips_invalid(self) -> None:
        raw = '```json\nInvalid {Not JSON}\n```\n```json\n[{"title": "Valid Fence"}]\n```'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert result[0]["title"] == "Valid Fence"

    def test_outermost_brackets_with_trailing_comma(self) -> None:
        raw = 'Preceding text [{"title": "Bracket Trailing", "type": "entity"}, ] trailing words.'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert result[0]["title"] == "Bracket Trailing"

    def test_extract_individual_objects_escapes_and_nested_braces(self) -> None:
        raw = (
            'Some partial stream: [{"title": "Quote \\"Nested\\"", "meta": {"depth": 2}}, '
            '{"title": "Back\\\\slash"}, {"broken": "unclosed'
        )
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["meta"]["depth"] == 2
        assert result[1]["title"] == "Back\\slash"

    def test_extract_individual_objects_with_trailing_comma(self) -> None:
        raw = 'Text: {"title": "Object 1", "type": "concept", } and then {"title": "Object 2"}'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "Object 1"
        assert result[1]["title"] == "Object 2"

    def test_extract_single_object_without_brackets_returns_dict(self) -> None:
        # Step 4 will fail because the outermost braces span invalid content across multiple blocks
        raw = 'prefix { "title": "Single" } suffix with unclosed { brace'
        result = extract_json_data(raw)
        assert isinstance(result, dict)
        assert result["title"] == "Single"

    def test_outermost_brackets_malformed_falls_through_to_step5(self) -> None:
        raw = 'Unclosed [ not json at all but here is {"title": "Salvaged 1"} and {"title": "Salvaged 2"} inside ]'
        result = extract_json_data(raw)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["title"] == "Salvaged 1"
        assert result[1]["title"] == "Salvaged 2"

    def test_outermost_braces_malformed_with_extra_trailing_brace_returns_single_dict(self) -> None:
        raw = 'prefix text {"title": "Single Salvaged", "val": 1} stray text }'
        result = extract_json_data(raw)
        assert isinstance(result, dict)
        assert result["title"] == "Single Salvaged"

    def test_individual_objects_skips_unparseable_block(self) -> None:
        raw = 'Random stream: {"invalid": unquoted_bareword} and {"valid": "recovered"}'
        result = extract_json_data(raw)
        assert isinstance(result, dict)
        assert result["valid"] == "recovered"

    def test_extract_individual_objects_direct_cases(self) -> None:
        # String starting immediately at index 0 with '{' (kills i = 0 -> i = 1 mutant)
        text_zero = '{"key0": "val0"}{"key1": "val1"}'
        objs = _extract_individual_objects(text_zero)
        assert len(objs) == 2
        assert objs[0]["key0"] == "val0"
        assert objs[1]["key1"] == "val1"

        # String with escaped quotes and backslashes inside string value
        text_escape = '{"quote": "a \\" b", "slash": "c\\\\d"}'
        objs_esc = _extract_individual_objects(text_escape)
        assert len(objs_esc) == 1
        assert objs_esc[0]["quote"] == 'a " b'
        assert objs_esc[0]["slash"] == "c\\d"

        # String with braces inside quotes (must not alter depth)
        text_braces = '{"has_braces": "contains { and } braces"}'
        objs_braces = _extract_individual_objects(text_braces)
        assert len(objs_braces) == 1
        assert objs_braces[0]["has_braces"] == "contains { and } braces"

        # Text with no braces at all
        assert _extract_individual_objects("no braces here") == []

        # Incomplete / unclosed braces
        assert _extract_individual_objects('{"open": 1') == []

        # Trailing comma fixed inside individual object candidate
        text_tc = '{"item": 1, }'
        objs_tc = _extract_individual_objects(text_tc)
        assert len(objs_tc) == 1
        assert objs_tc[0]["item"] == 1

    def test_trailing_comma_regex_pattern(self) -> None:
        # In an array
        cleaned_arr = _TRAILING_COMMA_PATTERN.sub(r"\1", "[1, 2, ]")
        assert cleaned_arr == "[1, 2]"

        # In an object
        cleaned_obj = _TRAILING_COMMA_PATTERN.sub(r"\1", '{"a": 1, }')
        assert cleaned_obj == '{"a": 1}'
