"""Unit tests for ARQ distributed worker settings and job execution."""

from __future__ import annotations

import pytest

from cresmo.infrastructure.workers.arq_worker import (
    WorkerSettings,
    get_redis_settings,
    job_extract_audio,
    job_process_pipeline_stage,
    job_sync_feed,
)


def test_worker_settings_configuration() -> None:
    """Verify that WorkerSettings registers the required jobs and timeout defaults."""
    assert job_process_pipeline_stage in WorkerSettings.functions
    assert job_extract_audio in WorkerSettings.functions
    assert job_sync_feed in WorkerSettings.functions
    assert WorkerSettings.job_timeout >= 300
    assert WorkerSettings.max_tries >= 3


def test_redis_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that RedisSettings parses environment variables."""
    monkeypatch.setenv("REDIS_HOST", "redis.internal")
    monkeypatch.setenv("REDIS_PORT", "6380")

    settings = get_redis_settings()
    assert settings.host == "redis.internal"
    assert settings.port == 6380


@pytest.mark.asyncio
async def test_job_process_pipeline_stage_mock_execution() -> None:
    """Verify that job_process_pipeline_stage executes via injected stage_runner mock."""

    class MockStageRunner:
        def execute_stage(self, stage: str, source: str, context: object) -> str:
            return f"Processed {stage}: {source.upper()}"

    ctx = {
        "job_id": "test_job_123",
        "job_try": 1,
        "stage_runner": MockStageRunner(),
        "settings": None,
    }

    result = await job_process_pipeline_stage(
        ctx=ctx,
        stage_name="fluid_prose",
        content_id="test_content",
        channel="MyChannel",
        source_payload="sample text",
    )

    assert result["status"] == "COMPLETED"
    assert result["stage_name"] == "fluid_prose"
    assert result["content_id"] == "test_content"
    assert "Processed fluid_prose: SAMPLE TEXT" in result["result"]


@pytest.mark.asyncio
async def test_job_extract_audio_mock_execution() -> None:
    """Verify that job_extract_audio executes via injected ingestion adapter."""

    class MockTranscriptContent:
        body = "extracted transcript text"

    class MockTranscript:
        content = MockTranscriptContent()

    class MockIngestionAdapter:
        def ingest_single_video(
            self, video_url: str, output_dir: object, whisper_model: str
        ) -> MockTranscript:
            return MockTranscript()

    ctx = {
        "job_id": "test_audio_123",
        "job_try": 1,
        "ingestion_adapter": MockIngestionAdapter(),
        "settings": None,
    }

    result = await job_extract_audio(
        ctx=ctx,
        content_id="audio_content_1",
        media_url="https://example.com/watch?v=123",
    )

    assert result["status"] == "COMPLETED"
    assert result["content_id"] == "audio_content_1"
    assert result["text_length"] == len("extracted transcript text")


@pytest.mark.asyncio
async def test_job_sync_feed_mock_execution() -> None:
    """Verify that job_sync_feed executes via injected sync_channel_use_case."""

    class MockReport:
        total_discovered = 10
        processed_count = 8
        skipped_count = 1
        failed_count = 1

    class MockSyncUseCase:
        def execute(self, query: object) -> MockReport:
            return MockReport()

    ctx = {
        "job_id": "test_sync_123",
        "job_try": 1,
        "sync_channel_use_case": MockSyncUseCase(),
        "settings": None,
    }

    result = await job_sync_feed(
        ctx=ctx,
        channel_url="https://youtube.com/@test",
        max_videos=5,
        lookback_days=3,
    )

    assert result["status"] == "COMPLETED"
    assert result["channel_url"] == "https://youtube.com/@test"
    assert result["total_discovered"] == 10
    assert result["processed_count"] == 8
    assert result["skipped_count"] == 1
    assert result["failed_count"] == 1
