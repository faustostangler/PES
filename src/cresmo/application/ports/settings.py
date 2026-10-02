"""Application Pipeline Settings Protocol and default in-memory implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class PipelineSettingsProtocol(Protocol):
    """Protocol defining runtime settings required by application use cases and pipeline."""

    @property
    def raw_index_max_chars(self) -> int: ...

    @property
    def raw_index_temperature(self) -> float: ...

    @property
    def language(self) -> str: ...

    @property
    def llm_temperature(self) -> float: ...

    @property
    def indexing_provider(self) -> str: ...

    @property
    def batch_size(self) -> int: ...

    @property
    def concat_max_words(self) -> int: ...

    @property
    def raw_dir(self) -> Path: ...

    @property
    def enriched_dir(self) -> Path: ...

    @property
    def priority_texts_dir(self) -> Path | None: ...

    @property
    def playlist_path(self) -> Path: ...

    @property
    def playlist_priority_path(self) -> Path | None: ...

    @property
    def discovery_queue_maxsize(self) -> int: ...

    @property
    def channel_discovery_workers(self) -> int: ...

    @property
    def days_lookback(self) -> int: ...

    @property
    def inventory_max_attempts(self) -> int: ...

    @property
    def judge_blocking(self) -> bool: ...

    @property
    def judge_max_attempts(self) -> int: ...


@dataclass
class DefaultPipelineSettings:
    """Default in-memory settings for standalone application use cases without .env dependency."""

    raw_index_max_chars: int = 2000
    raw_index_temperature: float = 0.2
    language: str = "Português do Brasil"
    llm_temperature: float = 0.7
    indexing_provider: str = "gemini"
    batch_size: int = 5
    concat_max_words: int = 50000
    raw_dir: Path = Path("data/raw")
    enriched_dir: Path = Path("data/enriched")
    priority_texts_dir: Path | None = None
    playlist_path: Path = Path("data/playlist.txt")
    playlist_priority_path: Path | None = None
    discovery_queue_maxsize: int = 50
    channel_discovery_workers: int = 4
    days_lookback: int = 30
    inventory_max_attempts: int = 3
    judge_blocking: bool = False
    judge_max_attempts: int = 1
