"""Batch source discovery use case for Cresmo Knowledge Engine.

Orchestrates raw transcript ingestion, manifest parsing, concurrent channel resolution,
and lookback feed discovery per ADR-003 and Clean Hexagonal Architecture.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cresmo.application.ports import MediaIngestionPort
from cresmo.domain.value_objects import ChannelFeedQuery
from cresmo.infrastructure.config import CresmoSettings

_CHANNEL_REGEX = re.compile(r"youtube\.com/(?:@|c/|channel/|user/|playlist\?list=)", re.IGNORECASE)
_VIDEO_ID_REGEX = re.compile(
    r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/|/live/|^)([a-zA-Z0-9_-]{8,64})",
    re.IGNORECASE,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass(frozen=True)
class BatchSource:
    """Represents an atomic input item for batch processing."""

    kind: str  # "file" | "url"
    target: str

    @property
    def display_name(self) -> str:
        """Human-readable representation for CLI logs."""
        if self.kind == "file":
            return Path(self.target).name
        return self.target


@dataclass(frozen=True)
class BatchDiscoveryQuery:
    """Encapsulates input parameters for batch source discovery."""

    explicit_manifest: Path | None = None
    manifest_path: Path | None = None
    priority_texts_dir: Path | None = None
    playlist_priority_path: Path | None = None
    playlist_path: Path | None = None
    raw_dir: Path | None = None
    scan_raw: bool = True
    lookback_days: int | None = None
    channel_max_videos: int = 50
    discovery_workers: int | None = None
mutants_x_is_channel_or_playlist_feed__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_is_channel_or_playlist_feed__mutmut)
def is_channel_or_playlist_feed(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_orig(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_1(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = None
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_2(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.upper()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_3(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) or ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_4(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(None)
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_5(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p not in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_6(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("XX/channel/XX", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_7(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/CHANNEL/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_8(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "XX/c/XX", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_9(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/C/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_10(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "XX/user/XX", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_11(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/USER/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_12(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "XX/@XX", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_13(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "XXplaylist?list=XX"))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_14(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "PLAYLIST?LIST="))
    ) and ("watch?v=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_15(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower and "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_16(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("XXwatch?v=XX" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_17(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("WATCH?V=" not in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_18(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" in url_lower or "list=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_19(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "XXlist=XX" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_20(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "LIST=" in url_lower)


def x_is_channel_or_playlist_feed__mutmut_21(url: str) -> bool:
    """Check if a URL represents a channel or playlist rather than a single video."""
    url_lower = url.lower()
    return (
        any(p in url_lower for p in ("/channel/", "/c/", "/user/", "/@", "playlist?list="))
    ) and ("watch?v=" not in url_lower or "list=" not in url_lower)

mutants_x_is_channel_or_playlist_feed__mutmut['_mutmut_orig'] = x_is_channel_or_playlist_feed__mutmut_orig # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_1'] = x_is_channel_or_playlist_feed__mutmut_1 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_2'] = x_is_channel_or_playlist_feed__mutmut_2 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_3'] = x_is_channel_or_playlist_feed__mutmut_3 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_4'] = x_is_channel_or_playlist_feed__mutmut_4 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_5'] = x_is_channel_or_playlist_feed__mutmut_5 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_6'] = x_is_channel_or_playlist_feed__mutmut_6 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_7'] = x_is_channel_or_playlist_feed__mutmut_7 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_8'] = x_is_channel_or_playlist_feed__mutmut_8 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_9'] = x_is_channel_or_playlist_feed__mutmut_9 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_10'] = x_is_channel_or_playlist_feed__mutmut_10 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_11'] = x_is_channel_or_playlist_feed__mutmut_11 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_12'] = x_is_channel_or_playlist_feed__mutmut_12 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_13'] = x_is_channel_or_playlist_feed__mutmut_13 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_14'] = x_is_channel_or_playlist_feed__mutmut_14 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_15'] = x_is_channel_or_playlist_feed__mutmut_15 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_16'] = x_is_channel_or_playlist_feed__mutmut_16 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_17'] = x_is_channel_or_playlist_feed__mutmut_17 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_18'] = x_is_channel_or_playlist_feed__mutmut_18 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_19'] = x_is_channel_or_playlist_feed__mutmut_19 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_20'] = x_is_channel_or_playlist_feed__mutmut_20 # type: ignore # mutmut generated
mutants_x_is_channel_or_playlist_feed__mutmut['x_is_channel_or_playlist_feed__mutmut_21'] = x_is_channel_or_playlist_feed__mutmut_21 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_load_transcript_files__mutmut)
def load_transcript_files(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_orig(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_1(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None and not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_2(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is not None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_3(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_4(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        None
    )


def x_load_transcript_files__mutmut_5(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob(None) if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_6(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("XX*XX") if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_7(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() or p.suffix.lower() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_8(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.upper() in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_9(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() not in {".md", ".txt"}
    )


def x_load_transcript_files__mutmut_10(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {"XX.mdXX", ".txt"}
    )


def x_load_transcript_files__mutmut_11(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".MD", ".txt"}
    )


def x_load_transcript_files__mutmut_12(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", "XX.txtXX"}
    )


def x_load_transcript_files__mutmut_13(directory: Path | None) -> list[Path]:
    """Find all markdown and text files recursively in a directory."""
    if directory is None or not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".TXT"}
    )

mutants_x_load_transcript_files__mutmut['_mutmut_orig'] = x_load_transcript_files__mutmut_orig # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_1'] = x_load_transcript_files__mutmut_1 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_2'] = x_load_transcript_files__mutmut_2 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_3'] = x_load_transcript_files__mutmut_3 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_4'] = x_load_transcript_files__mutmut_4 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_5'] = x_load_transcript_files__mutmut_5 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_6'] = x_load_transcript_files__mutmut_6 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_7'] = x_load_transcript_files__mutmut_7 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_8'] = x_load_transcript_files__mutmut_8 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_9'] = x_load_transcript_files__mutmut_9 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_10'] = x_load_transcript_files__mutmut_10 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_11'] = x_load_transcript_files__mutmut_11 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_12'] = x_load_transcript_files__mutmut_12 # type: ignore # mutmut generated
mutants_x_load_transcript_files__mutmut['x_load_transcript_files__mutmut_13'] = x_load_transcript_files__mutmut_13 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_read_manifest_lines__mutmut)
def read_manifest_lines(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_orig(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_1(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None and not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_2(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is not None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_3(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_4(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = None
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_5(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding=None).splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_6(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="XXutf-8XX").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_7(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="UTF-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_8(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = None
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_9(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned or not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_10(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_11(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith(None):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_12(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("XX#XX"):
            lines.append(cleaned)
    return lines


def x_read_manifest_lines__mutmut_13(path: Path | None) -> list[str]:
    """Read clean non-empty, non-comment lines from a manifest text file."""
    if path is None or not path.is_file():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(None)
    return lines

mutants_x_read_manifest_lines__mutmut['_mutmut_orig'] = x_read_manifest_lines__mutmut_orig # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_1'] = x_read_manifest_lines__mutmut_1 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_2'] = x_read_manifest_lines__mutmut_2 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_3'] = x_read_manifest_lines__mutmut_3 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_4'] = x_read_manifest_lines__mutmut_4 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_5'] = x_read_manifest_lines__mutmut_5 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_6'] = x_read_manifest_lines__mutmut_6 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_7'] = x_read_manifest_lines__mutmut_7 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_8'] = x_read_manifest_lines__mutmut_8 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_9'] = x_read_manifest_lines__mutmut_9 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_10'] = x_read_manifest_lines__mutmut_10 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_11'] = x_read_manifest_lines__mutmut_11 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_12'] = x_read_manifest_lines__mutmut_12 # type: ignore # mutmut generated
mutants_x_read_manifest_lines__mutmut['x_read_manifest_lines__mutmut_13'] = x_read_manifest_lines__mutmut_13 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_extract_raw_file_metadata__mutmut)
def extract_raw_file_metadata(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_orig(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_1(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = None
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_2(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = None
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_3(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding=None)
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_4(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="XXutf-8XX")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_5(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="UTF-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_6(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith(None):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_7(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("XX---XX"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_8(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = None
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_9(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split(None, 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_10(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", None)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_11(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split(2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_12(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", )
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_13(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.rsplit("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_14(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("XX---XX", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_15(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 3)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_16(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) > 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_17(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 4:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_18(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = None
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_19(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[2]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_20(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if "XX:XX" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_21(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" not in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_22(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = None
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_23(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(None, 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_24(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", None)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_25(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_26(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", )
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_27(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.rsplit(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_28(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split("XX:XX", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_29(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 2)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_30(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = None

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_31(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip(None)

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_32(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("XX\"'XX")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_33(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = None
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_34(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") and metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_35(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get(None) or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_36(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("XXchannelXX") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_37(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("CHANNEL") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_38(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get(None)
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_39(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("XXchannel_idXX")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_40(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("CHANNEL_ID")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_41(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(None):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_42(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("XXhttp://XX", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_43(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("HTTP://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_44(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "XXhttps://XX")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_45(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "HTTPS://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_46(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = None
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_47(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["XXchannelXX"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_48(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["CHANNEL"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_49(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith(None):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_50(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("XX@XX"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_51(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = None
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_52(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["XXchannelXX"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_53(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["CHANNEL"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_54(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["channel"] = None
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_55(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["XXchannelXX"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata


def x_extract_raw_file_metadata__mutmut_56(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter attributes from a raw markdown transcript file."""
    metadata: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")

        raw_chan = metadata.get("channel") or metadata.get("channel_id")
        if raw_chan:
            if raw_chan.startswith(("http://", "https://")):
                metadata["channel"] = raw_chan
            elif raw_chan.startswith("@"):
                metadata["channel"] = f"https://www.youtube.com/{raw_chan}"
            else:
                metadata["CHANNEL"] = f"https://www.youtube.com/channel/{raw_chan}"
    except Exception:  # noqa: BLE001
        return {}
    return metadata

