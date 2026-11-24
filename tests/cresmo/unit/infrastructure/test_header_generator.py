"""Unit tests for RandomHeaderGenerator adapter.

Verifies loading from bundled package resources, custom path override,
resilient fallback on corruption/missing file, and profile coherence via public get_random_headers().
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from cresmo.infrastructure.adapters.scrapers.header_generator import RandomHeaderGenerator


class TestRandomHeaderGenerator:
    """Test suite for RandomHeaderGenerator."""

    def test_loads_bundled_resource_by_default(self) -> None:
        generator = RandomHeaderGenerator()
        seen_uas = {generator.get_random_headers()["User-Agent"] for _ in range(80)}
        assert len(seen_uas) > 5

    def test_get_random_headers_contains_required_keys(self) -> None:
        generator = RandomHeaderGenerator()
        headers = generator.get_random_headers()

        assert isinstance(headers, dict)
        assert headers["User-Agent"].startswith("Mozilla/5.0")
        assert len(headers["User-Agent"]) > 20
        assert "Accept" in headers

    def test_loads_from_custom_file_path(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        custom_file = tmp_path / "custom_headers.json"
        custom_profiles = [
            {
                "User-Agent": "CustomTestBrowser/1.0",
                "Accept": "application/json",
                "Sec-Ch-Ua-Platform": '"Linux"',
            }
        ]
        custom_file.write_text(json.dumps(custom_profiles), encoding="utf-8")

        generator = RandomHeaderGenerator(headers_path=custom_file)
        headers = generator.get_random_headers()
        assert headers["User-Agent"] == "CustomTestBrowser/1.0"
        assert headers["Accept"] == "application/json"
        assert "Successfully loaded 1 browser header profiles." in caplog.text

    def test_fallback_when_file_not_found(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.WARNING)
        missing_file = tmp_path / "non_existent_pool.json"
        generator = RandomHeaderGenerator(headers_path=missing_file)

        seen_platforms: set[str] = set()
        for _ in range(30):
            hdrs = generator.get_random_headers()
            assert hdrs["Sec-Fetch-Dest"] == "empty"
            assert hdrs["Sec-Fetch-Mode"] == "cors"
            assert hdrs["Sec-Fetch-Site"] == "same-origin"
            seen_platforms.add(hdrs["Sec-Ch-Ua-Platform"])

        assert seen_platforms <= {'"Windows"', '"macOS"'}
        assert f"Custom headers path '{missing_file}' does not exist." in caplog.text
        assert (
            "Browser header profiles pool was empty or failed to load. Falling back to embedded default profiles."
            in caplog.text
        )

    def test_fallback_when_file_is_invalid_json(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.WARNING)
        corrupt_file = tmp_path / "corrupt.json"
        corrupt_file.write_text("{invalid json", encoding="utf-8")

        generator = RandomHeaderGenerator(headers_path=corrupt_file)
        headers = generator.get_random_headers()
        assert "User-Agent" in headers
        assert "Sec-Ch-Ua" in headers
        assert f"Failed to load custom headers from '{corrupt_file}':" in caplog.text

    def test_empty_profiles_fallback_behavior(self) -> None:
        generator = RandomHeaderGenerator()
        generator._profiles = []
        headers = generator.get_random_headers()
        assert headers["User-Agent"].startswith("Mozilla/5.0 (Windows NT 10.0")
        assert headers["Sec-Ch-Ua-Platform"] == '"Windows"'

    def test_custom_payload_non_list_falls_back(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.WARNING)
        p1 = tmp_path / "not_list.json"
        p1.write_text('{"User-Agent": "Dict"}', encoding="utf-8")
        generator = RandomHeaderGenerator(headers_path=p1)
        headers = generator.get_random_headers()
        assert headers["User-Agent"].startswith("Mozilla/5.0")
        assert "Headers pool payload must be a JSON array." in caplog.text

    def test_custom_payload_items_missing_user_agent_or_non_dict(self, tmp_path: Path) -> None:
        p2 = tmp_path / "bad_items.json"
        p2.write_text(json.dumps(["not_a_dict", {"Accept": "only accept"}]), encoding="utf-8")
        generator = RandomHeaderGenerator(headers_path=p2)
        headers = generator.get_random_headers()
        assert headers["User-Agent"].startswith("Mozilla/5.0")

    def test_package_resource_loading_failure_falls_back(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.WARNING)
        with patch("importlib.resources.files", side_effect=OSError("Resource access denied")):
            generator = RandomHeaderGenerator()
            headers = generator.get_random_headers()
            assert headers["User-Agent"].startswith("Mozilla/5.0")
            assert (
                "Failed to load bundled package headers resource: Resource access denied"
                in caplog.text
            )

    def test_get_random_headers_returns_defensive_copy(self) -> None:
        generator = RandomHeaderGenerator()
        copy1 = generator.get_random_headers()
        copy1.clear()
        assert "User-Agent" in generator.get_random_headers()

    def test_profile_platform_coherence(self) -> None:
        generator = RandomHeaderGenerator()
        for _ in range(40):
            profile = generator.get_random_headers()
            ua = profile.get("User-Agent", "")
            platform = profile.get("Sec-Ch-Ua-Platform", "")

            if platform == '"Windows"':
                assert "Windows" in ua
            elif platform == '"macOS"':
                assert "Macintosh" in ua or "Mac OS X" in ua
            elif platform == '"Linux"':
                assert "Linux" in ua or "X11" in ua
