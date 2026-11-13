"""Unit tests for SqliteLedgerAdapter.

Verifies SQLite WAL mode, schema initialization, CRUD operations,
idempotency checking, and concurrency robustness per SPEC-003.
"""

from __future__ import annotations

import concurrent.futures
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from cresmo.domain.value_objects import ChannelName, ContentId, LedgerEntry, PipelineStatus
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
            channel_name=ChannelName("PhysicsDept"),
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
        assert retrieved.media_url == "https://youtube.com/watch?v=abcdefgh1234"
        assert retrieved.title == "Advanced Quantum Mechanics"
        assert retrieved.channel_name == ChannelName("PhysicsDept")
        assert retrieved.notes_count == 12
        assert retrieved.status == PipelineStatus.COMPLETED
        assert retrieved.error_message is None
        assert retrieved.started_at == now
        assert retrieved.completed_at == now

    def test_save_and_get_entry_with_error_message(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        now = datetime.now(UTC)
        entry = LedgerEntry(
            content_id=ContentId("errVideo123"),
            media_url="https://youtube.com/watch?v=errVideo123",
            title="Failed Video",
            channel_name=ChannelName("ErrorChannel"),
            status=PipelineStatus.FAILED_INGESTION,
            notes_count=0,
            error_message="Download timeout 408",
            started_at=now,
            completed_at=now,
        )
        adapter.save_entry(entry)
        retrieved = adapter.get_entry(ContentId("errVideo123"))
        assert retrieved is not None
        assert retrieved.error_message == "Download timeout 408"
        assert retrieved.status == PipelineStatus.FAILED_INGESTION
        assert retrieved.notes_count == 0
        assert retrieved.started_at == now
        assert retrieved.completed_at == now

    def test_save_entry_updates_existing_entry(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        start_time = datetime.now(UTC)
        initial = LedgerEntry(
            content_id=ContentId("runningVideo1"),
            media_url="https://youtube.com/watch?v=runningVideo1",
            title="Video in Progress",
            channel_name=ChannelName("TestChannel"),
            status=PipelineStatus.RUNNING,
            started_at=start_time,
        )
        adapter.save_entry(initial)
        assert not adapter.is_processed(ContentId("runningVideo1"))

        completed = LedgerEntry(
            content_id=ContentId("runningVideo1"),
            media_url="https://youtube.com/watch?v=runningVideo1",
            title="Video in Progress",
            channel_name=ChannelName("TestChannel"),
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
                    channel_name=ChannelName("Channel"),
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
                        channel_name=ChannelName("WorkerChannel"),
                        status=PipelineStatus.COMPLETED,
                    )
                )
                assert adapter.is_processed(ContentId(cid))

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="TestSqliteLedgerWorker"
        ) as executor:
            futures = [executor.submit(worker, i) for i in range(4)]
            for future in concurrent.futures.as_completed(futures):
                future.result()

        all_entries = adapter.list_entries(limit=100)
        assert len(all_entries) == 40

    def test_in_memory_database_initialization(self) -> None:
        adapter = SqliteLedgerAdapter(":memory:", timeout=10.0)
        assert adapter._db_path == ":memory:"
        assert adapter._timeout == 10.0
        with adapter._get_connection() as conn:
            cursor = conn.execute("PRAGMA synchronous;")
            sync_mode = cursor.fetchone()[0]
            assert sync_mode in (1, "1", "NORMAL", "normal")

    def test_is_processed_false_for_all_non_completed_statuses(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        for idx, status in enumerate(
            [
                PipelineStatus.SKIPPED_IDEMPOTENT,
                PipelineStatus.RUNNING,
                PipelineStatus.FAILED_INGESTION,
                PipelineStatus.FAILED_TRANSFORMATION,
                PipelineStatus.PAUSED_BUDGET,
            ]
        ):
            cid = ContentId(f"statusTest00{idx}")
            adapter.save_entry(
                LedgerEntry(
                    content_id=cid,
                    media_url=f"https://youtube.com/watch?v={cid.value}",
                    title="Status Test",
                    channel_name=ChannelName("TestChannel"),
                    status=status,
                )
            )
            assert not adapter.is_processed(cid)

    def test_mark_processed_defaults_and_on_conflict_update(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        cid = ContentId("defaultsTest01")

        # Initial mark_processed creates with defaults
        adapter.mark_processed(cid)
        entry = adapter.get_entry(cid)
        assert entry is not None
        assert entry.channel_name == ChannelName("DefaultChannel")
        assert entry.title == f"Video {cid.value}"
        assert entry.media_url == f"https://youtube.com/watch?v={cid.value}"
        assert entry.notes_count == 0
        assert entry.status == PipelineStatus.COMPLETED
        assert entry.completed_at is not None

        # Re-marking updates completed_at
        initial_completed = entry.completed_at
        adapter.mark_processed(cid)
        updated = adapter.get_entry(cid)
        assert updated is not None
        assert updated.status == PipelineStatus.COMPLETED
        assert updated.completed_at is not None
        assert updated.completed_at >= initial_completed

    def test_save_entry_started_at_preservation_and_error_message(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        cid = ContentId("errorTest001")
        start_time = datetime.now(UTC)

        # Initial running entry with start_time
        entry = LedgerEntry(
            content_id=cid,
            media_url=f"https://youtube.com/watch?v={cid.value}",
            title="Initial Title",
            channel_name=ChannelName("Channel1"),
            status=PipelineStatus.RUNNING,
            started_at=start_time,
        )
        adapter.save_entry(entry)

        # Failure update without started_at should preserve initial started_at via COALESCE
        fail_entry = LedgerEntry(
            content_id=cid,
            media_url=f"https://youtube.com/watch?v={cid.value}",
            title="Updated Title",
            channel_name=ChannelName("Channel2"),
            status=PipelineStatus.FAILED_INGESTION,
            error_message="Fatal processing failure",
            started_at=None,
        )
        adapter.save_entry(fail_entry)

        retrieved = adapter.get_entry(cid)
        assert retrieved is not None
        assert retrieved.title == "Updated Title"
        assert retrieved.channel_name == ChannelName("Channel2")
        assert retrieved.status == PipelineStatus.FAILED_INGESTION
        assert retrieved.error_message == "Fatal processing failure"
        assert retrieved.started_at == start_time
        assert retrieved.completed_at is None

    def test_list_entries_default_limit(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        for i in range(10):
            cid = ContentId(f"defaultLimit{i:02d}")
            adapter.save_entry(
                LedgerEntry(
                    content_id=cid,
                    media_url=f"https://youtube.com/watch?v={cid.value}",
                    title=f"Video #{i}",
                    channel_name=ChannelName("Channel"),
                    status=PipelineStatus.COMPLETED,
                )
            )
        # Calling without limit uses default 100
        entries = adapter.list_entries()
        assert len(entries) == 10

    def test_init_schema_creates_tables_and_indexes(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "schema_test.db")
        with adapter._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='cresmo_ledger';"
            )
            assert cursor.fetchone() is not None

            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index';")
            index_names = {row[0] for row in cursor.fetchall()}
            assert "idx_cresmo_ledger_status" in index_names

    def test_is_processed_only_returns_true_for_completed_status(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "status_test.db")
        cid_running = ContentId("vid_running")
        cid_failed = ContentId("vid_failed")
        cid_completed = ContentId("vid_completed")

        adapter.save_entry(
            LedgerEntry(
                content_id=cid_running,
                media_url="https://youtube.com/watch?v=vid_running",
                title="Running Video",
                channel_name=ChannelName("Channel"),
                status=PipelineStatus.RUNNING,
            )
        )
        adapter.save_entry(
            LedgerEntry(
                content_id=cid_failed,
                media_url="https://youtube.com/watch?v=vid_failed",
                title="Failed Video",
                channel_name=ChannelName("Channel"),
                status=PipelineStatus.FAILED_INGESTION,
            )
        )
        adapter.save_entry(
            LedgerEntry(
                content_id=cid_completed,
                media_url="https://youtube.com/watch?v=vid_completed",
                title="Completed Video",
                channel_name=ChannelName("Channel"),
                status=PipelineStatus.COMPLETED,
            )
        )

        assert adapter.is_processed(cid_running) is False
        assert adapter.is_processed(cid_failed) is False
        assert adapter.is_processed(cid_completed) is True

    def test_init_defaults_and_timeout(self) -> None:
        adapter = SqliteLedgerAdapter(":memory:")
        assert adapter._timeout == 5.0
        assert adapter._db_path == ":memory:"

    def test_row_to_entry_direct_and_null_fields(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        entry_none = LedgerEntry(
            content_id=ContentId("null_fields_vid"),
            media_url="https://youtube.com/watch?v=null_fields_vid",
            title="Null Fields Video",
            channel_name=ChannelName("NullChannel"),
            status=PipelineStatus.RUNNING,
            notes_count=0,
            error_message=None,
            started_at=None,
            completed_at=None,
        )
        adapter.save_entry(entry_none)
        retrieved = adapter.get_entry(ContentId("null_fields_vid"))
        assert retrieved is not None
        assert retrieved.started_at is None
        assert retrieved.completed_at is None
        assert retrieved.error_message is None
        assert retrieved.notes_count == 0
        assert retrieved.status == PipelineStatus.RUNNING
        assert retrieved.title == "Null Fields Video"
        assert retrieved.media_url == "https://youtube.com/watch?v=null_fields_vid"
        assert retrieved.channel_name == ChannelName("NullChannel")

    def test_is_processed_skipped_idempotent_and_non_existent(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        cid_skip = ContentId("vid_skipped_test")
        adapter.save_entry(
            LedgerEntry(
                content_id=cid_skip,
                media_url="https://youtube.com/watch?v=vid_skipped_test",
                title="Skipped",
                channel_name=ChannelName("Chan"),
                status=PipelineStatus.SKIPPED_IDEMPOTENT,
            )
        )
        assert adapter.is_processed(cid_skip) is False
        assert adapter.get_entry(ContentId("non_existent_id")) is None

    def test_list_entries_limit_parameter_and_default(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        for i in range(15):
            adapter.mark_processed(ContentId(f"lim_vid_{i:02d}"))

        assert len(adapter.list_entries(limit=5)) == 5
        assert len(adapter.list_entries(limit=10)) == 10
        assert len(adapter.list_entries(limit=15)) == 15
        assert len(adapter.list_entries()) == 15

    def test_init_creates_nested_parent_directories(self, tmp_path: Path) -> None:
        deep_dir = tmp_path / "deep" / "nested" / "path"
        db_file = deep_dir / "ledger.db"
        adapter = SqliteLedgerAdapter(db_file)
        assert deep_dir.exists()
        assert adapter.is_processed(ContentId("any_id")) is False

    def test_init_memory_does_not_call_mkdir(self) -> None:
        with patch.object(Path, "mkdir") as mock_mkdir:
            adapter = SqliteLedgerAdapter(":memory:")
            mock_mkdir.assert_not_called()
            assert adapter._db_path == ":memory:"

    def test_mark_processed_timestamp_timezone_is_utc(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        cid = ContentId("utc_tz_test_vid")
        adapter.mark_processed(cid)
        entry = adapter.get_entry(cid)
        assert entry is not None
        assert entry.completed_at is not None
        assert entry.completed_at.tzinfo == UTC

    def test_list_entries_default_limit_is_one_hundred(self, tmp_path: Path) -> None:
        adapter = SqliteLedgerAdapter(tmp_path / "test.db")
        for i in range(105):
            adapter.mark_processed(ContentId(f"bulk_limit_{i:03d}"))
        entries = adapter.list_entries()
        assert len(entries) == 100

    def test_row_to_entry_case_sensitive_mapping_all_columns(self) -> None:
        start_dt = datetime.now(UTC)
        comp_dt = datetime.now(UTC)
        strict_row = {
            "content_id": "strict_vid",
            "media_url": "https://youtube.com/watch?v=strict_vid",
            "title": "Strict Title",
            "channel_name": "Strict Channel",
            "status": "COMPLETED",
            "notes_count": 42,
            "error_message": "Some transient error",
            "started_at": start_dt.isoformat(),
            "completed_at": comp_dt.isoformat(),
        }
        entry = SqliteLedgerAdapter._row_to_entry(strict_row)  # type: ignore[arg-type]
        assert entry.content_id.value == "strict_vid"
        assert entry.media_url == "https://youtube.com/watch?v=strict_vid"
        assert entry.title == "Strict Title"
        assert entry.channel_name.value == "Strict Channel"
        assert entry.status == PipelineStatus.COMPLETED
        assert entry.notes_count == 42
        assert entry.error_message == "Some transient error"
        assert entry.started_at == start_dt
        assert entry.completed_at == comp_dt

    def test_row_to_entry_without_timestamps_or_error(self) -> None:
        strict_row = {
            "content_id": "strict_vid_none",
            "media_url": "https://youtube.com/watch?v=strict_vid_none",
            "title": "Strict Title None",
            "channel_name": "Strict Channel None",
            "status": "RUNNING",
            "notes_count": 0,
            "error_message": None,
            "started_at": None,
            "completed_at": None,
        }
        entry = SqliteLedgerAdapter._row_to_entry(strict_row)  # type: ignore[arg-type]
        assert entry.content_id.value == "strict_vid_none"
        assert entry.started_at is None
        assert entry.completed_at is None
        assert entry.error_message is None
