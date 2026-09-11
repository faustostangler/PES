"""Atomic File-Based JSON Ledger Adapter.

Implements LedgerRepositoryPort using atomic filesystem rename semantics to prevent
corruption during sudden process termination.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

from cresmo.application.ports import LedgerRepositoryPort
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import ContentId


class JsonLedgerAdapter(LedgerRepositoryPort):
    """File-based idempotency ledger backed by a JSON array of processed ContentIds."""

    def __init__(self, ledger_path: Path) -> None:
        """Initialize ledger adapter with target filesystem path.

        Args:
            ledger_path: Path to processed content JSON file.
        """
        self.ledger_path = Path(ledger_path)

    def _load_entries(self) -> set[str]:
        """Load processed content IDs from disk into a set.

        Returns:
            Set of processed content ID strings.

        Raises:
            CresmoDomainError: If the ledger file contains malformed non-JSON data.
        """
        if not self.ledger_path.exists():
            return set()

        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise CresmoDomainError(
                    f"Corrupted ledger file at: {self.ledger_path} (expected JSON array, got {type(data).__name__})"
                )
            return set(data)
        except json.JSONDecodeError as exc:
            raise CresmoDomainError(
                f"Corrupted ledger file at: {self.ledger_path} ({exc})"
            ) from exc

    def is_processed(self, content_id: ContentId) -> bool:
        """Check whether a content item has already been marked processed.

        Args:
            content_id: Target content identifier.

        Returns:
            True if the content ID is recorded in the ledger, False otherwise.
        """
        return content_id.value in self._load_entries()

    def mark_processed(self, content_id: ContentId) -> None:
        """Mark a content item as processed, persisting atomically to disk.

        Args:
            content_id: Target content identifier to append.
        """
        entries = self._load_entries()
        if content_id.value in entries:
            return

        entries.add(content_id.value)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        temp_file = self.ledger_path.with_name(f"{self.ledger_path.name}.tmp.{uuid4().hex}")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(sorted(entries), f, indent=2, ensure_ascii=False)
            os.replace(temp_file, self.ledger_path)
        except Exception:
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            raise
