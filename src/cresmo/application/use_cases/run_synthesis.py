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

from cresmo.application.ports import (
    MediaIngestionPort,
    NoOpProcessRuntimePort,
    PipelineSettingsProtocol,
    ProcessRuntimePort,
    VaultRepositoryPort,
)
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.domain.exceptions import (
    IngestionNetworkError,
    QuotaPoolExhaustedError,
    RateLimitExceededError,
)
from cresmo.domain.value_objects import (
    BatchId,
    ChannelName,
    SourceModality,
    SyncFilterCriteria,
    is_processable_transcript_file,
)

if TYPE_CHECKING:
    from cresmo.application.pipeline import CresmoPipeline
    from cresmo.application.use_cases.concat_master import ConcatMasterUseCase
    from cresmo.application.use_cases.discovery import (
        BatchDiscoveryQuery,
        BatchSource,
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

    PREFLIGHT_WARNING = "preflight_warning"
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
    item_prefix: str = ""
    content_id: str | None = None
    target: str | None = None


@dataclass(frozen=True, slots=True)
class RunSynthesisRequest:
    """Immutable request DTO specifying synthesis run parameters."""

    url: str | None = None
    manifest: Path | None = None
    passes: int = 3
    batch_size: int | None = None
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
    mode: str
    batch_id: BatchId | None = None
    completed: int = 0
    skipped: int = 0
    failed: int = 0
    aborted_by_quota: bool = False
    total_items: int = 0
    dry_run: bool = False
    empty_sources: bool = False
    master_parts_generated: int = 0
    master_channels_count: int = 0
    single_notes_count: int = 0
    single_mocs_count: int = 0
    single_duplicates_unified: int = 0
    single_content_id: str | None = None
    single_dry_run_chars: int | None = None
    single_dry_run_url: str | None = None
    dry_run_validated: int = 0
    dry_run_total: int = 0
    manifest_display: str = "data/playlist.txt"
    scan_raw: bool = False
    error_message: str | None = None


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
        settings: PipelineSettingsProtocol,
        preflight_checker: PreflightHealthChecker,
        pipeline_factory: Callable[[], CresmoPipeline],
        discover_sources_factory: Callable[
            [MediaIngestionPort, Callable[[str], object] | None],
            DiscoverBatchSourcesUseCase,
        ],
        concat_master_factory: Callable[[VaultRepositoryPort], ConcatMasterUseCase],
        runtime_port: ProcessRuntimePort | None = None,
    ) -> None:
        self._settings = settings
        self._preflight_checker = preflight_checker
        self._pipeline_factory = pipeline_factory
        self._discover_sources_factory = discover_sources_factory
        self._concat_master_factory = concat_master_factory
        self._runtime_port = runtime_port or NoOpProcessRuntimePort()

    def execute(
        self,
        request: RunSynthesisRequest,
        on_event: Callable[[BatchItemEvent], None] | None = None,
    ) -> RunSynthesisOutcome:
        """Execute preflight validation, warmup, and single-video or batch synthesis.

        Args:
            request: Immutable synthesis execution request parameters.
            on_event: Optional progress event observer callback.

        Returns:
            RunSynthesisOutcome summarizing exit status and item metrics.
        """
        preflight_result = self._preflight_checker.check_all()
        preflight_result.assert_healthy()
        for warning in preflight_result.warnings:
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.PREFLIGHT_WARNING,
                    message=warning,
                ),
            )

        pipeline = self._pipeline_factory()
        if not request.web_index:
            pipeline.warmup()

        if request.url:
            return self._execute_single_video(pipeline, request, on_event)
        return self._execute_batch(pipeline, request, on_event)

    def _execute_single_video(
        self,
        pipeline: CresmoPipeline,
        request: RunSynthesisRequest,
        on_event: Callable[[BatchItemEvent], None] | None,
    ) -> RunSynthesisOutcome:
        video_url = request.url or ""
        if request.dry_run:
            raw_transcript = pipeline.ingest_raw_transcript.execute(video_url=video_url)
            if raw_transcript is None:
                return RunSynthesisOutcome(
                    status=RunExitStatus.INGESTION_ERROR,
                    mode="single",
                    dry_run=True,
                    single_dry_run_url=video_url,
                )
            return RunSynthesisOutcome(
                status=RunExitStatus.SUCCESS,
                mode="single",
                dry_run=True,
                single_content_id=raw_transcript.content.id.value,
                single_dry_run_chars=len(raw_transcript.content.text),
                single_dry_run_url=video_url,
            )

        result = pipeline.run_for_video(
            video_url=video_url,
            gap_filler_passes=request.passes,
            force_reprocess=request.force_reprocess,
        )
        content_id_str = result.content_id.value
        if result.already_processed:
            return RunSynthesisOutcome(
                status=RunExitStatus.SUCCESS,
                mode="single",
                skipped=1,
                total_items=1,
                single_content_id=content_id_str,
            )
        if result.success:
            try:
                raw_transcript = pipeline.vault_port.get_stage_transcript(
                    "raw",
                    result.content_id,
                )
                if raw_transcript and raw_transcript.channel.name:
                    concat_master = self._concat_master_factory(pipeline.vault_port)
                    concat_master.execute(ChannelName(raw_transcript.channel.name))
            except Exception as exc:  # noqa: BLE001
                _emit(
                    on_event,
                    BatchItemEvent(
                        kind=BatchItemEventKind.MASTER_WARNING,
                        message=f"Warning: Master consolidation failed: {exc}",
                        content_id=content_id_str,
                    ),
                )
            return RunSynthesisOutcome(
                status=RunExitStatus.SUCCESS,
                mode="single",
                completed=1,
                total_items=1,
                single_notes_count=len(result.synthesized_notes),
                single_mocs_count=len(result.reconciled_mocs),
                single_duplicates_unified=result.duplicates_unified,
                single_content_id=content_id_str,
            )
        return RunSynthesisOutcome(
            status=RunExitStatus.INTERNAL_ERROR,
            mode="single",
            failed=1,
            total_items=1,
            single_content_id=content_id_str,
            error_message=result.error_message,
        )

    def _execute_batch(
        self,
        pipeline: CresmoPipeline,
        request: RunSynthesisRequest,
        on_event: Callable[[BatchItemEvent], None] | None,
    ) -> RunSynthesisOutcome:
        query = self._build_discovery_query(request)
        manifest_display = str(request.manifest) if request.manifest else "data/playlist.txt"

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
        sources = discover_use_case.execute(query=query)

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

    def _build_discovery_query(self, request: RunSynthesisRequest) -> BatchDiscoveryQuery:
        from cresmo.application.use_cases.discovery import BatchDiscoveryQuery

        if request.crawl:
            enable_channel_crawler = True
        else:
            enable_channel_crawler = bool(getattr(self._settings, "enable_channel_crawler", False))

        filter_criteria = SyncFilterCriteria.from_strings(
            channels=list(request.channels),
            categories=list(request.categories),
            video_ids=list(request.video_ids),
        )

        return BatchDiscoveryQuery(
            explicit_manifest=request.manifest,
            scan_raw=request.scan_raw,
            lookback_days=self._settings.days_lookback,
            channel_max_videos=request.channel_max_videos,
            discovery_workers=self._settings.channel_discovery_workers,
            enable_channel_crawler=enable_channel_crawler,
            filter_criteria=filter_criteria,
            queue_maxsize=self._settings.discovery_queue_maxsize,
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
                mode="batch",
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
                            message=(f"{item_prefix} Dry-run skipped artifact: [{file_path.name}]"),
                            item_prefix=item_prefix,
                            target=source.target,
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
                        item_prefix=item_prefix,
                        content_id=file_path.stem,
                        target=source.target,
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
                            item_prefix=item_prefix,
                            content_id=content_id,
                            target=source.target,
                        ),
                    )
                else:
                    _emit(
                        on_event,
                        BatchItemEvent(
                            kind=BatchItemEventKind.DRY_RUN_FAILED,
                            message=f"{item_prefix} Ingestion failed for: {source.target}",
                            item_prefix=item_prefix,
                            target=source.target,
                        ),
                    )

        return RunSynthesisOutcome(
            status=RunExitStatus.SUCCESS,
            mode="batch",
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
                        item_prefix=item_prefix,
                        target=source.target,
                    ),
                )
                break
            finally:
                self._drain_telemetry_and_memory(pipeline)

        total_items = completed + skipped + failed
        if total_items == 0:
            return RunSynthesisOutcome(
                status=RunExitStatus.SUCCESS,
                mode="batch",
                batch_id=batch_id,
                empty_sources=True,
                manifest_display=manifest_display,
                scan_raw=request.scan_raw,
            )

        master_parts = 0
        master_channels = 0
        if completed > 0:
            master_parts, master_channels = self._consolidate_master(pipeline, on_event)

        exit_status = (
            RunExitStatus.RATE_LIMITED
            if aborted_by_quota
            else (RunExitStatus.SUCCESS if failed == 0 else RunExitStatus.INTERNAL_ERROR)
        )
        return RunSynthesisOutcome(
            status=exit_status,
            mode="batch",
            batch_id=batch_id,
            completed=completed,
            skipped=skipped,
            failed=failed,
            aborted_by_quota=aborted_by_quota,
            total_items=total_items,
            master_parts_generated=master_parts,
            master_channels_count=master_channels,
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
                            item_prefix=item_prefix,
                            target=source.target,
                        ),
                    )
                    return "skipped"
                result = pipeline.run_for_text_file(
                    file_path=file_path,
                    gap_filler_passes=request.passes,
                    force_reprocess=request.force_reprocess,
                    batch_id=batch_id,
                )
            else:
                result = pipeline.run_for_video(
                    video_url=source.target,
                    gap_filler_passes=request.passes,
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
                        item_prefix=item_prefix,
                        content_id=content_id,
                        target=source.target,
                    ),
                )
                return "skipped"

            if result.success:
                _emit(
                    on_event,
                    BatchItemEvent(
                        kind=BatchItemEventKind.COMPLETED,
                        message=(
                            f"{item_prefix} [DONE] [{content_id}]: "
                            f"{len(result.synthesized_notes)} atomic notes synthesized, "
                            f"{len(result.reconciled_mocs)} MOCs reconciled, "
                            f"{result.duplicates_unified} duplicate clusters unified."
                        ),
                        item_prefix=item_prefix,
                        content_id=content_id,
                        target=source.target,
                    ),
                )
                return "completed"

            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.ITEM_FAILED,
                    message=f"{item_prefix} [ERROR] {source.target}: {result.error_message}",
                    item_prefix=item_prefix,
                    content_id=content_id,
                    target=source.target,
                ),
            )
            return "failed"
        except QuotaPoolExhaustedError:
            raise
        except RateLimitExceededError as exc:
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.ITEM_RATE_LIMITED,
                    message=f"{item_prefix} [RATE LIMIT] {source.target}: {exc}",
                    item_prefix=item_prefix,
                    target=source.target,
                ),
            )
            return "failed"
        except IngestionNetworkError as exc:
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.ITEM_NETWORK_ERROR,
                    message=f"{item_prefix} [NETWORK ERROR] {source.target}: {exc}",
                    item_prefix=item_prefix,
                    target=source.target,
                ),
            )
            return "failed"
        except Exception as exc:  # noqa: BLE001
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.ITEM_FAILED,
                    message=f"{item_prefix} [FAILED] {source.target}: {exc}",
                    item_prefix=item_prefix,
                    target=source.target,
                ),
            )
            return "failed"

    def _consolidate_master(
        self,
        pipeline: CresmoPipeline,
        on_event: Callable[[BatchItemEvent], None] | None,
    ) -> tuple[int, int]:
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
            return total_parts, channels_count
        except Exception as exc:  # noqa: BLE001
            _emit(
                on_event,
                BatchItemEvent(
                    kind=BatchItemEventKind.MASTER_WARNING,
                    message=f"Warning: Master consolidation failed: {exc}",
                ),
            )
            return 0, 0

    def _drain_telemetry_and_memory(self, pipeline: CresmoPipeline) -> None:
        try:
            pipeline.telemetry_port.flush()
        except Exception:  # noqa: BLE001, S110
            pass
        try:
            self._runtime_port.collect_garbage()
            rss_bytes = self._runtime_port.get_process_rss_bytes()
            pipeline.metrics_port.set_gauge(
                "cresmo_process_resident_memory_bytes",
                rss_bytes,
                labels={"role": "worker"},
            )
            pipeline.metrics_port.increment_counter(
                "cresmo_gc_collections_total",
                1.0,
                labels={"generation": "all"},
            )
        except Exception:  # noqa: BLE001, S110
            pass
