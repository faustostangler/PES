"""Unit tests for json_parser utility.

Tests direct JSON parsing, markdown code fences, outermost array/object bracket extraction,
and error handling.
"""

from __future__ import annotations

import pytest

from cresmo.application.json_parser import extract_json_data


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
