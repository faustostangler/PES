"""Hermetic unit tests for YAML frontmatter parsing and zero-read header inspection."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Self
from unittest.mock import patch

import pytest

from cresmo.application.services.frontmatter import parse_frontmatter, read_frontmatter_header


class _SinglePassFrontmatterStream:
    """File-like iterator asserting read_frontmatter_header halts immediately at closing '---'."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines
        self._index = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> str:
        if self._index >= 2:
            raise AssertionError("read_frontmatter_header continued reading past closing '---'")
        line = self._lines[self._index]
        self._index += 1
        return line


class TestReadFrontmatterHeader:
    """Verifies zero-read header boundaries, encoding resilience, and fallback YAML parsing."""

    def test_respects_default_max_lines_boundary_50(self, tmp_path: Path) -> None:
        # 51 lines total: opening '---' at idx 0, 49 keys (idx 1..49), closing '---' at idx 50
        lines_over = ["---", *(f"k{i}: v{i}" for i in range(49)), "---", "body"]
        over_path = tmp_path / "over_50.md"
        over_path.write_text("\n".join(lines_over), encoding="utf-8")
        assert read_frontmatter_header(over_path) == {}

        # 50 lines total: opening '---' at idx 0, 48 keys (idx 1..48), closing '---' at idx 49
        lines_exact = ["---", *(f"k{i}: v{i}" for i in range(48)), "---", "body"]
        exact_path = tmp_path / "exact_50.md"
        exact_path.write_text("\n".join(lines_exact), encoding="utf-8")
        parsed = read_frontmatter_header(exact_path)
        assert parsed["k0"] == "v0"
        assert parsed["k47"] == "v47"

    def test_respects_custom_max_lines_boundary_and_returns_empty_dict(self, tmp_path: Path) -> None:
        # Closing '---' at idx 3 exceeds max_lines=3 -> must break and return {} (not None)
        path_limit = tmp_path / "custom_limit.md"
        path_limit.write_text("---\na: 1\nb: 2\n---\nbody", encoding="utf-8")
        result_over = read_frontmatter_header(path_limit, max_lines=3)
        assert result_over == {}
        assert isinstance(result_over, dict)

        # Closing '---' at idx 2 fits within max_lines=3 -> parses {'a': 1}
        path_fit = tmp_path / "custom_fit.md"
        path_fit.write_text("---\na: 1\n---\nbody", encoding="utf-8")
        assert read_frontmatter_header(path_fit, max_lines=3) == {"a": 1}

    def test_enforces_utf8_and_ignores_invalid_bytes(self, tmp_path: Path) -> None:
        raw_path = tmp_path / "bad_bytes.md"
        raw_path.write_bytes(b"---\ntitle: Caf\xc3\xa9\xff\n---\nBody\n")

        orig_open = Path.open
        recorded_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

        def _spy_open(
            self_path: Path,
            *args: object,
            **kwargs: object,
        ) -> object:
            recorded_calls.append(((self_path, *args), dict(kwargs)))
            mode = str(args[0]) if args else "r"
            encoding = kwargs.get("encoding")
            errors = kwargs.get("errors")
            return orig_open(
                self_path,
                mode,
                encoding=str(encoding) if encoding is not None else None,
                errors=str(errors) if errors is not None else None,
            )

        with patch.object(Path, "open", _spy_open):
            header = read_frontmatter_header(raw_path)

        assert header == {"title": "Café"}
        assert len(recorded_calls) == 1
        assert recorded_calls[0][0] == (raw_path, "r")
        assert recorded_calls[0][1] == {"encoding": "utf-8", "errors": "ignore"}

    def test_stops_reading_immediately_on_closing_delimiter_at_line_two(self, tmp_path: Path) -> None:
        target = tmp_path / "empty_header.md"
        stream = _SinglePassFrontmatterStream(["---\n", "---\n", "unexpected_extra_line\n"])
        with patch.object(Path, "open", return_value=stream):
            result = read_frontmatter_header(target, max_lines=50)
        assert result == {}

    def test_empty_file_and_missing_opening_delimiter_return_empty(self, tmp_path: Path) -> None:
        empty_path = tmp_path / "empty.md"
        empty_path.write_text("", encoding="utf-8")
        assert read_frontmatter_header(empty_path) == {}

        plain_path = tmp_path / "plain.md"
        plain_path.write_text("No frontmatter here\n---\ntitle: x\n---\n", encoding="utf-8")
        assert read_frontmatter_header(plain_path) == {}

    def test_oserror_logs_debug_message_and_returns_empty(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        missing = tmp_path / "does_not_exist.md"
        with caplog.at_level(logging.DEBUG):
            result = read_frontmatter_header(missing)

        assert result == {}
        record = next(
            r
            for r in caplog.records
            if r.levelno == logging.DEBUG
            and "Unable to read frontmatter header from" in r.getMessage()
        )
        msg = record.getMessage()
        assert msg.startswith(f"Unable to read frontmatter header from {missing}: ")
        assert not msg.endswith(": None")
        assert "%s" not in msg

    def test_invalid_yaml_header_uses_colon_fallback_and_logs_debug(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        bad_yaml = tmp_path / "broken_header.md"
        bad_yaml.write_text(
            "---\n"
            'title: "XFactorX"\n'
            "channel: 'SingleQuoted'\n"
            "url: https://example.com/a:b\n"
            "empty_val:\n"
            ": empty_key\n"
            "broken: [unclosed\n"
            "---\n"
            "Body\n",
            encoding="utf-8",
        )

        with caplog.at_level(logging.DEBUG):
            result = read_frontmatter_header(bad_yaml)

        assert result == {
            "title": "XFactorX",
            "channel": "SingleQuoted",
            "url": "https://example.com/a:b",
            "broken": "[unclosed",
        }
        assert "empty_val" not in result
        assert "" not in result

        record = next(
            r
            for r in caplog.records
            if r.levelno == logging.DEBUG and "Invalid YAML header in" in r.getMessage()
        )
        msg = record.getMessage()
        assert msg.startswith(f"Invalid YAML header in {bad_yaml}: ")
        assert not msg.endswith(": None")
        assert "%s" not in msg

    def test_parse_frontmatter_non_mapping_yaml_returns_empty_dict(self) -> None:
        body, meta = parse_frontmatter("---\n- item1\n- item2\n---\nBody text")
        assert body == "Body text"
        assert meta == {}
