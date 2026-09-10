"""Centralized Configuration for Cresmo Hexagonal Modular Monolith.

Enforces the 4-Category Configuration Taxonomy using Pydantic Settings V2:
- Category 1: Secrets & Credentials (Strictly from .env or environment)
- Category 2: Infra & Storage Paths (Obsidian vault, raw, enriched, index)
- Category 3: Operational Tunables (Model names, temperatures, batch sizes)
- Category 4: Domain Invariants (Defined in domain modules)
"""

from __future__ import annotations

from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_WORKSPACE_DIR = Path(__file__).resolve().parents[3]


class CresmoSettings(BaseSettings):
    """Single Source of Truth (SSOT) configuration for Cresmo."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # =========================================================================
    # 🔴 Category 1: Secrets & Credentials
    # =========================================================================
    gemini_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="Google Gemini API Key for synthesis and expansion.",
    )
    langfuse_secret_key: SecretStr = Field(
        default=SecretStr(""),
        description="Langfuse secret key for evaluation and observability.",
    )
    langfuse_public_key: str = Field(
        default="",
        description="Langfuse public key for evaluation and observability.",
    )
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        description="Langfuse telemetry endpoint URL.",
    )

    # =========================================================================
    # 🟡 Category 2: Infra & Storage Paths
    # =========================================================================
    vault_dir: Path = Field(
        default_factory=lambda: _WORKSPACE_DIR / "playground" / "cresmo",
        description="Root directory for Cresmo pipeline artifacts and Obsidian vault.",
    )

    @property
    def raw_dir(self) -> Path:
        """Directory for ingested raw media transcripts."""
        return self.vault_dir / "raw"

    @property
    def enriched_dir(self) -> Path:
        """Directory for enriched multi-pass compendiums."""
        return self.vault_dir / "enriched"

    @property
    def wiki_dir(self) -> Path:
        """Obsidian vault directory holding atomic notes and MOCs."""
        return self.vault_dir / "wiki"

    @property
    def index_path(self) -> Path:
        """Master lookup JSON index."""
        return self.wiki_dir / "_index.json"

    # =========================================================================
    # 🟢 Category 3: Operational Tunables
    # =========================================================================
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Default Gemini model variant for pipeline stages.",
    )
    whisper_model: str = Field(
        default="base",
        description="Whisper STT model variant for audio transcription.",
    )
    days_lookback: int = Field(
        default=730,
        description="Default crawling lookback window in days.",
    )
    batch_size: int = Field(
        default=5,
        validation_alias=AliasChoices("batch_size", "stage_5_batch_size", "atomic_batch_size"),
        description="Batch size for Atomic Note synthesis.",
    )
    keep_audio: bool = Field(
        default=False,
        description="Whether to preserve downloaded raw audio files.",
    )
