"""Unit tests for RandomHeaderGenerator adapter.

Verifies loading from bundled package resources, custom path override,
resilient fallback on corruption/missing file, and profile coherence (SPEC/TDD).
"""

from __future__ import annotations

import json
from pathlib import Path

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

    def test_loads_from_custom_file_path(self, tmp_path: Path) -> None:
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

    def test_fallback_when_file_not_found(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "non_existent_pool.json"
        generator = RandomHeaderGenerator(headers_path=missing_file)

        assert len(generator.profiles) >= 1
        headers = generator.get_random_headers()
        assert "User-Agent" in headers

    def test_fallback_when_file_is_invalid_json(self, tmp_path: Path) -> None:
        corrupt_file = tmp_path / "corrupt.json"
        corrupt_file.write_text("{invalid json", encoding="utf-8")

        generator = RandomHeaderGenerator(headers_path=corrupt_file)
        assert len(generator.profiles) >= 1
        headers = generator.get_random_headers()
        assert "User-Agent" in headers

    def test_randomization_distribution(self) -> None:
        generator = RandomHeaderGenerator()
        uas = {generator.get_random_user_agent() for _ in range(30)}
        # Across 30 samples with ~79 profiles, there should be substantial variance
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
