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
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from cresmo.domain.stage_registry import StageName
from cresmo.infrastructure.paths import find_workspace_root

_WORKSPACE_DIR = find_workspace_root()
_DATA_DIR_NAME: Final[str] = "data"
_VAULT_DIR_NAME: Final[str] = "vault"
_MASTER_DIR_NAME: Final[str] = "master"
_VAULT_INDEX_FILENAME: Final[str] = "_index.json"
_MOCS_DIR_NAME: Final[str] = "MOCs"
DEFAULT_SQLITE_LEDGER_FILENAME: Final[str] = "cresmo_ledger.db"
DEFAULT_PLAYLIST_FILENAME: Final[str] = "playlist.txt"
DEFAULT_PLAYLIST_PRIORITY_FILENAME: Final[str] = "playlist-priority.txt"
DEFAULT_PRIORITY_TEXTS_DIRNAME: Final[str] = "priority"

__all__ = ["StorageSettings"]


class StorageSettings(BaseModel):
    """Immutable infrastructure and filesystem storage settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    data_dir: Path = Field(
        default_factory=lambda: _WORKSPACE_DIR / _DATA_DIR_NAME,
        description="Root directory for staged media transcripts and processing ledger.",
    )
    vault_dir: Path = Field(
        default_factory=lambda: _WORKSPACE_DIR / _VAULT_DIR_NAME,
        description="Root directory for Obsidian Second Brain knowledge graph vault.",
    )

    def stage_dir(self, stage: StageName) -> Path:
        """Resolve directory for a canonical pipeline stage under ``data_dir``."""
        return self.data_dir / stage.value

    @property
    def raw_dir(self) -> Path:
        """Directory for ingested raw media transcripts."""
        return self.stage_dir(StageName.RAW)

    @property
    def master_dir(self) -> Path:
        """Directory for consolidated master compendiums per channel category for RAG."""
        return self.data_dir / _MASTER_DIR_NAME

    @property
    def index_path(self) -> Path:
        """Master lookup JSON index."""
        return self.vault_dir / _VAULT_INDEX_FILENAME

    @property
    def mocs_dir(self) -> Path:
        """Subdirectory within vault/ housing Maps of Content."""
        return self.vault_dir / _MOCS_DIR_NAME

    sqlite_ledger_filename: str = Field(
        default=DEFAULT_SQLITE_LEDGER_FILENAME,
        description="Filename of the SQLite WAL database for processed content tracking.",
    )

    @property
    def sqlite_ledger_path(self) -> Path:
        """Absolute path to processed content SQLite WAL database file."""
        return self.data_dir / self.sqlite_ledger_filename

    playlist_filename: str = Field(
        default=DEFAULT_PLAYLIST_FILENAME,
        description="Filename of the main video manifest inside data_dir.",
    )
    playlist_priority_filename: str = Field(
        default=DEFAULT_PLAYLIST_PRIORITY_FILENAME,
        description="Filename of the priority video manifest inside data_dir.",
    )

    priority_texts_dirname: str = Field(
        default=DEFAULT_PRIORITY_TEXTS_DIRNAME,
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
