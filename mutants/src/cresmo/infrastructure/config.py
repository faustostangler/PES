"""Centralized Configuration for Cresmo Hexagonal Modular Monolith.

Enforces the 4-Category Configuration Taxonomy using Pydantic Settings V2:
- Category 1: Secrets & Credentials (Strictly from .env or environment)
- Category 2: Infra & Storage Paths (Obsidian vault, raw, enriched, index)
- Category 3: Operational Tunables (Model names, temperatures, batch sizes)
- Category 4: Domain Invariants (Defined in domain modules)
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from pydantic import AliasChoices, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_workspace_root(start_path: Path | None = None) -> Path:
    """Locate the workspace root directory using Anchor Marker resolution."""
    current = (start_path or Path(__file__)).resolve()
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists() or (directory / ".git").exists():
            return directory
    return (start_path or Path(__file__)).resolve().parents[3]


_WORKSPACE_DIR = find_workspace_root()


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁCresmoSettingsǁensure_directories__mutmut: MutantDict = {}  # type: ignore


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

    @_mutmut_mutated(mutants_xǁCresmoSettingsǁensure_directories__mutmut)
    def ensure_directories(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_orig(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_1(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=None, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_2(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=None)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_3(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_4(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, )
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_5(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=False, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_6(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=False)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_7(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=None, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_8(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=None)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_9(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_10(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, )
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_11(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=False, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_12(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=False)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_13(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=None, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_14(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=None)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_15(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_16(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, )
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_17(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=False, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_18(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=False)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_19(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=None, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_20(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=None)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_21(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_22(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, )
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_23(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=False, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_24(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=False)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_25(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=None, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_26(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=None)

    def xǁCresmoSettingsǁensure_directories__mutmut_27(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_28(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, )

    def xǁCresmoSettingsǁensure_directories__mutmut_29(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=False, exist_ok=True)

    def xǁCresmoSettingsǁensure_directories__mutmut_30(self) -> None:
        """Ensure all runtime directories exist on the filesystem (fail-safe idempotent)."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.priority_texts_dir.mkdir(parents=True, exist_ok=False)

    browser_headers_path: Path | None = Field(
        default=None,
        description="Optional custom path to browser request headers pool JSON file.",
    )
    prompts_path: Path | None = Field(
        default=None,
        description="Optional custom path to LLM prompt templates JSON file.",
    )
    skills_dir: Path | None = Field(
        default=None,
        description="Optional custom path to .agents/skills directory for prompt enrichment.",
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

    @model_validator(mode="after")
    def _compute_worker_multiples(self) -> Self:
        """Compute worker pools as multiples of whisper_workers unless explicitly configured."""
        if self.subtitle_workers <= 0:
            self.subtitle_workers = max(1, self.whisper_workers * 5)
        if self.channel_discovery_workers <= 0:
            self.channel_discovery_workers = max(1, self.whisper_workers * 10)
        return self

    batch_size: int = Field(
        default=5,
        validation_alias=AliasChoices("batch_size", "stage_5_batch_size", "atomic_batch_size"),
        description="Batch size for Atomic Note synthesis.",
    )
    keep_audio: bool = Field(
        default=False,
        description="Whether to preserve downloaded raw audio files.",
    )
    gap_filler_passes: int = Field(
        default=3,
        validation_alias=AliasChoices("gap_filler_passes", "stage_2_passes"),
        description="Default Socratic gap filler refinement passes.",
    )

mutants_xǁCresmoSettingsǁensure_directories__mutmut['_mutmut_orig'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_orig # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_1'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_1 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_2'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_2 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_3'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_3 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_4'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_4 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_5'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_5 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_6'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_6 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_7'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_7 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_8'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_8 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_9'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_9 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_10'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_10 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_11'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_11 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_12'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_12 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_13'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_13 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_14'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_14 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_15'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_15 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_16'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_16 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_17'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_17 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_18'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_18 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_19'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_19 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_20'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_20 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_21'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_21 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_22'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_22 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_23'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_23 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_24'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_24 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_25'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_25 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_26'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_26 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_27'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_27 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_28'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_28 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_29'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_29 # type: ignore # mutmut generated
mutants_xǁCresmoSettingsǁensure_directories__mutmut['xǁCresmoSettingsǁensure_directories__mutmut_30'] = CresmoSettings.xǁCresmoSettingsǁensure_directories__mutmut_30 # type: ignore # mutmut generated
