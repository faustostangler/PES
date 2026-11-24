"""Ingestion, cookies, Whisper STT, and worker pool settings for Cresmo.

Conforms to:
    - ADR-004: Native Media Ingestion
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CookieSettings(BaseModel):
    """Immutable YouTube browser/cookie authentication settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    browser: str | None = Field(
        default="firefox",
        description="Default browser to extract cookies from if cookies file is absent.",
    )
    auto_extract: bool = Field(
        default=True,
        description="Whether to automatically extract cookies from browser if cookies file is absent or expired.",
    )
    require_auth: bool = Field(
        default=False,
        description="Whether to fail-fast if no valid authenticated YouTube session cookies are found.",
    )
    file: Path | None = Field(
        default=None,
        description="Optional explicit path to Netscape cookies file for YouTube authentication.",
    )


class WorkerPoolSettings(BaseModel):
    """Immutable ingestion worker pool sizing and queue backpressure settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    whisper: int = Field(
        default=1,
        ge=1,
        description="Concurrent worker threads for local Whisper audio-to-text fallback.",
    )
    subtitle: int = Field(
        default=0,
        ge=0,
        description="Concurrent worker threads for native subtitle downloading (0 -> whisper * 5).",
    )
    channel_discovery: int = Field(
        default=0,
        ge=0,
        description="Concurrent worker threads for scanning YouTube channel feeds (0 -> whisper * 10).",
    )
    discovery_queue_maxsize: int = Field(
        default=50,
        ge=1,
        description="Maximum bounded capacity for batch source streaming queue.",
    )

    @model_validator(mode="after")
    def _compute_worker_multiples(self) -> Self:
        """Compute deterministic worker pool ratios from whisper base on frozen construction."""
        if self.subtitle <= 0:
            object.__setattr__(self, "subtitle", max(1, self.whisper * 5))
        if self.channel_discovery <= 0:
            object.__setattr__(self, "channel_discovery", max(1, self.whisper * 10))
        return self


class IngestionSettings(BaseModel):
    """Composed media ingestion, cookie, Whisper, and worker pool settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cookies: CookieSettings = Field(default_factory=CookieSettings)
    workers: WorkerPoolSettings = Field(default_factory=WorkerPoolSettings)
    whisper_model: str = Field(
        default="base",
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
        default=365,
        ge=0,
        description="Default crawling lookback window in days.",
    )
    enable_channel_crawler: bool = Field(
        default=False,
        description="Whether batch discovery automatically crawls uploads across channels by default.",
    )
    keep_audio: bool = Field(
        default=False,
        description="Whether to preserve downloaded raw audio files.",
    )


__all__ = [
    "CookieSettings",
    "IngestionSettings",
    "WorkerPoolSettings",
]
