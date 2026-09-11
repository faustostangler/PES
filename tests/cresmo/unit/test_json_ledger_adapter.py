"""Unit tests for JsonLedgerAdapter.

Verifies atomic filesystem persistence, lazy initialization, idempotency,
and corrupted JSON recovery per SPEC-002 §4.3.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.value_objects import ContentId
from cresmo.infrastructure.adapters.json_ledger_adapter import JsonLedgerAdapter


class TestJsonLedgerAdapter:
    """Hermetic unit tests for atomic file-based ledger adapter."""

    def test_ledger_initializes_empty_when_file_not_found(self, tmp_path: Path) -> None:
        ledger_file = tmp_path / "processed_cresmo.json"
        adapter = JsonLedgerAdapter(ledger_path=ledger_file)

        cid = ContentId("dQw4w9WgXcQ")
        assert adapter.is_processed(cid) is False
        assert not ledger_file.exists()

    def test_mark_processed_persists_atomically(self, tmp_path: Path) -> None:
        ledger_file = tmp_path / "processed_cresmo.json"
        adapter = JsonLedgerAdapter(ledger_path=ledger_file)

        cid = ContentId("dQw4w9WgXcQ")
        adapter.mark_processed(cid)

        assert adapter.is_processed(cid) is True
        assert ledger_file.exists()

        # Verify underlying JSON structure is a clean array
        with open(ledger_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data == ["dQw4w9WgXcQ"]

    def test_mark_processed_idempotent_deduplication(self, tmp_path: Path) -> None:
        ledger_file = tmp_path / "processed_cresmo.json"
        adapter = JsonLedgerAdapter(ledger_path=ledger_file)

        cid = ContentId("dQw4w9WgXcQ")
        adapter.mark_processed(cid)
        adapter.mark_processed(cid)  # Duplicate insertion

        with open(ledger_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data == ["dQw4w9WgXcQ"]

    def test_mark_processed_multiple_distinct_ids(self, tmp_path: Path) -> None:
        ledger_file = tmp_path / "processed_cresmo.json"
        adapter = JsonLedgerAdapter(ledger_path=ledger_file)

        cid1 = ContentId("video_id_001")
        cid2 = ContentId("video_id_002")

        adapter.mark_processed(cid1)
        adapter.mark_processed(cid2)

        assert adapter.is_processed(cid1) is True
        assert adapter.is_processed(cid2) is True
        assert adapter.is_processed(ContentId("video_id_003")) is False

        with open(ledger_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert sorted(data) == ["video_id_001", "video_id_002"]

    def test_corrupted_json_raises_domain_error(self, tmp_path: Path) -> None:
        ledger_file = tmp_path / "processed_cresmo.json"
        ledger_file.write_text("INVALID_NON_JSON_CORRUPTED", encoding="utf-8")

        adapter = JsonLedgerAdapter(ledger_path=ledger_file)

        with pytest.raises(CresmoDomainError, match="Corrupted ledger file"):
            adapter.is_processed(ContentId("dQw4w9WgXcQ"))
