"""Unit tests for PolarsBatchProcessor ensuring zero-copy columnar operations."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from cresmo.application.use_cases.discovery.models import BatchSource
from cresmo.domain.value_objects import ContentId, SourceModality
from cresmo.infrastructure.adapters.data import PolarsBatchProcessor
from tests.factories import BatchSourceFactory


def test_sources_to_dataframe() -> None:
    """Verify that a list of BatchSource items is converted to a Polars DataFrame."""
    sources = [
        BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=vid1", content_id=ContentId("vid1")),
        BatchSource(kind=SourceModality.FILE, target="/data/raw/vid2.txt", content_id=ContentId("vid2")),
    ]

    df = PolarsBatchProcessor.sources_to_dataframe(sources)
    assert isinstance(df, pl.DataFrame)
    assert df.height == 2
    assert "content_id" in df.columns
    assert "target" in df.columns
    assert "kind" in df.columns


def test_deduplicate_batch_sources_keeps_unique() -> None:
    """Verify that duplicates are deduplicated by content_id using Polars."""
    s1 = BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=dup1", content_id=ContentId("dup1"))
    s2 = BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=dup1", content_id=ContentId("dup1"))
    s3 = BatchSource(kind=SourceModality.URL, target="https://youtube.com/watch?v=unique2", content_id=ContentId("unique2"))

    deduped = PolarsBatchProcessor.deduplicate_batch_sources([s1, s2, s3])
    assert len(deduped) == 2
    ids = [s.content_id.value for s in deduped if s.content_id]
    assert "dup1" in ids
    assert "unique2" in ids


def test_export_and_scan_filter_pending(tmp_path: Path) -> None:
    """Verify export to Parquet and lazy scan/filtering with Polars."""
    parquet_file = tmp_path / "batches" / "test_batch.parquet"

    sources = [
        BatchSourceFactory.build(content_id=ContentId("item1")),
        BatchSourceFactory.build(content_id=ContentId("item2")),
    ]

    PolarsBatchProcessor.export_to_parquet(sources, parquet_file)
    assert parquet_file.exists()

    df = PolarsBatchProcessor.scan_and_filter_pending(parquet_file, status="PENDING")
    assert isinstance(df, pl.DataFrame)
    assert df.height == 2
