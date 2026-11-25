"""Application Use Case orchestrating single-video and batch knowledge synthesis.

Conforms to:
    - ADR-009: Streaming Batch Source Discovery Producer-Consumer Pattern
    - ADR-015: Artifact Segregation and Exclusion Invariants
    - ADR-041: Gemini Credential Pool and Quota-Aware Failover Rotation
    - ADR-067: Humble Presentation CLI and Run/Sync Use Cases
    - SPEC-067: Humble Presentation CLI & Run/Sync Use Cases
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sized
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from cresmo.application.ports import (
    MediaIngestionPort,
    MetricName,
    NoOpProcessRuntimePort,
    ProcessRuntimePort,
    VaultRepositoryPort,
)
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.discovery.models import BatchDiscoveryQuery, BatchSource
from cresmo.domain.exceptions import (
    IngestionNetworkError,
    QuotaPoolExhaustedError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import (
    BatchId,
    DiscoveryPolicy,
    SourceModality,
    SyncFilterCriteria,
    is_processable_transcript_file,
)

logger = structlog.get_logger(__name__)

if TYPE_CHECKING:
    from cresmo.application.pipeline.coordinator import CresmoPipeline
    from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
    from cresmo.application.use_cases.discovery.discover_batch_sources import (
        DiscoverBatchSourcesUseCase,
    )


class RunExitStatus(StrEnum):
    """Canonical application termination status for synthesis runs."""

    SUCCESS = "success"
    RATE_LIMITED = "rate_limited"
    INGESTION_ERROR = "ingestion_error"
    INTERNAL_ERROR = "internal_error"


class BatchItemEventKind(StrEnum):
    """Event discriminators emitted during synthesis run execution."""

    DISCOVERY_PROGRESS = "discovery_progress"
    SKIPPED_ARTIFACT = "skipped_artifact"
    SKIPPED_IDEMPOTENT = "skipped_idempotent"
    COMPLETED = "completed"
    DRY_RUN_TEXT = "dry_run_text"
    DRY_RUN_URL = "dry_run_url"
    DRY_RUN_FAILED = "dry_run_failed"
    ITEM_RATE_LIMITED = "item_rate_limited"
    ITEM_NETWORK_ERROR = "item_network_error"
    ITEM_FAILED = "item_failed"
    QUOTA_ABORT = "quota_abort"
    MASTER_WARNING = "master_warning"
    MASTER_CONSOLIDATED = "master_consolidated"


@dataclass(frozen=True, slots=True)
class BatchItemEvent:
    """Immutable progress event emitted to driving adapters (CLI/UI)."""

    kind: BatchItemEventKind
    message: str


@dataclass(frozen=True, slots=True)
class RunSynthesisRequest:
    """Immutable request DTO specifying synthesis run parameters."""

    url: str | None = None
    manifest: Path | None = None
    passes: int | None = None
    dry_run: bool = False
    force_reprocess: bool = False
    lookback: int | None = None
    channel_max_videos: int = 50
    scan_raw: bool = False
    crawl: bool = False
    web_index: bool = False
    channels: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    video_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RunSynthesisOutcome:
    """Immutable summary outcome returned by RunSynthesisUseCase."""

    status: RunExitStatus
    batch_id: BatchId | None = None
    completed: int = 0
    skipped: int = 0
    failed: int = 0
    total_items: int = 0
    dry_run: bool = False
    empty_sources: bool = False
    dry_run_validated: int = 0
    dry_run_total: int = 0
    manifest_display: str = ""
    scan_raw: bool = False


def _emit(
    on_event: Callable[[BatchItemEvent], None] | None,
    event: BatchItemEvent,
) -> None:
    if on_event is not None:
        on_event(event)


class RunSynthesisUseCase:
    """Application orchestrator for single-video and prioritized batch synthesis."""

    def __init__(
        self,
        discovery_policy: DiscoveryPolicy,
        preflight_checker: PreflightHealthChecker,
        pipeline_factory: Callable[[], CresmoPipeline],
        discover_sources_factory: Callable[
            [MediaIngestionPort, Callable[[str], object] | None],
            DiscoverBatchSourcesUseCase,
        ],
        concat_master_factory: Callable[[VaultRepositoryPort], ConcatMasterUseCase],
        runtime_port: ProcessRuntimePort | None = None,
        default_manifest_path: Path | None = None,
    ) -> None:
        self._discovery_policy = discovery_policy
        self._preflight_checker = preflight_checker
        self._pipeline_factory = pipeline_factory
        self._discover_sources_factory = discover_sources_factory
        self._concat_master_factory = concat_master_factory
        self._runtime_port = runtime_port or NoOpProcessRuntimePort()
        self._default_manifest_display = (
            str(default_manifest_path) if default_manifest_path is not None else ""
        )

    def execute(
        self,
        request: RunSynthesisRequest,
        on_event: Callable[[BatchItemEvent], None] | None = None,
    ) -> RunSynthesisOutcome:
        """Execute preflight validation, warmup, and unified batch synthesis.

        Args:
            request: Immutable synthesis execution request parameters.
            on_event: Optional progress event observer callback.

        Returns:
            RunSynthesisOutcome summarizing exit status and item metrics.
        """
        preflight_result = self._preflight_checker.check_all()
        preflight_result.assert_healthy()

        pipeline = self._pipeline_factory()
        if not request.dry_run:
            pipeline.warmup()

        if request.url:
            sources: Iterable[BatchSource] = [
                BatchSource(kind=SourceModality.URL, target=request.url)
            ]
            manifest_display = request.url
        else:
            sources, manifest_display = self._discover_sources(pipeline, request, on_event)

        if request.dry_run:
            return self._execute_batch_dry_run(
                pipeline=pipeline,
                sources=list(sources),
                manifest_display=manifest_display,
                scan_raw=request.scan_raw,
                on_event=on_event,
            )
        return self._execute_batch_run(
            pipeline=pipeline,
            sources=sources,
            request=request,
            manifest_display=manifest_display,
            on_event=on_event,
        )

    def _discover_sources(
        self,
        pipeline: CresmoPipeline,
        request: RunSynthesisRequest,
        on_event: Callable[[BatchItemEvent], None] | None,
    ) -> tuple[Iterable[BatchSource], str]:
        query = self._build_discovery_query(request)
        manifest_display = (
            str(request.manifest) if request.manifest else self._default_manifest_display
        )

        def _on_progress(msg: str) -> None:
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.DISCOVERY_PROGRESS,
                    message=msg,
                ),
            )

        discover_use_case = self._discover_sources_factory(
            pipeline.media_ingestion_port,
            _on_progress,
        )
        return discover_use_case.execute(query=query), manifest_display

    def _build_discovery_query(self, request: RunSynthesisRequest) -> BatchDiscoveryQuery:
        enable_channel_crawler = (
            True if request.crawl else self._discovery_policy.enable_channel_crawler
        )

        filter_criteria = SyncFilterCriteria.from_strings(
            channels=list(request.channels),
            categories=list(request.categories),
            video_ids=list(request.video_ids),
        )

        lookback_days = (
            request.lookback
            if request.lookback is not None
            else self._discovery_policy.lookback_days
        )
        return BatchDiscoveryQuery(
            explicit_manifest=request.manifest,
            scan_raw=request.scan_raw,
            lookback_days=lookback_days,
            channel_max_videos=request.channel_max_videos,
            discovery_workers=self._discovery_policy.discovery_workers,
            enable_channel_crawler=enable_channel_crawler,
            filter_criteria=filter_criteria,
            queue_maxsize=self._discovery_policy.queue_maxsize,
        )

    def _execute_batch_dry_run(
        self,
        *,
        pipeline: CresmoPipeline,
        sources: list[BatchSource],
        manifest_display: str,
        scan_raw: bool,
        on_event: Callable[[BatchItemEvent], None] | None,
    ) -> RunSynthesisOutcome:
        if not sources:
            return RunSynthesisOutcome(
                status=RunExitStatus.SUCCESS,
                dry_run=True,
                empty_sources=True,
                manifest_display=manifest_display,
                scan_raw=scan_raw,
            )

        validated = 0
        total = len(sources)
        for source_index, source in enumerate(sources, 1):
            item_prefix = f"[{source_index}/{total}]"
            if source.kind is SourceModality.FILE:
                file_path = Path(source.target)
                if not is_processable_transcript_file(file_path):
                    _emit(
                        on_event,
                        BatchItemEvent(
                            kind=BatchItemEventKind.SKIPPED_ARTIFACT,
                            message=f"{item_prefix} Dry-run skipped artifact: [{file_path.name}]",
                        ),
                    )
                    continue
                size_bytes = self._runtime_port.get_file_size_bytes(file_path)
                validated += 1
                _emit(
                    on_event,
                    BatchItemEvent(
                        kind=BatchItemEventKind.DRY_RUN_TEXT,
                        message=(
                            f"{item_prefix} Dry-run text: [{file_path.stem}] ({size_bytes} bytes)"
                        ),
                    ),
                )
            else:
                raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=source.target)
                if raw_transcript is not None:
                    validated += 1
                    content_id = raw_transcript.content.id.value
                    _emit(
                        on_event,
                        BatchItemEvent(
                            kind=BatchItemEventKind.DRY_RUN_URL,
                            message=(
                                f"{item_prefix} Dry-run ingested: [{content_id}] "
                                f"({len(raw_transcript.content.text)} chars)"
                            ),
                        ),
                    )
                else:
                    _emit(
                        on_event,
                        BatchItemEvent(
                            kind=BatchItemEventKind.DRY_RUN_FAILED,
                            message=f"{item_prefix} Ingestion failed for: {source.target}",
                        ),
                    )

        return RunSynthesisOutcome(
            status=RunExitStatus.SUCCESS,
            dry_run=True,
            dry_run_validated=validated,
            dry_run_total=total,
            manifest_display=manifest_display,
            scan_raw=scan_raw,
        )

    def _execute_batch_run(
        self,
        *,
        pipeline: CresmoPipeline,
        sources: Iterable[BatchSource],
        request: RunSynthesisRequest,
        manifest_display: str,
        on_event: Callable[[BatchItemEvent], None] | None,
    ) -> RunSynthesisOutcome:
        completed = 0
        skipped = 0
        failed = 0
        batch_id = BatchId.generate()
        aborted_by_quota = False
        total_suffix = f"/{len(sources)}" if isinstance(sources, Sized) else ""

        for source_index, source in enumerate(sources, 1):
            item_prefix = f"[{source_index}{total_suffix}]"
            try:
                status = self._process_batch_item(
                    pipeline=pipeline,
                    source=source,
                    request=request,
                    item_prefix=item_prefix,
                    batch_id=batch_id,
                    on_event=on_event,
                )
                if status == "completed":
                    completed += 1
                elif status == "skipped":
                    skipped += 1
                else:
                    failed += 1
            except QuotaPoolExhaustedError as exc:
                failed += 1
                aborted_by_quota = True
                _emit(
                    on_event,
                    BatchItemEvent(
                        kind=BatchItemEventKind.QUOTA_ABORT,
                        message=(
                            f"{item_prefix} [COOLDOWN ABORT] {source.target}: {exc}\n"
                            "Halting batch processing immediately (fail-fast cooldown)."
                        ),
                    ),
                )
                break
            finally:
                self._drain_telemetry_and_memory(pipeline)

        total_items = completed + skipped + failed
        if total_items == 0:
            return RunSynthesisOutcome(
                status=RunExitStatus.SUCCESS,
                batch_id=batch_id,
                empty_sources=True,
                manifest_display=manifest_display,
                scan_raw=request.scan_raw,
            )

        if completed > 0:
            self._consolidate_master(pipeline, on_event)

        exit_status = (
            RunExitStatus.RATE_LIMITED
            if aborted_by_quota
            else (RunExitStatus.SUCCESS if failed == 0 else RunExitStatus.INTERNAL_ERROR)
        )
        return RunSynthesisOutcome(
            status=exit_status,
            batch_id=batch_id,
            completed=completed,
            skipped=skipped,
            failed=failed,
            total_items=total_items,
            manifest_display=manifest_display,
            scan_raw=request.scan_raw,
        )

    def _process_batch_item(
        self,
        *,
        pipeline: CresmoPipeline,
        source: BatchSource,
        request: RunSynthesisRequest,
        item_prefix: str,
        batch_id: BatchId,
        on_event: Callable[[BatchItemEvent], None] | None,
    ) -> str:
        try:
            if source.kind is SourceModality.FILE:
                file_path = Path(source.target)
                if not is_processable_transcript_file(file_path):
                    _emit(
                        on_event,
                        BatchItemEvent(
                            kind=BatchItemEventKind.SKIPPED_ARTIFACT,
                            message=(
                                f"{item_prefix} [SKIPPED] [{file_path.name}] "
                                "Ignored internal Cresmo artifact or system index."
                            ),
                        ),
                    )
                    return "skipped"
                result = pipeline.run_for_text_file(
                    file_path=file_path,
                    expansion_max_passes=request.passes,
                    force_reprocess=request.force_reprocess,
                    batch_id=batch_id,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=source.target,
                    expansion_max_passes=request.passes,
                    force_reprocess=request.force_reprocess,
                    batch_id=batch_id,
                )

            content_id = result.content_id.value
            if result.already_processed:
                _emit(
                    on_event,
                    BatchItemEvent(
                        kind=BatchItemEventKind.SKIPPED_IDEMPOTENT,
                        message=(
                            f"{item_prefix} [SKIPPED] [{content_id}] Already processed in ledger."
                        ),
                    ),
                )
                return "skipped"

            completed_stages = list(result.stage_artifacts)
            final_stage = completed_stages[-1].value if completed_stages else "none"
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.COMPLETED,
                    message=(
                        f"{item_prefix} [DONE] [{content_id}]: "
                        f"{len(completed_stages)} stages completed ({final_stage})."
                    ),
                ),
            )
            return "completed"
        except QuotaPoolExhaustedError:
            raise
        except RateLimitExceededError as exc:
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.ITEM_RATE_LIMITED,
                    message=f"{item_prefix} [RATE LIMIT] {source.target}: {exc}",
                ),
            )
            return "failed"
        except IngestionNetworkError as exc:
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.ITEM_NETWORK_ERROR,
                    message=f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}",
                ),
            )
            return "failed"
        except Exception as exc:  # noqa: BLE001
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.ITEM_FAILED,
                    message=f"{item_prefix} [FAILED] {source.target}: {exc}",
                ),
            )
            return "failed"

    def _consolidate_master(
        self,
        pipeline: CresmoPipeline,
        on_event: Callable[[BatchItemEvent], None] | None,
    ) -> None:
        try:
            concat_master = self._concat_master_factory(pipeline.vault_port)
            master_results = concat_master.execute_all()
            total_parts = sum(len(parts) for parts in master_results.values())
            channels_count = len(master_results)
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.MASTER_CONSOLIDATED,
                    message=(
                        f"Master consolidation complete: {total_parts} master document(s) "
                        f"generated across {channels_count} channel(s)."
                    ),
                ),
            )
        except Exception as exc:  # noqa: BLE001
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.MASTER_WARNING,
                    message=f"Warning: Master consolidation failed: {exc}",
                ),
            )

    def _drain_telemetry_and_memory(self, pipeline: CresmoPipeline) -> None:
        try:
            pipeline.telemetry_port.flush()
        except Exception as exc:  # noqa: BLE001
            logger.debug("Telemetry flush failed during batch drain: %s", exc)
        try:
            self._runtime_port.collect_garbage()
            rss_bytes = self._runtime_port.get_process_rss_bytes()
            pipeline.metrics_port.set_gauge(
                MetricName.PROCESS_RESIDENT_MEMORY_BYTES,
                rss_bytes,
                labels={"role": "cli"},
            )
            pipeline.metrics_port.increment_counter(
                MetricName.GC_COLLECTIONS,
                1.0,
                labels={"generation": "all"},
            )
            pipeline.metrics_port.flush()
        except Exception as exc:  # noqa: BLE001
            logger.debug("Metrics/GC drain failed during batch drain: %s", exc)
