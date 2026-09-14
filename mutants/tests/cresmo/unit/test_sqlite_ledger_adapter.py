"""Unit tests for SqliteLedgerAdapter.

Verifies SQLite WAL mode, schema initialization, CRUD operations,
idempotency checking, and concurrency robustness per SPEC-003.
"""

from __future__ import annotations

import concurrent.futures
from datetime import UTC, datetime
from pathlib import Path

from cresmo.domain.value_objects import ContentId, LedgerEntry, PipelineStatus
from cresmo.infrastructure.adapters.sqlite_ledger_adapter import SqliteLedgerAdapter


class TestSqliteLedgerAdapter:
    """Test suite for SqliteLedgerAdapter."""

    def test_database_and_wal_mode_initialization(self, tmp_path: Path) -> None:
        db_path = tmp_path / "subdir" / "test_ledger.db"
        adapter = SqliteLedgerAdapter(db_path)

        assert db_path.exists()

        with adapter._get_connection() as conn:
            cursor = conn.execute("PRAGMA journal_mode;")
            journal_mode = cursor.fetchone()[0]
            assert str(journal_mode).lower() == "wal"

            cursor = conn.execute("PRAGMA synchronous;")
            sync_mode = cursor.fetchone()[0]
            # synchronous NORMAL is represented as 1 in SQLite
            assert sync_mode in (1, "1", "NORMAL", "normal")

    def test_is_processed_empty_database_returns_false(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        assert not adapter.is_processed(ContentId("dQw4w9WgXcQ"))

    def test_mark_processed_persists_and_queries_true(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        content_id = ContentId("dQw4w9WgXcQ")

        adapter.mark_processed(content_id)
        assert adapter.is_processed(content_id)

        entry = adapter.get_entry(content_id)
        assert entry is not None
        assert entry.content_id == content_id
        assert entry.status == PipelineStatus.COMPLETED

    def test_save_entry_and_get_entry(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        now = datetime.now(UTC)
        entry = LedgerEntry(
            content_id=ContentId("abcdefgh1234"),
            media_url="https://youtube.com/watch?v=abcdefgh1234",
            title="Advanced Quantum Mechanics",
            channel_name="PhysicsDept",
            status=PipelineStatus.COMPLETED,
            notes_count=12,
            error_message=None,
            started_at=now,
            completed_at=now,
        )

        adapter.save_entry(entry)
        retrieved = adapter.get_entry(ContentId("abcdefgh1234"))

        assert retrieved is not None
        assert retrieved.content_id.value == "abcdefgh1234"
        assert retrieved.title == "Advanced Quantum Mechanics"
        assert retrieved.channel_name == "PhysicsDept"
        assert retrieved.notes_count == 12
        assert retrieved.status == PipelineStatus.COMPLETED
        assert retrieved.error_message is None

    def test_save_entry_updates_existing_entry(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        start_time = datetime.now(UTC)
        initial = LedgerEntry(
            content_id=ContentId("runningVideo1"),
            media_url="https://youtube.com/watch?v=runningVideo1",
            title="Video in Progress",
            channel_name="TestChannel",
            status=PipelineStatus.RUNNING,
            started_at=start_time,
        )
        adapter.save_entry(initial)
        assert not adapter.is_processed(ContentId("runningVideo1"))

        completed = LedgerEntry(
            content_id=ContentId("runningVideo1"),
            media_url="https://youtube.com/watch?v=runningVideo1",
            title="Video in Progress",
            channel_name="TestChannel",
            status=PipelineStatus.COMPLETED,
            notes_count=5,
            started_at=start_time,
            completed_at=datetime.now(UTC),
        )
        adapter.save_entry(completed)
        assert adapter.is_processed(ContentId("runningVideo1"))

        updated = adapter.get_entry(ContentId("runningVideo1"))
        assert updated is not None
        assert updated.status == PipelineStatus.COMPLETED
        assert updated.notes_count == 5

    def test_list_entries_orders_by_recency(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        for i in range(5):
            cid = f"testVideo000{i}"
            adapter.save_entry(
                LedgerEntry(
                    content_id=ContentId(cid),
                    media_url=f"https://youtube.com/watch?v={cid}",
                    title=f"Video #{i}",
                    channel_name="Channel",
                    status=PipelineStatus.COMPLETED,
                )
            )

        entries = adapter.list_entries(limit=3)
        assert len(entries) == 3
        # Most recent inserted should be first
        assert entries[0].content_id.value == "testVideo0004"
        assert entries[1].content_id.value == "testVideo0003"
        assert entries[2].content_id.value == "testVideo0002"

    def test_concurrent_writes_and_reads_thread_safety(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test_concurrent.db")

        def worker(worker_id: int) -> None:
            for j in range(10):
                cid = f"worker{worker_id:02d}item{j:02d}00"
                adapter.save_entry(
                    LedgerEntry(
                        content_id=ContentId(cid),
                        media_url=f"https://youtube.com/watch?v={cid}",
                        title=f"Concurrent Video {cid}",
                        channel_name="WorkerChannel",
                        status=PipelineStatus.COMPLETED,
                    )
                )
                assert adapter.is_processed(ContentId(cid))

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(worker, i) for i in range(4)]
            for future in concurrent.futures.as_completed(futures):
                future.result()

        all_entries = adapter.list_entries(limit=100)
        assert len(all_entries) == 40
