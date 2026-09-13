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
        env_file=(
            ".env",
            str(_WORKSPACE_DIR / ".env"),
            str(_WORKSPACE_DIR / "vault" / ".env"),
            str(_WORKSPACE_DIR / "data" / ".env"),
        ),
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
    data_dir: Path = Field(
        default_factory=lambda: _WORKSPACE_DIR / "data",
        description="Root directory for raw media lake, enriched compendiums, and ledger.",
    )
    vault_dir: Path = Field(
        default_factory=lambda: _WORKSPACE_DIR / "vault",
        description="Root directory for Obsidian Second Brain knowledge graph vault.",
    )

    @property
    def raw_dir(self) -> Path:
        """Directory for ingested raw media transcripts."""
        return self.data_dir / "raw"

    @property
    def enriched_dir(self) -> Path:
        """Directory for enriched multi-pass compendiums."""
        return self.data_dir / "enriched"

    @property
    def index_path(self) -> Path:
        """Master lookup JSON index."""
        return self.vault_dir / "_index.json"

    sqlite_ledger_filename: str = Field(
        default="cresmo_ledger.db",
        description="Filename of the SQLite WAL database for processed content tracking.",
    )

    @property
    def sqlite_ledger_path(self) -> Path:
        """Absolute path to processed content SQLite WAL database file."""
        return self.data_dir / self.sqlite_ledger_filename

    playlist_filename: str = Field(
        default="playlist.txt",
        description="Filename of the main video manifest inside data_dir.",
    )
    playlist_priority_filename: str = Field(
        default="playlist-priority.txt",
        description="Filename of the priority video manifest inside data_dir.",
    )

    priority_texts_dirname: str = Field(
        default="priority",
        description="Directory name inside data_dir containing priority text files (.txt, .md).",
    )

    @property
    def playlist_path(self) -> Path:
        """Absolute path to the main video manifest."""
        return self.data_dir / self.playlist_filename

    @property
    def playlist_priority_path(self) -> Path:
        """Absolute path to the priority video manifest."""
        return self.data_dir / self.playlist_priority_filename

    @property
    def priority_texts_dir(self) -> Path:
        """Absolute path to the priority texts directory."""
        return self.data_dir / self.priority_texts_dirname

    browser_headers_path: Path | None = Field(
        default=None,
        description="Optional custom path to browser request headers pool JSON file.",
    )

    # =========================================================================
    # 🟢 Category 3: Operational Tunables
    # =========================================================================
    gemini_model: str = Field(
        default="gemini-3.5-flash-lite",
        description="Default Gemini model variant for pipeline stages.",
    )
    gemini_fallback_model: str = Field(
        default="gemini-3.1-flash-lite",
        description="Fallback Gemini model variant if primary hits quota or demand spikes.",
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
