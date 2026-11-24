"""Infrastructure storage and filesystem path settings for Cresmo.

Pure declarative, immutable Pydantic V2 BaseModel without filesystem mutation
or probe side effects during instantiation.

Conforms to:
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-006: Resilient Workspace Root Discovery
    - ADR-074: Hierarchical Immutable Settings & Pure Domain Policies
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from cresmo.infrastructure.paths import find_workspace_root

_WORKSPACE_DIR = find_workspace_root()

__all__ = ["StorageSettings"]


class StorageSettings(BaseModel):
    """Immutable infrastructure and filesystem storage settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

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
    def fluid_dir(self) -> Path:
        """Directory for intermediate detranscribed fluid prose transcripts."""
        return self.data_dir / "fluid_prose"

    @property
    def gap_filler_dir(self) -> Path:
        """Directory for deep gap-filled prose transcripts."""
        return self.data_dir / "gap_filler"

    @property
    def enriched_dir(self) -> Path:
        """Directory for enriched multi-pass compendiums."""
        return self.data_dir / "enriched"

    @property
    def master_dir(self) -> Path:
        """Directory for consolidated master compendiums per channel category for RAG."""
        return self.data_dir / "master"

    @property
    def index_path(self) -> Path:
        """Master lookup JSON index."""
        return self.vault_dir / "_index.json"

    @property
    def mocs_dir(self) -> Path:
        """Subdirectory within vault/ housing Maps of Content."""
        return self.vault_dir / "MOCs"

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
    brain_csv_filename: str = Field(
        default="brain.csv",
        description="Filename of the global conceptual index CSV inside data_dir.",
    )

    @property
    def brain_csv_path(self) -> Path:
        """Absolute path to global brain.csv conceptual index file."""
        return self.data_dir / self.brain_csv_filename

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
    prompts_path: Path | None = Field(
        default=None,
        description="Optional custom path to LLM prompt templates JSON file.",
    )
    taxonomy_path: Path | None = Field(
        default=None,
        description="Optional custom path to channel taxonomy catalog JSON file.",
    )
    skills_dir: Path | None = Field(
        default=None,
        description="Optional custom path to .agents/skills directory for prompt enrichment.",
    )
