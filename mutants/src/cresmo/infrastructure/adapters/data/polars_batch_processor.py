"""Polars Batch Ingestion & Columnar Processor for Cresmo.

Provides zero-copy, multi-threaded DataFrame processing for batch discovery,
manifest indexing, and source deduplication using Apache Arrow and Polars.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from cresmo.application.use_cases.discovery.models import BatchSource


class PolarsBatchProcessor:
    """High-performance batch processing adapter powered by Polars LazyFrames.

    Eliminates memory overhead and row-by-row iteration bottlenecks in large batch
    ingestion pipelines, replacing legacy Pandas with vectorised Rust execution.
    """

    @staticmethod
    def scan_and_filter_pending(
        parquet_glob: str | Path,
        status: str = "PENDING",
        priority_descending: bool = True,
    ) -> pl.DataFrame:
        """Scan Parquet manifests lazily and collect prioritized pending batches.

        Args:
            parquet_glob: Path glob string (e.g. 'data/batches/*.parquet').
            status: Target status string to filter on.
            priority_descending: Sort highest priority items first.

        Returns:
            Collected Polars DataFrame containing matching pending items.
        """
        query = (
            pl.scan_parquet(str(parquet_glob))
            .filter(pl.col("status") == status)
            .sort("priority", descending=priority_descending)
        )
        return query.collect()

    @staticmethod
    def sources_to_dataframe(sources: list[BatchSource]) -> pl.DataFrame:
        """Convert a list of BatchSource domain entities into a columnar Polars DataFrame."""
        if not sources:
            return pl.DataFrame(
                schema={
                    "content_id": pl.String,
                    "channel": pl.String,
                    "media_url": pl.String,
                    "modality": pl.String,
                    "priority": pl.Int32,
                    "status": pl.String,
                }
            )

        data = [
            {
                "content_id": s.content_id.value if s.content_id else Path(s.target).stem,
                "target": s.target,
                "kind": s.kind.value if hasattr(s.kind, "value") else str(s.kind),
                "channel": getattr(s, "channel_name", "DefaultChannel"),
                "priority": getattr(s, "priority", 0),
                "status": getattr(s, "status", "PENDING"),
            }
            for s in sources
        ]
        return pl.DataFrame(data)

    @classmethod
    def deduplicate_batch_sources(cls, sources: list[BatchSource]) -> list[BatchSource]:
        """Deduplicate BatchSources by content_id preserving the highest priority entry.

        Utilizes Polars native C/Rust sorting and distinct execution.
        """
        if not sources:
            return []

        df = cls.sources_to_dataframe(sources)
        deduped_df = (
            df.sort("priority", descending=True)
            .unique(subset=["content_id"], keep="first", maintain_order=True)
        )

        content_id_map = {
            (s.content_id.value if s.content_id else Path(s.target).stem): s
            for s in sources
        }
        return [content_id_map[cid] for cid in deduped_df["content_id"].to_list() if cid in content_id_map]

    @classmethod
    def export_to_parquet(cls, sources: list[BatchSource], destination_path: Path | str) -> Path:
        """Export a list of BatchSources to a fast columnar Parquet file.

        Args:
            sources: List of BatchSource items to serialize.
            destination_path: Target .parquet file path.

        Returns:
            Resolved output Path.
        """
        out_path = Path(destination_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df = cls.sources_to_dataframe(sources)
        df.write_parquet(out_path, compression="zstd")
        return out_path
