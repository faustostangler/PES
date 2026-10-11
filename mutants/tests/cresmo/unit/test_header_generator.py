"""Unit tests for RandomHeaderGenerator adapter.

Verifies loading from bundled package resources, custom path override,
resilient fallback on corruption/missing file, and profile coherence (SPEC/TDD).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cresmo.infrastructure.adapters.header_generator import RandomHeaderGenerator


class TestRandomHeaderGenerator:
    """Test suite for RandomHeaderGenerator."""

    def test_loads_bundled_resource_by_default(self) -> None:
        generator = RandomHeaderGenerator()
        assert len(generator.profiles) >= 50

    def test_get_random_headers_contains_required_keys(self) -> None:
        generator = RandomHeaderGenerator()
        headers = generator.get_random_headers()

        assert isinstance(headers, dict)
        assert "User-Agent" in headers
        assert len(headers["User-Agent"]) > 20
        assert "Accept" in headers

    def test_get_random_user_agent_returns_string(self) -> None:
        generator = RandomHeaderGenerator()
        ua = generator.get_random_user_agent()

        assert isinstance(ua, str)
        assert ua.startswith("Mozilla/5.0")

    def test_loads_from_custom_file_path(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

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
        assert len(generator.profiles) == 1
        headers = generator.get_random_headers()
        assert headers["User-Agent"] == "CustomTestBrowser/1.0"
        assert headers["Accept"] == "application/json"
        assert "Successfully loaded 1 browser header profiles." in caplog.text

    def test_fallback_when_file_not_found(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        caplog.set_level(logging.WARNING)
        missing_file = tmp_path / "non_existent_pool.json"
        generator = RandomHeaderGenerator(headers_path=missing_file)

        assert len(generator.profiles) == 2
        p0 = generator.profiles[0]
        assert p0["User-Agent"] == (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        assert (
            p0["Accept"]
            == "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        )
        assert p0["Accept-Language"] == "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        assert p0["Sec-Ch-Ua"] == '"Not_A Brand";v="8", "Chromium";v="124", "Google Chrome";v="124"'
        assert p0["Sec-Ch-Ua-Mobile"] == "?0"
        assert p0["Sec-Ch-Ua-Platform"] == '"Windows"'
        assert p0["Sec-Fetch-Dest"] == "empty"
        assert p0["Sec-Fetch-Mode"] == "cors"
        assert p0["Sec-Fetch-Site"] == "same-origin"

        p1 = generator.profiles[1]
        assert p1["User-Agent"] == (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        assert (
            p1["Accept"]
            == "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        )
        assert p1["Accept-Language"] == "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7"
        assert (
            p1["Sec-Ch-Ua"] == '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
        )
        assert p1["Sec-Ch-Ua-Mobile"] == "?0"
        assert p1["Sec-Ch-Ua-Platform"] == '"macOS"'
        assert p1["Sec-Fetch-Dest"] == "empty"
        assert p1["Sec-Fetch-Mode"] == "cors"
        assert p1["Sec-Fetch-Site"] == "same-origin"

        assert f"Custom headers path '{missing_file}' does not exist." in caplog.text
        assert (
            "Browser header profiles pool was empty or failed to load. Falling back to embedded default profiles."
            in caplog.text
        )

    def test_fallback_when_file_is_invalid_json(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        caplog.set_level(logging.WARNING)
        corrupt_file = tmp_path / "corrupt.json"
        corrupt_file.write_text("{invalid json", encoding="utf-8")

        generator = RandomHeaderGenerator(headers_path=corrupt_file)
        assert len(generator.profiles) == 2
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
        ua = generator.get_random_user_agent()
        assert ua.startswith("Mozilla/5.0 (Windows NT 10.0")

    def test_custom_payload_non_list_falls_back(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        caplog.set_level(logging.WARNING)
        p1 = tmp_path / "not_list.json"
        p1.write_text('{"User-Agent": "Dict"}', encoding="utf-8")
        generator = RandomHeaderGenerator(headers_path=p1)
        assert len(generator.profiles) == 2
        assert "Headers pool payload must be a JSON array." in caplog.text

    def test_custom_payload_items_missing_user_agent_or_non_dict(self, tmp_path: Path) -> None:
        p2 = tmp_path / "bad_items.json"
        p2.write_text(json.dumps(["not_a_dict", {"Accept": "only accept"}]), encoding="utf-8")
        generator = RandomHeaderGenerator(headers_path=p2)
        assert len(generator.profiles) == 2

    def test_package_resource_loading_failure_falls_back(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging
        from unittest.mock import patch

        caplog.set_level(logging.WARNING)
        with patch("importlib.resources.files", side_effect=OSError("Resource access denied")):
            generator = RandomHeaderGenerator()
            assert len(generator.profiles) == 2
            assert (
                "Failed to load bundled package headers resource: Resource access denied"
                in caplog.text
            )

    def test_profiles_property_returns_defensive_copy(self) -> None:
        generator = RandomHeaderGenerator()
        copy1 = generator.profiles
        copy1.clear()
        assert len(generator.profiles) > 0

    def test_randomization_distribution(self) -> None:
        generator = RandomHeaderGenerator()
        uas = {generator.get_random_user_agent() for _ in range(30)}
        assert len(uas) > 1

    def test_profile_platform_coherence(self) -> None:
        generator = RandomHeaderGenerator()
        for profile in generator.profiles:
            ua = profile.get("User-Agent", "")
            platform = profile.get("Sec-Ch-Ua-Platform", "")

            if platform == '"Windows"':
                assert "Windows" in ua
            elif platform == '"macOS"':
                assert "Macintosh" in ua or "Mac OS X" in ua
            elif platform == '"Linux"':
                assert "Linux" in ua or "X11" in ua
