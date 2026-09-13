"""Randomized Browser Request Header Generator.

Provides dynamic, coherent browser fingerprints (User-Agent, Accept, and
Client Hints like Sec-Ch-Ua, Sec-Ch-Ua-Platform, Sec-Ch-Ua-Mobile) decoupled
from source code, loaded via importlib.resources or custom external path.
"""

from __future__ import annotations

import importlib.resources
import json
import logging
import random
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_FALLBACK_PROFILES: tuple[dict[str, str], ...] = (
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="124", "Google Chrome";v="124"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    },
    {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    },
)


class RandomHeaderGenerator:
    """Decoupled browser header generator and rotator.

    Loads a catalog of realistic browser profiles and emits randomized,
    coherent request headers to mitigate scraping and WAF heuristics.
    """

    def __init__(self, headers_path: Path | None = None) -> None:
        """Initialize the generator with bundled or custom profile pool.

        Args:
            headers_path: Optional explicit filesystem path to a JSON pool.
                If None, loads the default package resource headers_pool.json.
        """
        self._profiles: list[dict[str, str]] = []
        self._load_profiles(headers_path)

    @property
    def profiles(self) -> list[dict[str, str]]:
        """Return immutable view of loaded browser profiles."""
        return list(self._profiles)

    def get_random_headers(self) -> dict[str, str]:
        """Return a fresh copy of a randomly selected coherent browser header dict.

        Returns:
            Dictionary containing User-Agent, Accept, and matching Client Hints.
        """
        if not self._profiles:
            return dict(_DEFAULT_FALLBACK_PROFILES[0])
        chosen = random.choice(self._profiles)
        return dict(chosen)

    def get_random_user_agent(self) -> str:
        """Return a random browser User-Agent string.

        Returns:
            Selected User-Agent string.
        """
        headers = self.get_random_headers()
        return headers.get("User-Agent", _DEFAULT_FALLBACK_PROFILES[0]["User-Agent"])

    def _load_profiles(self, headers_path: Path | None) -> None:
        """Load and parse browser profiles with graceful fallback."""
        if headers_path is not None:
            self._load_from_path(headers_path)
        else:
            self._load_from_package_resource()

        if not self._profiles:
            logger.warning(
                "Browser header profiles pool was empty or failed to load. "
                "Falling back to embedded default profiles."
            )
            self._profiles = [dict(p) for p in _DEFAULT_FALLBACK_PROFILES]

    def _load_from_path(self, path: Path) -> None:
        """Load JSON profiles from an explicit path."""
        try:
            if not path.is_file():
                logger.warning("Custom headers path '%s' does not exist.", path)
                return
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            self._parse_and_set_profiles(data)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load custom headers from '%s': %s", path, exc)

    def _load_from_package_resource(self) -> None:
        """Load JSON profiles from bundled cresmo.infrastructure.resources package."""
        try:
            resource_file = importlib.resources.files("cresmo.infrastructure.resources").joinpath(
                "headers_pool.json"
            )
            with resource_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self._parse_and_set_profiles(data)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load bundled package headers resource: %s", exc)

    def _parse_and_set_profiles(self, data: Any) -> None:
        """Validate and set profiles from decoded JSON data."""
        if not isinstance(data, list):
            logger.warning("Headers pool payload must be a JSON array.")
            return

        valid_profiles: list[dict[str, str]] = []
        for item in data:
            if isinstance(item, dict) and "User-Agent" in item:
                # Ensure all header values are strings
                sanitized = {str(k): str(v) for k, v in item.items()}
                valid_profiles.append(sanitized)

        if valid_profiles:
            self._profiles = valid_profiles
            logger.debug("Successfully loaded %d browser header profiles.", len(self._profiles))