mutants_x_extract_raw_file_metadata__mutmut['_mutmut_orig'] = x_extract_raw_file_metadata__mutmut_orig # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_1'] = x_extract_raw_file_metadata__mutmut_1 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_2'] = x_extract_raw_file_metadata__mutmut_2 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_3'] = x_extract_raw_file_metadata__mutmut_3 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_4'] = x_extract_raw_file_metadata__mutmut_4 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_5'] = x_extract_raw_file_metadata__mutmut_5 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_6'] = x_extract_raw_file_metadata__mutmut_6 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_7'] = x_extract_raw_file_metadata__mutmut_7 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_8'] = x_extract_raw_file_metadata__mutmut_8 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_9'] = x_extract_raw_file_metadata__mutmut_9 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_10'] = x_extract_raw_file_metadata__mutmut_10 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_11'] = x_extract_raw_file_metadata__mutmut_11 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_12'] = x_extract_raw_file_metadata__mutmut_12 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_13'] = x_extract_raw_file_metadata__mutmut_13 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_14'] = x_extract_raw_file_metadata__mutmut_14 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_15'] = x_extract_raw_file_metadata__mutmut_15 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_16'] = x_extract_raw_file_metadata__mutmut_16 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_17'] = x_extract_raw_file_metadata__mutmut_17 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_18'] = x_extract_raw_file_metadata__mutmut_18 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_19'] = x_extract_raw_file_metadata__mutmut_19 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_20'] = x_extract_raw_file_metadata__mutmut_20 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_21'] = x_extract_raw_file_metadata__mutmut_21 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_22'] = x_extract_raw_file_metadata__mutmut_22 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_23'] = x_extract_raw_file_metadata__mutmut_23 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_24'] = x_extract_raw_file_metadata__mutmut_24 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_25'] = x_extract_raw_file_metadata__mutmut_25 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_26'] = x_extract_raw_file_metadata__mutmut_26 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_27'] = x_extract_raw_file_metadata__mutmut_27 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_28'] = x_extract_raw_file_metadata__mutmut_28 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_29'] = x_extract_raw_file_metadata__mutmut_29 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_30'] = x_extract_raw_file_metadata__mutmut_30 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_31'] = x_extract_raw_file_metadata__mutmut_31 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_32'] = x_extract_raw_file_metadata__mutmut_32 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_33'] = x_extract_raw_file_metadata__mutmut_33 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_34'] = x_extract_raw_file_metadata__mutmut_34 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_35'] = x_extract_raw_file_metadata__mutmut_35 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_36'] = x_extract_raw_file_metadata__mutmut_36 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_37'] = x_extract_raw_file_metadata__mutmut_37 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_38'] = x_extract_raw_file_metadata__mutmut_38 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_39'] = x_extract_raw_file_metadata__mutmut_39 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_40'] = x_extract_raw_file_metadata__mutmut_40 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_41'] = x_extract_raw_file_metadata__mutmut_41 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_42'] = x_extract_raw_file_metadata__mutmut_42 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_43'] = x_extract_raw_file_metadata__mutmut_43 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_44'] = x_extract_raw_file_metadata__mutmut_44 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_45'] = x_extract_raw_file_metadata__mutmut_45 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_46'] = x_extract_raw_file_metadata__mutmut_46 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_47'] = x_extract_raw_file_metadata__mutmut_47 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_48'] = x_extract_raw_file_metadata__mutmut_48 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_49'] = x_extract_raw_file_metadata__mutmut_49 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_50'] = x_extract_raw_file_metadata__mutmut_50 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_51'] = x_extract_raw_file_metadata__mutmut_51 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_52'] = x_extract_raw_file_metadata__mutmut_52 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_53'] = x_extract_raw_file_metadata__mutmut_53 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_54'] = x_extract_raw_file_metadata__mutmut_54 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_55'] = x_extract_raw_file_metadata__mutmut_55 # type: ignore # mutmut generated
mutants_x_extract_raw_file_metadata__mutmut['x_extract_raw_file_metadata__mutmut_56'] = x_extract_raw_file_metadata__mutmut_56 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut: MutantDict = {}  # type: ignore
mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut: MutantDict = {}  # type: ignore
mutants_xǁ_BatchSourceAccumulatorǁhas_seen__mutmut: MutantDict = {}  # type: ignore


