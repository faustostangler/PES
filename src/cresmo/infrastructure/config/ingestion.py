"""Ingestion, crawler, transcription, and pipeline throughput settings for Cresmo.

Conforms to:
    - ADR-069: Modular Domain Settings Package
"""

from __future__ import annotations

from typing import Self

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestionSettings(BaseSettings):
    """Media ingestion, worker concurrency, and pipeline execution settings."""

    model_config = SettingsConfigDict(extra="ignore")

    browser_cookies: str | None = Field(
        default="firefox",
        description="Default browser to extract cookies from if cookies_file is absent ('firefox', 'chrome', etc.).",
    )
    auto_extract_cookies: bool = Field(
        default=True,
        description="Whether to automatically extract cookies from browser if cookies_file is absent or expired.",
    )
    enable_channel_crawler: bool = Field(
        default=False,
        description="Whether batch discovery automatically crawls 365d uploads across all channels by default.",
    )
    require_auth_cookies: bool = Field(
        default=False,
        description="Whether to fail-fast if no valid authenticated YouTube session cookies are found.",
    )
    whisper_model: str = Field(
        default="base",
        description="Whisper STT model variant for audio transcription.",
    )
    days_lookback: int = Field(
        default=365,
        description="Default crawling lookback window in days (default: 365 / 1 year).",
    )
    whisper_workers: int = Field(
        default=1,
        validation_alias=AliasChoices("whisper_workers", "max_whisper_workers"),
        description="Concurrent worker threads for local Whisper audio-to-text fallback (default: 1).",
    )
    subtitle_workers: int = Field(
        default=0,
        validation_alias=AliasChoices("subtitle_workers", "max_subtitle_workers"),
        description="Concurrent worker threads for native JSON/SRV subtitle downloading (defaults to whisper_workers * 5).",
    )
    channel_discovery_workers: int = Field(
        default=0,
        validation_alias=AliasChoices("channel_discovery_workers", "max_channel_workers"),
        description="Concurrent worker threads for scanning YouTube channel uploads feeds (defaults to whisper_workers * 10).",
    )
    discovery_queue_maxsize: int = Field(
        default=50,
        ge=1,
        validation_alias=AliasChoices("discovery_queue_maxsize", "max_discovery_queue_size"),
        description="Maximum bounded capacity for batch source streaming queue to enforce backpressure against OOM (default: 50).",
    )

    @model_validator(mode="after")
    def _compute_worker_multiples(self) -> Self:
        """Calculate dynamic worker pool sizes from whisper_workers base.

        Maintains healthy worker ratios (5x for network-bound subtitle downloads,
        10x for channel uploads feed polling) derived from the CPU-bound whisper_workers base,
        preventing thread starvation and CPU saturation.

        Returns:
            Self instance with calculated worker counts.
        """
        if self.subtitle_workers <= 0:
            self.subtitle_workers = max(1, self.whisper_workers * 5)
        if self.channel_discovery_workers <= 0:
            self.channel_discovery_workers = max(1, self.whisper_workers * 10)
        return self

    batch_size: int = Field(
        default=5,
        validation_alias=AliasChoices("batch_size", "CRESMO_BATCH_SIZE"),
        description="Batch size for Atomic Note synthesis.",
    )
    keep_audio: bool = Field(
        default=False,
        description="Whether to preserve downloaded raw audio files.",
    )
    expansion_max_passes: int = Field(
        default=5,
        ge=1,
        le=10,
        validation_alias=AliasChoices(
            "expansion_max_passes",
            "CRESMO_EXPANSION_MAX_PASSES",
            "EXPANSION_MAX_PASSES",
            "gap_filler_passes",
            "CRESMO_GAP_FILLER_PASSES",
            "GAP_FILLER_PASSES",
        ),
        description="Default multi-pass text expansion and refinement limit before mechanical saturation.",
    )

    @property
    def gap_filler_passes(self) -> int:
        """Backward-compatible property alias for expansion_max_passes."""
        return self.expansion_max_passes

    concat_max_words: int = Field(
        default=500_000,
        validation_alias=AliasChoices("concat_max_words", "CONCAT_MAX_WORDS", "MASTER_MAX_WORDS"),
        description="Maximum word limit per aggregated master document before sequential rollover without mid-file splits.",
    )
    raw_index_max_chars: int = Field(
        default=0,
        description="Maximum characters of transcript body passed to LLM for conceptual synthesis, zero means full text.",
    )
    raw_index_max_attempts: int = Field(
        default=2,
        ge=0,
        validation_alias=AliasChoices(
            "raw_index_max_attempts", "CRESMO_RAW_INDEX_MAX_ATTEMPTS", "RAW_INDEX_MAX_ATTEMPTS"
        ),
        description="Maximum LLM judge rewrite attempts for raw indexing (0 means unconstrained / infinite loop).",
    )
    inventory_max_attempts: int = Field(
        default=2,
        ge=0,
        validation_alias=AliasChoices(
            "inventory_max_attempts", "CRESMO_INVENTORY_MAX_ATTEMPTS", "INVENTORY_MAX_ATTEMPTS"
        ),
        description="Maximum LLM judge rewrite attempts for atomic inventory discovery (0 means unconstrained / infinite loop).",
    )


__all__ = ["IngestionSettings"]
