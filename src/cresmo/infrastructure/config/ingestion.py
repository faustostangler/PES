"""Ingestion, cookies, Whisper STT, and worker pool settings for Cresmo.

Conforms to:
    - ADR-004: Native Media Ingestion
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

DEFAULT_WHISPER_WORKERS: Final[int] = 1
DEFAULT_CHANNEL_DISCOVERY_WORKERS: Final[int] = 0
CHANNEL_DISCOVERY_WORKER_MULTIPLIER: Final[int] = 10
DEFAULT_DISCOVERY_QUEUE_MAXSIZE: Final[int] = 50
DEFAULT_WHISPER_MODEL: Final[str] = "base"
DEFAULT_DAYS_LOOKBACK: Final[int] = 365


class WorkerPoolSettings(BaseModel):
    """Immutable ingestion worker pool sizing and queue backpressure settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    whisper: int = Field(
        default=DEFAULT_WHISPER_WORKERS,
        ge=1,
        description="Concurrent worker threads for local Whisper audio-to-text fallback.",
    )
    channel_discovery: int = Field(
        default=DEFAULT_CHANNEL_DISCOVERY_WORKERS,
        ge=0,
        description="Concurrent worker threads for scanning YouTube channel feeds (0 -> whisper * 10).",
    )
    discovery_queue_maxsize: int = Field(
        default=DEFAULT_DISCOVERY_QUEUE_MAXSIZE,
        ge=1,
        description="Maximum bounded capacity for batch source streaming queue.",
    )

    @model_validator(mode="after")
    def _compute_worker_multiples(self) -> Self:
        """Compute deterministic worker pool ratios from whisper base on frozen construction."""
        if self.channel_discovery <= 0:
            object.__setattr__(
                self,
                "channel_discovery",
                max(DEFAULT_WHISPER_WORKERS, self.whisper * CHANNEL_DISCOVERY_WORKER_MULTIPLIER),
            )
        return self


class IngestionSettings(BaseModel):
    """Composed media ingestion, cookie, Whisper, and worker pool settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cookies_file: Path | None = Field(
        default=None,
        description="Optional explicit path to Netscape cookies file for YouTube authentication.",
    )
    workers: WorkerPoolSettings = Field(default_factory=WorkerPoolSettings)
    whisper_model: str = Field(
        default=DEFAULT_WHISPER_MODEL,
        description="Whisper STT model variant for audio transcription.",
    )
    whisper_device: Literal["auto", "cpu", "cuda"] = Field(
        default="auto",
        description="Inference device for FasterWhisperEngine ('auto', 'cpu', or 'cuda').",
    )
    whisper_compute_type: Literal["auto", "int8", "int8_float16", "float16", "float32"] = Field(
        default="auto",
        description="CTranslate2 quantization/precision mode for FasterWhisperEngine.",
    )
    whisper_vad_filter: bool = Field(
        default=True,
        description="Whether to apply Silero VAD speech filtering during audio transcription.",
    )
    enable_rss_fast_path: bool = Field(
        default=True,
        description="Whether to use YouTube Atom RSS feeds as a sub-200ms fast-path before yt-dlp.",
    )
    days_lookback: int = Field(
        default=DEFAULT_DAYS_LOOKBACK,
        ge=0,
        description="Default crawling lookback window in days.",
    )
    enable_channel_crawler: bool = Field(
        default=False,
        description="Whether batch discovery automatically crawls uploads across channels by default.",
    )


__all__ = [
    "IngestionSettings",
    "WorkerPoolSettings",
]