class _BatchSourceAccumulator:
    """Encapsulates deduplication and ordered accumulation of batch sources."""

    @_mutmut_mutated(mutants_xǁ_BatchSourceAccumulatorǁ__init____mutmut)
    def __init__(self) -> None:
        self.sources: list[BatchSource] = []
        self.seen_vids: set[str] = set()

    def xǁ_BatchSourceAccumulatorǁ__init____mutmut_orig(self) -> None:
        self.sources: list[BatchSource] = []
        self.seen_vids: set[str] = set()

    def xǁ_BatchSourceAccumulatorǁ__init____mutmut_1(self) -> None:
        self.sources: list[BatchSource] = None
        self.seen_vids: set[str] = set()

    def xǁ_BatchSourceAccumulatorǁ__init____mutmut_2(self) -> None:
        self.sources: list[BatchSource] = []
        self.seen_vids: set[str] = None

    @_mutmut_mutated(mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut)
    def add_source(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(kind=kind, target=target))
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(target)

    def xǁ_BatchSourceAccumulatorǁadd_source__mutmut_orig(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(kind=kind, target=target))
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(target)

    def xǁ_BatchSourceAccumulatorǁadd_source__mutmut_1(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(None)
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(target)

    def xǁ_BatchSourceAccumulatorǁadd_source__mutmut_2(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(kind=None, target=target))
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(target)

    def xǁ_BatchSourceAccumulatorǁadd_source__mutmut_3(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(kind=kind, target=None))
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(target)

    def xǁ_BatchSourceAccumulatorǁadd_source__mutmut_4(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(target=target))
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(target)

    def xǁ_BatchSourceAccumulatorǁadd_source__mutmut_5(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(kind=kind, ))
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(target)

    def xǁ_BatchSourceAccumulatorǁadd_source__mutmut_6(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(kind=kind, target=target))
        if vid:
            self.seen_vids.add(None)
        else:
            self.register_identifier(target)

    def xǁ_BatchSourceAccumulatorǁadd_source__mutmut_7(self, kind: str, target: str, vid: str | None = None) -> None:
        """Append a source and register its identifier for deduplication."""
        self.sources.append(BatchSource(kind=kind, target=target))
        if vid:
            self.seen_vids.add(vid)
        else:
            self.register_identifier(None)

    @_mutmut_mutated(mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut)
    def register_identifier(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            self.seen_vids.add(m.group(1))
        else:
            self.seen_vids.add(Path(target_str).stem)

    def xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_orig(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            self.seen_vids.add(m.group(1))
        else:
            self.seen_vids.add(Path(target_str).stem)

    def xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_1(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = None
        if m:
            self.seen_vids.add(m.group(1))
        else:
            self.seen_vids.add(Path(target_str).stem)

    def xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_2(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(None)
        if m:
            self.seen_vids.add(m.group(1))
        else:
            self.seen_vids.add(Path(target_str).stem)

    def xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_3(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            self.seen_vids.add(None)
        else:
            self.seen_vids.add(Path(target_str).stem)

    def xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_4(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            self.seen_vids.add(m.group(None))
        else:
            self.seen_vids.add(Path(target_str).stem)

    def xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_5(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            self.seen_vids.add(m.group(2))
        else:
            self.seen_vids.add(Path(target_str).stem)

    def xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_6(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            self.seen_vids.add(m.group(1))
        else:
            self.seen_vids.add(None)

    def xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_7(self, target_str: str) -> None:
        """Register video ID or path stem into the deduplication set."""
        m = _VIDEO_ID_REGEX.search(target_str)
        if m:
            self.seen_vids.add(m.group(1))
        else:
            self.seen_vids.add(Path(None).stem)

    @_mutmut_mutated(mutants_xǁ_BatchSourceAccumulatorǁhas_seen__mutmut)
    def has_seen(self, identifier: str) -> bool:
        """Check if an identifier (video ID or stem) was already registered."""
        return identifier in self.seen_vids

    def xǁ_BatchSourceAccumulatorǁhas_seen__mutmut_orig(self, identifier: str) -> bool:
        """Check if an identifier (video ID or stem) was already registered."""
        return identifier in self.seen_vids

    def xǁ_BatchSourceAccumulatorǁhas_seen__mutmut_1(self, identifier: str) -> bool:
        """Check if an identifier (video ID or stem) was already registered."""
        return identifier not in self.seen_vids

mutants_xǁ_BatchSourceAccumulatorǁ__init____mutmut['_mutmut_orig'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁ__init____mutmut['xǁ_BatchSourceAccumulatorǁ__init____mutmut_1'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁ__init____mutmut['xǁ_BatchSourceAccumulatorǁ__init____mutmut_2'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁ__init____mutmut_2 # type: ignore # mutmut generated

mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut['_mutmut_orig'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁadd_source__mutmut_orig # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut['xǁ_BatchSourceAccumulatorǁadd_source__mutmut_1'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁadd_source__mutmut_1 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut['xǁ_BatchSourceAccumulatorǁadd_source__mutmut_2'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁadd_source__mutmut_2 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut['xǁ_BatchSourceAccumulatorǁadd_source__mutmut_3'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁadd_source__mutmut_3 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut['xǁ_BatchSourceAccumulatorǁadd_source__mutmut_4'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁadd_source__mutmut_4 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut['xǁ_BatchSourceAccumulatorǁadd_source__mutmut_5'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁadd_source__mutmut_5 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut['xǁ_BatchSourceAccumulatorǁadd_source__mutmut_6'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁadd_source__mutmut_6 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁadd_source__mutmut['xǁ_BatchSourceAccumulatorǁadd_source__mutmut_7'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁadd_source__mutmut_7 # type: ignore # mutmut generated

mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut['_mutmut_orig'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_orig # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut['xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_1'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_1 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut['xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_2'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_2 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut['xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_3'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_3 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut['xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_4'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_4 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut['xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_5'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_5 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut['xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_6'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_6 # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut['xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_7'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁregister_identifier__mutmut_7 # type: ignore # mutmut generated

mutants_xǁ_BatchSourceAccumulatorǁhas_seen__mutmut['_mutmut_orig'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁhas_seen__mutmut_orig # type: ignore # mutmut generated
mutants_xǁ_BatchSourceAccumulatorǁhas_seen__mutmut['xǁ_BatchSourceAccumulatorǁhas_seen__mutmut_1'] = _BatchSourceAccumulator.xǁ_BatchSourceAccumulatorǁhas_seen__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut: MutantDict = {}  # type: ignore


class DiscoverBatchSourcesUseCase:
    """Application use case orchestrating batch discovery of files, seeds, and channel feeds."""

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut)
    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        settings: CresmoSettings | None = None,
        progress_callback: Callable[[str], object] | None = None,
    ) -> None:
        """Initialize use case with injected media ingestion adapter and optional settings."""
        self.media_ingestion_port = media_ingestion_port
        self.settings = settings or CresmoSettings()
        self.progress_callback = progress_callback

    def xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_orig(
        self,
        media_ingestion_port: MediaIngestionPort,
        settings: CresmoSettings | None = None,
        progress_callback: Callable[[str], object] | None = None,
    ) -> None:
        """Initialize use case with injected media ingestion adapter and optional settings."""
        self.media_ingestion_port = media_ingestion_port
        self.settings = settings or CresmoSettings()
        self.progress_callback = progress_callback

    def xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_1(
        self,
        media_ingestion_port: MediaIngestionPort,
        settings: CresmoSettings | None = None,
        progress_callback: Callable[[str], object] | None = None,
    ) -> None:
        """Initialize use case with injected media ingestion adapter and optional settings."""
        self.media_ingestion_port = None
        self.settings = settings or CresmoSettings()
        self.progress_callback = progress_callback

    def xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_2(
        self,
        media_ingestion_port: MediaIngestionPort,
        settings: CresmoSettings | None = None,
        progress_callback: Callable[[str], object] | None = None,
    ) -> None:
        """Initialize use case with injected media ingestion adapter and optional settings."""
        self.media_ingestion_port = media_ingestion_port
        self.settings = None
        self.progress_callback = progress_callback

    def xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_3(
        self,
        media_ingestion_port: MediaIngestionPort,
        settings: CresmoSettings | None = None,
        progress_callback: Callable[[str], object] | None = None,
    ) -> None:
        """Initialize use case with injected media ingestion adapter and optional settings."""
        self.media_ingestion_port = media_ingestion_port
        self.settings = settings and CresmoSettings()
        self.progress_callback = progress_callback

    def xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_4(
        self,
        media_ingestion_port: MediaIngestionPort,
        settings: CresmoSettings | None = None,
        progress_callback: Callable[[str], object] | None = None,
    ) -> None:
        """Initialize use case with injected media ingestion adapter and optional settings."""
        self.media_ingestion_port = media_ingestion_port
        self.settings = settings or CresmoSettings()
        self.progress_callback = None

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut)
    def _notify(self, message: str) -> None:
        """Emit progress message if a progress callback was provided."""
        if self.progress_callback is not None:
            self.progress_callback(message)

    def xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut_orig(self, message: str) -> None:
        """Emit progress message if a progress callback was provided."""
        if self.progress_callback is not None:
            self.progress_callback(message)

    def xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut_1(self, message: str) -> None:
        """Emit progress message if a progress callback was provided."""
        if self.progress_callback is None:
            self.progress_callback(message)

    def xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut_2(self, message: str) -> None:
        """Emit progress message if a progress callback was provided."""
        if self.progress_callback is not None:
            self.progress_callback(None)

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut)
    def execute(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_orig(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_1(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = None
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_2(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query and BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_3(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_4(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(None)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_5(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = None
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_6(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            None, acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_7(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), None
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_8(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_9(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_10(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir and getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_11(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(None, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_12(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, None, None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_13(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr("priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_14(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_15(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", ), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_16(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "XXpriority_texts_dirXX", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_17(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "PRIORITY_TEXTS_DIR", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_18(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            None, acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_19(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), None
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_20(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_21(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_22(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path and getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_23(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(None, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_24(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, None, None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_25(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr("playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_26(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_27(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", ), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_28(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "XXplaylist_priority_pathXX", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_29(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "PLAYLIST_PRIORITY_PATH", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_30(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = None
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_31(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir and getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_32(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(None, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_33(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, None, Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_34(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", None)
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_35(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr("raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_36(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_37(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", )
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_38(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "XXraw_dirXX", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_39(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "RAW_DIR", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_40(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path(None))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_41(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("XXdata/rawXX"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_42(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("DATA/RAW"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_43(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = None

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_44(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(None, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_45(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, None, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_46(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, None)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_47(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_48(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_49(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, )

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_50(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = None
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_51(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path and getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_52(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path and q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_53(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(None, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_54(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, None, Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_55(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", None)
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_56(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr("playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_57(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_58(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", )
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_59(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "XXplaylist_pathXX", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_60(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "PLAYLIST_PATH", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_61(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path(None))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_62(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("XXdata/playlist.txtXX"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_63(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("DATA/PLAYLIST.TXT"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_64(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = None

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_65(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            None, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_66(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, None, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_67(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, None
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_68(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_69(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_70(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_71(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_72(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = None
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_73(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_74(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = None

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_75(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_76(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                None, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_77(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, None, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_78(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, None, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_79(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, None
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_80(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_81(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_82(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_83(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_84(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                None, lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_85(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, None, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_86(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, None, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_87(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, None, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_88(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, None
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_89(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                lookback, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_90(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, q.channel_max_videos, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_91(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, workers, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_92(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, acc
            )

        return acc.sources

    def xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_93(self, query: BatchDiscoveryQuery | None = None) -> list[BatchSource]:
        """Discover and consolidate batch sources from local lake, seeds, and channel feeds.

        Discovery pipeline flow:
        - When explicit manifest is passed, only that manifest is loaded.
        - Otherwise:
          - Priority text/markdown files (bypasses Stage 1 STT).
          - Priority URLs from playlist-priority.txt.
          - Existing raw transcripts in raw_dir lake.
          - Direct video URLs from playlist.txt.
          - Concurrent discovery of channel feeds (explicit + discovered by videos).
        """
        q = query or BatchDiscoveryQuery()
        if q.explicit_manifest is not None:
            return self._load_explicit_manifest(q.explicit_manifest)

        acc = _BatchSourceAccumulator()
        self._collect_priority_texts(
            q.priority_texts_dir or getattr(self.settings, "priority_texts_dir", None), acc
        )
        self._collect_priority_urls(
            q.playlist_priority_path or getattr(self.settings, "playlist_priority_path", None), acc
        )

        raw_dir = q.raw_dir or getattr(self.settings, "raw_dir", Path("data/raw"))
        local_channels = self._scan_raw_lake(raw_dir, q.scan_raw, acc)

        playlist_path = (
            q.playlist_path
            or q.manifest_path
            or getattr(self.settings, "playlist_path", Path("data/playlist.txt"))
        )
        channels_to_probe, remote_videos, probed_channels = self._classify_seeds(
            playlist_path, local_channels, acc
        )

        if self.media_ingestion_port is not None:
            workers = (
                q.discovery_workers
                if q.discovery_workers is not None
                else self.settings.channel_discovery_workers
            )
            lookback = (
                q.lookback_days if q.lookback_days is not None else self.settings.days_lookback
            )

            self._resolve_remote_channels(
                remote_videos, workers, probed_channels, channels_to_probe
            )
            self._probe_channel_feeds(
                channels_to_probe, lookback, q.channel_max_videos, workers, )

        return acc.sources

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut)
    def _load_explicit_manifest(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="url", target=u) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_orig(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="url", target=u) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_1(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = None
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="url", target=u) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_2(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(None)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="url", target=u) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_3(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(None)
        return [BatchSource(kind="url", target=u) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_4(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind=None, target=u) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_5(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="url", target=None) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_6(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(target=u) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_7(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="url", ) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_8(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="XXurlXX", target=u) for u in urls]

    def xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_9(self, manifest_path: Path) -> list[BatchSource]:
        """Load and return sources directly from an explicit manifest override."""
        urls = read_manifest_lines(manifest_path)
        if urls:
            self._notify(f"[manifest] Loaded {len(urls)} URLs from {manifest_path.name}\n")
        return [BatchSource(kind="URL", target=u) for u in urls]

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut)
    def _collect_priority_texts(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="file", target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_orig(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="file", target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_1(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = None
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="file", target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_2(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(None)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="file", target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_3(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = None
            acc.add_source(kind="file", target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_4(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(None)
            acc.add_source(kind="file", target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_5(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind=None, target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_6(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="file", target=None)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_7(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_8(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="file", )

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_9(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="XXfileXX", target=resolved_pf)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_10(
        self, priority_texts_dir: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect local priority text/markdown files that bypass Stage 1 transcription."""
        priority_files = load_transcript_files(priority_texts_dir)
        for pf in priority_files:
            resolved_pf = str(pf.resolve())
            acc.add_source(kind="FILE", target=resolved_pf)

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut)
    def _collect_priority_urls(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            acc.add_source(kind="url", target=pu)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_orig(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            acc.add_source(kind="url", target=pu)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_1(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = None
        for pu in priority_urls:
            acc.add_source(kind="url", target=pu)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_2(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(None)
        for pu in priority_urls:
            acc.add_source(kind="url", target=pu)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_3(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            acc.add_source(kind=None, target=pu)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_4(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            acc.add_source(kind="url", target=None)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_5(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            acc.add_source(target=pu)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_6(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            acc.add_source(kind="url", )

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_7(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            acc.add_source(kind="XXurlXX", target=pu)

    def xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_8(
        self, playlist_priority_path: Path | None, acc: _BatchSourceAccumulator
    ) -> None:
        """Collect priority URLs scheduled for immediate processing."""
        priority_urls = read_manifest_lines(playlist_priority_path)
        for pu in priority_urls:
            acc.add_source(kind="URL", target=pu)

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut)
    def _scan_raw_lake(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_orig(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_1(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = None
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_2(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_3(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") or raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_4(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(None, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_5(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, None) and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_6(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr("is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_7(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, ) and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_8(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "XXis_dirXX") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_9(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "IS_DIR") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_10(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = None
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_11(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(None)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_12(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = None
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_13(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = None
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_14(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(None)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_15(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = None
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_16(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get(None)
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_17(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("XXvideo_idXX")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_18(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("VIDEO_ID")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_19(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = None
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_20(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get(None)
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_21(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("XXchannelXX")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_22(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("CHANNEL")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_23(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = None
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_24(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front and stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_25(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = None
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_26(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = None

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_27(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) or not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_28(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw or not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_29(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_30(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(None) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_31(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_32(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(None):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_33(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = None
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_34(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(None)
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_35(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind=None, target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_36(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=None, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_37(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=None)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_38(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_39(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_40(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, )
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_41(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="XXfileXX", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_42(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="FILE", target=resolved_rf, vid=stem)
                acc.seen_vids.add(canonical_vid)

        return local_video_to_channel

    def xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_43(
        self, raw_dir: Path | None, scan_raw: bool, acc: _BatchSourceAccumulator
    ) -> dict[str, str]:
        """Scan raw transcripts lake, extract channel metadata, and register existing files."""
        local_video_to_channel: dict[str, str] = {}
        if not (hasattr(raw_dir, "is_dir") and raw_dir.is_dir()):
            return local_video_to_channel

        raw_files = load_transcript_files(raw_dir)
        for rf in raw_files:
            stem = rf.stem
            meta = extract_raw_file_metadata(rf)
            vid_front = meta.get("video_id")
            chan_url = meta.get("channel")
            canonical_vid = vid_front or stem
            if chan_url:
                local_video_to_channel[canonical_vid] = chan_url
                local_video_to_channel[stem] = chan_url

            if scan_raw and not acc.has_seen(stem) and not acc.has_seen(canonical_vid):
                resolved_rf = str(rf.resolve())
                acc.add_source(kind="file", target=resolved_rf, vid=stem)
                acc.seen_vids.add(None)

        return local_video_to_channel

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut)
    def _classify_seeds(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_orig(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_1(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = None
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_2(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = None
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_3(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = None

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_4(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_5(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(None)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_6(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(None)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_7(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = None
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_8(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(None)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_9(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(None):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_10(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_11(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(None)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_12(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(None)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_13(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = None
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_14(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(None)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_15(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_16(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(None) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_17(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(2) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_18(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_19(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid or acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_20(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(None)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_21(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind=None, target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_22(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=None, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_23(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=None)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_24(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_25(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_26(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, )

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_27(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="XXurlXX", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_28(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="URL", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_29(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_30(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(None) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_31(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_32(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(None)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_33(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(None)
                else:
                    remote_videos.append(mu)

        return channels_to_probe, remote_videos, probed_channels

    def xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_34(
        self,
        playlist_path: Path | None,
        local_channels: dict[str, str],
        acc: _BatchSourceAccumulator,
    ) -> tuple[list[str], list[str], set[str]]:
        """Classify seed playlist entries into direct video URLs, feeds, and channel lookups."""
        channels_to_probe: list[str] = []
        probed_channels: set[str] = set()
        remote_videos: list[str] = []

        # Seed channels discovered from the local raw lake
        for c_url in local_channels.values():
            if c_url not in probed_channels:
                probed_channels.add(c_url)
                channels_to_probe.append(c_url)

        main_urls = read_manifest_lines(playlist_path)
        for mu in main_urls:
            if is_channel_or_playlist_feed(mu):
                if mu not in probed_channels:
                    probed_channels.add(mu)
                    channels_to_probe.append(mu)
            else:
                m = _VIDEO_ID_REGEX.search(mu)
                vid = m.group(1) if m else None
                if not (vid and acc.has_seen(vid)):
                    acc.add_source(kind="url", target=mu, vid=vid)

                local_chan = local_channels.get(vid) if vid else None
                if local_chan:
                    if local_chan not in probed_channels:
                        probed_channels.add(local_chan)
                        channels_to_probe.append(local_chan)
                else:
                    remote_videos.append(None)

        return channels_to_probe, remote_videos, probed_channels

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut)
    def _resolve_remote_channels(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_orig(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_1(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_2(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(None)
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_3(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = None
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_4(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(None, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_5(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, None)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_6(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_7(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, )
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_8(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(2, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_9(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(None, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_10(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, None))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_11(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_12(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, ))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_13(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=None) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_14(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = None
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_15(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(None, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_16(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, None): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_17(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_18(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, ): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_19(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(None):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_20(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = None
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_21(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan or resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_22(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_23(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(None)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_24(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(None)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_25(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = None
                    self._notify(
                        f"[crawler] Warning: Failed to resolve channel for {failed_vu}: {exc}\n"
                    )

    def xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_26(
        self,
        videos: list[str],
        workers: int,
        probed_channels: set[str],
        channels_to_probe: list[str],
    ) -> None:
        """Resolve parent channels concurrently for seed videos missing local metadata."""
        if not videos:
            return

        self._notify(f"[crawler] Resolving parent channels for {len(videos)} seed videos...\n")
        max_workers = max(1, min(workers, len(videos)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_vurl = {
                executor.submit(self.media_ingestion_port.extract_channel_url_from_video, vu): vu
                for vu in videos
            }
            for fut in as_completed(future_to_vurl):
                try:
                    resolved_chan = fut.result()
                    if resolved_chan and resolved_chan not in probed_channels:
                        probed_channels.add(resolved_chan)
                        channels_to_probe.append(resolved_chan)
                except Exception as exc:  # noqa: BLE001
                    failed_vu = future_to_vurl[fut]
                    self._notify(
                        None
                    )

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut)
    def _probe_channel_feeds(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_orig(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_1(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_2(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            None
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_3(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = None
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_4(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) + timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_5(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(None) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_6(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=None)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_7(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_8(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(None, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_9(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, None)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_10(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_11(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_12(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(2, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_13(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(None, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_14(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, None))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_15(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_16(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, ))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_17(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=None) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_18(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = None
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_19(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    None, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_20(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, None, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_21(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, None, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_22(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, None, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_23(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, None
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_24(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_25(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_26(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_27(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_28(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_29(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(None):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_30(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = None
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_31(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = None
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_32(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(None)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_33(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = None
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_34(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(None) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_35(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(2) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_36(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_37(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(None):
                        acc.add_source(kind="url", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_38(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind=None, target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_39(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=None, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_40(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, vid=None)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_41(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_42(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_43(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="url", target=d_url, )

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_44(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="XXurlXX", target=d_url, vid=vid)

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_45(
        self,
        channels: list[str],
        lookback_days: int,
        max_videos: int,
        workers: int,
        acc: _BatchSourceAccumulator,
    ) -> None:
        """Probe recent video uploads across unique channel feeds concurrently."""
        if not channels:
            return

        self._notify(
            f"[crawler] Discovering recent videos across {len(channels)} channels "
            f"(lookback: {lookback_days}d, workers: {workers})...\n"
        )
        cutoff = datetime.now(UTC) - timedelta(days=lookback_days)
        max_workers = max(1, min(workers, len(channels)))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._probe_single_channel_feed, u, lookback_days, max_videos, cutoff
                ): u
                for u in channels
            }
            for future in as_completed(future_to_url):
                discovered_urls = future.result()
                for d_url in discovered_urls:
                    m = _VIDEO_ID_REGEX.search(d_url)
                    vid = m.group(1) if m else d_url
                    if not acc.has_seen(vid):
                        acc.add_source(kind="URL", target=d_url, vid=vid)

    @_mutmut_mutated(mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut)
    def _probe_single_channel_feed(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_orig(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_1(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = None
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_2(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(None) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_3(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("XXhttp://XX", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_4(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("HTTP://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_5(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "XXhttps://XX")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_6(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "HTTPS://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_7(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = None
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_8(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=None,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_9(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=None,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_10(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=None,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_11(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_12(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_13(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_14(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = None
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_15(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(None)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_16(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = None
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_17(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = None
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_18(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(None, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_19(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, None, None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_20(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr("published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_21(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_22(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", )
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_23(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "XXpublished_atXX", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_24(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "PUBLISHED_AT", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_25(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_26(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is not None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_27(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = None
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_28(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=None)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_29(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub <= cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_30(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        break
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_31(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = None
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_32(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(None, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_33(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, None, getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_34(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", None)
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_35(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr("media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_36(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_37(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", )
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_38(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "XXmedia_urlXX", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_39(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "MEDIA_URL", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_40(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(None, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_41(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, None, ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_42(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", None))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_43(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr("url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_44(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_45(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_46(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "XXurlXX", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_47(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "URL", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_48(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", "XXXX"))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_49(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(None)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(f"[crawler] Warning: Failed to probe {chan_url}: {exc}\n")
            return []

    def xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_50(
        self, chan_url: str, lookback_days: int, max_videos: int, cutoff: datetime
    ) -> list[str]:
        """Fetch and filter recent uploads within lookback window for a single channel feed."""
        formatted_url = (
            chan_url if chan_url.startswith(("http://", "https://")) else f"https://{chan_url}"
        )
        feed_query = ChannelFeedQuery(
            channel_url=formatted_url,
            lookback_days=lookback_days,
            max_videos=max_videos,
        )
        try:
            discovered = self.media_ingestion_port.discover_channel_feed(feed_query)
            in_window: list[str] = []
            for item in discovered:
                pub = getattr(item, "published_at", None)
                if pub is not None:
                    if pub.tzinfo is None:
                        pub = pub.replace(tzinfo=UTC)
                    if pub < cutoff:
                        continue
                u = getattr(item, "media_url", getattr(item, "url", ""))
                if u:
                    in_window.append(u)
            return in_window
        except Exception as exc:  # noqa: BLE001
            self._notify(None)
            return []

mutants_xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut['xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut['xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut['xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut['xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ__init____mutmut_4 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_notify__mutmut_2 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_9'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_10'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_11'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_12'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_13'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_14'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_15'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_16'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_17'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_18'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_19'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_20'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_21'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_22'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_23'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_24'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_25'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_26'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_26 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_27'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_27 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_28'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_28 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_29'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_29 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_30'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_30 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_31'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_31 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_32'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_32 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_33'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_33 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_34'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_34 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_35'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_35 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_36'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_36 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_37'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_37 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_38'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_38 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_39'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_39 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_40'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_40 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_41'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_41 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_42'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_42 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_43'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_43 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_44'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_44 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_45'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_45 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_46'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_46 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_47'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_47 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_48'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_48 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_49'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_49 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_50'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_50 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_51'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_51 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_52'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_52 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_53'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_53 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_54'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_54 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_55'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_55 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_56'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_56 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_57'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_57 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_58'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_58 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_59'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_59 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_60'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_60 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_61'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_61 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_62'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_62 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_63'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_63 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_64'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_64 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_65'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_65 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_66'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_66 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_67'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_67 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_68'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_68 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_69'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_69 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_70'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_70 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_71'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_71 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_72'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_72 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_73'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_73 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_74'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_74 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_75'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_75 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_76'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_76 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_77'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_77 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_78'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_78 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_79'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_79 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_80'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_80 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_81'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_81 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_82'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_82 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_83'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_83 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_84'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_84 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_85'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_85 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_86'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_86 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_87'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_87 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_88'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_88 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_89'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_89 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_90'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_90 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_91'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_91 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_92'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_92 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut['xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_93'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁexecute__mutmut_93 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_9'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_load_explicit_manifest__mutmut_9 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_9'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_10'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_texts__mutmut_10 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_collect_priority_urls__mutmut_8 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_9'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_10'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_11'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_12'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_13'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_14'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_15'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_16'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_17'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_18'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_19'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_20'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_21'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_22'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_23'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_24'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_25'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_26'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_26 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_27'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_27 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_28'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_28 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_29'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_29 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_30'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_30 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_31'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_31 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_32'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_32 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_33'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_33 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_34'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_34 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_35'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_35 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_36'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_36 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_37'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_37 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_38'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_38 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_39'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_39 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_40'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_40 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_41'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_41 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_42'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_42 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_43'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_scan_raw_lake__mutmut_43 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_9'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_10'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_11'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_12'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_13'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_14'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_15'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_16'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_17'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_18'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_19'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_20'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_21'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_22'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_23'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_24'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_25'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_26'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_26 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_27'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_27 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_28'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_28 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_29'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_29 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_30'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_30 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_31'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_31 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_32'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_32 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_33'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_33 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_34'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_classify_seeds__mutmut_34 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_9'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_10'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_11'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_12'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_13'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_14'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_15'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_16'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_17'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_18'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_19'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_20'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_21'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_22'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_23'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_24'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_25'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_26'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_resolve_remote_channels__mutmut_26 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_9'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_10'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_11'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_12'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_13'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_14'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_15'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_16'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_17'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_18'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_19'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_20'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_21'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_22'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_23'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_24'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_25'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_26'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_26 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_27'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_27 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_28'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_28 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_29'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_29 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_30'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_30 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_31'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_31 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_32'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_32 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_33'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_33 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_34'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_34 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_35'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_35 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_36'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_36 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_37'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_37 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_38'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_38 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_39'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_39 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_40'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_40 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_41'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_41 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_42'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_42 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_43'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_43 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_44'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_44 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_45'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_channel_feeds__mutmut_45 # type: ignore # mutmut generated

mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['_mutmut_orig'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_1'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_2'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_3'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_4'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_5'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_6'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_7'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_8'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_9'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_10'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_11'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_12'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_13'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_14'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_15'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_16'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_17'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_18'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_19'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_20'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_21'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_22'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_23'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_24'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_25'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_26'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_26 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_27'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_27 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_28'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_28 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_29'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_29 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_30'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_30 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_31'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_31 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_32'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_32 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_33'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_33 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_34'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_34 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_35'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_35 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_36'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_36 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_37'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_37 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_38'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_38 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_39'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_39 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_40'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_40 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_41'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_41 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_42'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_42 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_43'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_43 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_44'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_44 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_45'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_45 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_46'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_46 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_47'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_47 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_48'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_48 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_49'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_49 # type: ignore # mutmut generated
mutants_xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut['xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_50'] = DiscoverBatchSourcesUseCase.xǁDiscoverBatchSourcesUseCaseǁ_probe_single_channel_feed__mutmut_50 # type: ignore # mutmut generated
