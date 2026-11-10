"""ARQ Distributed Async Worker for Cresmo Pipeline Tasks.

Replaces local synchronous polling with high-throughput Redis job queues.
Executes heavy AI synthesis stages (fluid_prose, gap_filler, long_expander,
Whisper audio extraction) with automated retries, timeouts, and graceful shutdown.

Conforms to:
- ADR-003: PES Production Architecture & Telemetry
- ADR-005: Multi-Role 12-Factor Container & Settings
- Technology Stack Reference §2 (Layer 1: Distributed Task Queue)
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

import structlog
from arq import Retry
from arq.connections import RedisSettings

logger = structlog.get_logger(__name__)

# Timeout configurations per job profile
_DEFAULT_JOB_TIMEOUT_SECONDS: int = 600  # 10 minutes for long synthesis/transcription
_DEFAULT_MAX_RETRIES: int = 3
_DEFAULT_RETRY_DELAY_SECONDS: int = 15

_STAGE_RUNNER_FACTORY: Callable[..., Any] | None = None
_MEDIA_INGESTION_FACTORY: Callable[..., Any] | None = None
_SYNC_CHANNEL_FACTORY: Callable[..., Any] | None = None


def register_stage_runner_factory(factory: Callable[..., Any]) -> None:
    """Register stage runner builder hook to decouple infrastructure from presentation (ADR-048)."""
    global _STAGE_RUNNER_FACTORY
    _STAGE_RUNNER_FACTORY = factory


def get_stage_runner_factory() -> Callable[..., Any] | None:
    """Return registered stage runner builder hook."""
    return _STAGE_RUNNER_FACTORY


def register_media_ingestion_factory(factory: Callable[..., Any]) -> None:
    """Register media ingestion builder hook to decouple infrastructure from presentation (ADR-051)."""
    global _MEDIA_INGESTION_FACTORY
    _MEDIA_INGESTION_FACTORY = factory


def get_media_ingestion_factory() -> Callable[..., Any] | None:
    """Return registered media ingestion builder hook."""
    return _MEDIA_INGESTION_FACTORY


def register_sync_channel_factory(factory: Callable[..., Any]) -> None:
    """Register sync channel use case builder hook to decouple infrastructure from presentation (ADR-051)."""
    global _SYNC_CHANNEL_FACTORY
    _SYNC_CHANNEL_FACTORY = factory


def get_sync_channel_factory() -> Callable[..., Any] | None:
    """Return registered sync channel use case builder hook."""
    return _SYNC_CHANNEL_FACTORY


async def job_process_pipeline_stage(
    ctx: dict[str, Any],
    stage_name: str,
    content_id: str,
    channel: str,
    source_payload: str,
) -> dict[str, Any]:
    """Execute a heavy LLM conveyor stage as an asynchronous background job.

    Args:
        ctx: ARQ worker execution context.
        stage_name: Registered stage identifier (e.g. 'fluid_prose', 'gap_filler').
        content_id: Target ContentId string.
        channel: Origin channel name string.
        source_payload: Text source passed to the stage runner.

    Returns:
        Dictionary report containing stage outcome, status, and output text.
    """
    job_id = ctx.get("job_id", "unknown")
    job_try = ctx.get("job_try", 1)
    logger.info(
        "Executing pipeline stage job [stage=%s, content_id=%s, try=%d, job_id=%s]",
        stage_name,
        content_id,
        job_try,
        job_id,
    )

    try:
        from cresmo.application.pipeline.context import PipelineExecutionContext
        from cresmo.domain.entities import UserIdentity
        from cresmo.domain.value_objects import (
            Channel,
            ChannelId,
            ChannelName,
            Content,
            ContentId,
        )
        from cresmo.infrastructure.config import resolve_shared_settings

        settings = ctx.get("settings") or resolve_shared_settings()
        stage_runner = ctx.get("stage_runner")
        if stage_runner is None:
            factory = ctx.get("stage_runner_factory") or _STAGE_RUNNER_FACTORY
            if factory is not None:
                stage_runner = factory(settings=settings)
            else:
                raise RuntimeError(
                    "Stage runner factory not configured in worker context. "
                    "Register via register_stage_runner_factory() or inject ctx['stage_runner']."
                )

        session_key = f"{channel}:{content_id}"
        exec_context = PipelineExecutionContext(
            user_identity=UserIdentity("arq-worker"),
            channel=Channel(name=ChannelName(channel), id=ChannelId(channel)),
            content=Content(
                id=ContentId(content_id),
                title=content_id,
                body=source_payload,
                session_id=session_key,
            ),
        )

        result_text = stage_runner.execute_stage(
            stage=stage_name,
            source=source_payload,
            context=exec_context,
        )

        return {
            "status": "COMPLETED",
            "stage_name": stage_name,
            "content_id": content_id,
            "output_length": len(result_text),
            "result": result_text,
        }

    except Exception as exc:
        logger.exception(
            "Stage job failed [stage=%s, content_id=%s, try=%d]",
            stage_name,
            content_id,
            job_try,
        )
        if job_try < _DEFAULT_MAX_RETRIES:
            raise Retry(defer=job_try * _DEFAULT_RETRY_DELAY_SECONDS) from exc
        return {
            "status": "FAILED",
            "stage_name": stage_name,
            "content_id": content_id,
            "error": str(exc),
        }


async def job_extract_audio(
    ctx: dict[str, Any],
    content_id: str,
    media_url: str,
) -> dict[str, Any]:
    """Execute native media ingestion and Whisper audio extraction in background.

    Args:
        ctx: ARQ worker execution context.
        content_id: Target ContentId.
        media_url: Stream or YouTube URL to download.

    Returns:
        Report dictionary with extraction outcome.
    """
    job_id = ctx.get("job_id", "unknown")
    job_try = ctx.get("job_try", 1)
    logger.info("Executing audio extraction job [content_id=%s, job_id=%s]", content_id, job_id)

    try:
        from cresmo.infrastructure.config import resolve_shared_settings

        settings = ctx.get("settings") or resolve_shared_settings()
        ingestion_adapter = ctx.get("ingestion_adapter")
        if ingestion_adapter is None:
            factory = ctx.get("media_ingestion_factory") or _MEDIA_INGESTION_FACTORY
            if factory is not None:
                ingestion_adapter = factory(settings=settings)
            else:
                from cresmo.infrastructure.adapters.header_generator import RandomHeaderGenerator
                from cresmo.infrastructure.adapters.native_media_ingestion_adapter import (
                    NativeMediaIngestionAdapter,
                )

                headers_path = getattr(settings, "browser_headers_path", None)
                cookie_file = getattr(settings, "cookies_file", None)
                header_generator = RandomHeaderGenerator(headers_path=headers_path)
                whisper_workers = getattr(settings, "whisper_workers", 1)
                ingestion_adapter = NativeMediaIngestionAdapter(
                    header_generator=header_generator,
                    cookie_file=Path(cookie_file) if cookie_file else None,
                    whisper_concurrency_limit=whisper_workers,
                )

        output_dir = Path(getattr(settings, "raw_dir", "data/raw"))
        transcript_obj = ingestion_adapter.ingest_single_video(
            video_url=media_url,
            output_dir=output_dir,
            whisper_model=getattr(settings, "whisper_model", "base"),
        )
        body = transcript_obj.content.body if transcript_obj else ""
        return {
            "status": "COMPLETED",
            "content_id": content_id,
            "text_length": len(body),
        }
    except Exception as exc:
        logger.error(
            "Audio extraction failed [content_id=%s, try=%d]: %s", content_id, job_try, exc
        )
        if job_try < _DEFAULT_MAX_RETRIES:
            raise Retry(defer=job_try * _DEFAULT_RETRY_DELAY_SECONDS) from exc
        return {"status": "FAILED", "content_id": content_id, "error": str(exc)}


async def job_sync_feed(
    ctx: dict[str, Any],
    channel_url: str,
    max_videos: int = 10,
    lookback_days: int = 7,
) -> dict[str, Any]:
    """Execute channel polling and feed synchronization as an isolated Redis task."""
    logger.info("Executing sync feed job [channel_url=%s, max_videos=%d]", channel_url, max_videos)
    from cresmo.domain.value_objects import ChannelFeedQuery
    from cresmo.infrastructure.config import resolve_shared_settings

    settings = ctx.get("settings") or resolve_shared_settings()
    sync_use_case = ctx.get("sync_channel_use_case")
    if sync_use_case is None:
        factory = ctx.get("sync_channel_factory") or _SYNC_CHANNEL_FACTORY
        if factory is not None:
            sync_use_case = factory(settings=settings)
        else:
            raise RuntimeError(
                "Sync channel use case not configured in worker context. "
                "Register via register_sync_channel_factory() or inject ctx['sync_channel_use_case']."
            )

    query = ChannelFeedQuery(
        channel_url=channel_url,
        max_videos=max_videos,
        lookback_days=lookback_days,
    )
    report = sync_use_case.execute(query)
    return {
        "status": "COMPLETED",
        "channel_url": channel_url,
        "total_discovered": report.total_discovered,
        "processed_count": report.processed_count,
        "skipped_count": report.skipped_count,
        "failed_count": report.failed_count,
    }


async def startup(ctx: dict[str, Any]) -> None:
    """Initialize shared connections, settings, and telemetry on worker boot."""
    logger.info("Starting ARQ Worker for Cresmo Knowledge Engine...")
    from cresmo.infrastructure.config import resolve_shared_settings

    try:
        from cresmo.presentation.composition import bind_arq_worker_factories

        bind_arq_worker_factories()
    except ImportError:
        pass

    ctx["settings"] = resolve_shared_settings()


async def shutdown(ctx: dict[str, Any]) -> None:
    """Graceful termination and cleanup of resources."""
    logger.info("Shutting down ARQ Worker cleanly...")


def get_redis_settings() -> RedisSettings:
    """Resolve Redis connection settings from environment variables with fail-safe defaults."""
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD") or None
    return RedisSettings(
        host=redis_host,
        port=redis_port,
        password=redis_password,
    )


class WorkerSettings:
    """Canonical ARQ Worker Configuration.

    Executed via: `arq cresmo.infrastructure.workers.arq_worker.WorkerSettings`
    """

    functions: ClassVar[list[Any]] = [
        job_process_pipeline_stage,
        job_extract_audio,
        job_sync_feed,
    ]
    on_startup: ClassVar[Any] = startup
    on_shutdown: ClassVar[Any] = shutdown
    redis_settings: ClassVar[RedisSettings] = get_redis_settings()
    max_jobs: ClassVar[int] = 10
    job_timeout: ClassVar[int] = _DEFAULT_JOB_TIMEOUT_SECONDS
    max_tries: ClassVar[int] = _DEFAULT_MAX_RETRIES
    retry_jobs: ClassVar[bool] = True
