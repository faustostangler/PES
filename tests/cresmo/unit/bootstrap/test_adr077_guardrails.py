"""Hermetic architectural and contract guardrail tests enforcing ADR-077 invariants."""

from __future__ import annotations

import ast
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.application.ports import LLMTransformationPort, MetricName, MetricsPort
from cresmo.application.use_cases.discovery.discover_batch_sources import (
    DiscoverBatchSourcesUseCase,
)
from cresmo.application.use_cases.discovery.models import BatchDiscoveryQuery, DiscoveryPaths
from cresmo.domain.value_objects import (
    ChannelName,
    ChatPrompt,
    ContentId,
    DiscoveredMediaItem,
    EvaluationContext,
    JudgeCriterion,
    PromptKey,
    SyncFilterCriteria,
)
from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter
from cresmo.infrastructure.adapters.judges.ollama_judge import OllamaJudgeAdapter
from cresmo.infrastructure.adapters.judges.prompt_judge_runner import evaluate_prompt_judge
from cresmo.infrastructure.adapters.llm.metrics_decorator import MetricsLLMTransformationDecorator
from cresmo.infrastructure.adapters.media.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.prompts.template_renderer import TemplateRenderer


def test_presentation_layer_has_zero_infrastructure_imports() -> None:
    """AST guard: presentation layer must never import cresmo.infrastructure directly."""
    presentation_root = (
        Path(__file__).resolve().parents[4] / "src" / "cresmo" / "presentation"
    )
    py_files = sorted(presentation_root.rglob("*.py"))
    assert py_files, f"Expected Python files under {presentation_root}"

    violations: list[str] = []
    for file_path in py_files:
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "cresmo.infrastructure" or alias.name.startswith(
                        "cresmo.infrastructure."
                    ):
                        violations.append(f"{file_path.name}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                if module_name == "cresmo.infrastructure" or module_name.startswith(
                    "cresmo.infrastructure."
                ):
                    violations.append(f"{file_path.name}:{node.lineno}: from {module_name}")

    assert violations == [], f"Presentation -> Infrastructure leaks detected: {violations}"


def test_strict_mustache_rendering_fails_fast_on_unresolved_placeholder() -> None:
    """Verify strict Mustache rendering in TemplateRenderer and JsonPromptProvider rejects missing vars."""
    renderer = TemplateRenderer()
    with pytest.raises(ValueError, match=r"Unresolved Mustache placeholder: '\{\{missing\}\}'"):
        renderer.render("Hello {{missing}}", {}, strict=True)

    provider = JsonPromptProvider()
    with pytest.raises(
        ValueError, match=r"Unresolved Mustache placeholder: '\{\{channel_name\}\}'"
    ):
        provider.get_prompt(
            PromptKey.RAW_INDEX_SYNTHESIS,
            content_title="Test Title",
            summary="Summary body",
            language="Português do Brasil",
        )


def test_prompt_judges_fail_fast_when_judge_prompt_key_is_none() -> None:
    """Verify evaluate_prompt_judge, GeminiJudgeAdapter, and OllamaJudgeAdapter reject None prompt key."""
    ctx = EvaluationContext(
        stage_name="fluid_prose",
        raw_text="Source text",
        candidate_text="Candidate text",
        required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        judge_prompt_key=None,
    )
    provider = JsonPromptProvider()

    with pytest.raises(ValueError, match="EvaluationContext.judge_prompt_key is required"):
        evaluate_prompt_judge(
            context=ctx,
            prompt_provider=provider,
            pass_threshold=0.7,
            provider_name="test",
            invoke_llm=lambda _prompt: "{}",
        )

    gemini_judge = GeminiJudgeAdapter(client=MagicMock(), prompt_provider=provider)
    with pytest.raises(ValueError, match="EvaluationContext.judge_prompt_key is required"):
        gemini_judge.evaluate(ctx)

    ollama_judge = OllamaJudgeAdapter(http_client=MagicMock(), prompt_provider=provider)
    with pytest.raises(ValueError, match="EvaluationContext.judge_prompt_key is required"):
        ollama_judge.evaluate(ctx)


def test_metrics_llm_transformation_decorator_observes_success_and_error() -> None:
    """Verify MetricsLLMTransformationDecorator records LLM_REQUEST_DURATION on success and error."""
    mock_metrics = MagicMock(spec=MetricsPort)
    inner_ok = MagicMock(spec=LLMTransformationPort)
    inner_ok.transform.return_value = "ok output"
    decorator_ok = MetricsLLMTransformationDecorator(
        inner=inner_ok,
        metrics_port=mock_metrics,
        provider="gemini",
    )

    prompt = ChatPrompt.single_turn(user_prompt="Hello")
    assert decorator_ok.transform(prompt=prompt) == "ok output"
    mock_metrics.observe_histogram.assert_called_once()
    call_args = mock_metrics.observe_histogram.call_args
    assert call_args[0][0] == MetricName.LLM_REQUEST_DURATION
    assert call_args[1]["labels"] == {"provider": "gemini", "status": "success"}

    mock_metrics.reset_mock()
    inner_fail = MagicMock(spec=LLMTransformationPort)
    inner_fail.transform.side_effect = RuntimeError("LLM timeout")
    decorator_fail = MetricsLLMTransformationDecorator(
        inner=inner_fail,
        metrics_port=mock_metrics,
        provider="ollama",
    )
    with pytest.raises(RuntimeError, match="LLM timeout"):
        decorator_fail.transform(prompt=prompt)
    mock_metrics.observe_histogram.assert_called_once()
    fail_args = mock_metrics.observe_histogram.call_args
    assert fail_args[0][0] == MetricName.LLM_REQUEST_DURATION
    assert fail_args[1]["labels"] == {"provider": "ollama", "status": "error"}


def test_metrics_llm_transformation_decorator_forwards_args_warmup_and_duration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify default provider label, argument forwarding, warmup delegation, and perf_counter delta."""
    import time

    clock = iter([10.0, 10.35])
    monkeypatch.setattr(time, "perf_counter", lambda: next(clock))

    mock_metrics = MagicMock(spec=MetricsPort)
    inner = MagicMock(spec=LLMTransformationPort)
    inner.transform.return_value = "delegated"
    decorator = MetricsLLMTransformationDecorator(inner=inner, metrics_port=mock_metrics)

    decorator.warmup()
    inner.warmup.assert_called_once_with()

    prompt = ChatPrompt.single_turn(user_prompt="Hello")
    result = decorator.transform(
        prompt=prompt,
        temperature=0.4,
        trace_id="tr-99",
        session_id="sess-77",
        user_id="usr-55",
    )

    assert result == "delegated"
    inner.transform.assert_called_once_with(
        prompt=prompt,
        temperature=0.4,
        trace_id="tr-99",
        session_id="sess-77",
        user_id="usr-55",
    )
    mock_metrics.observe_histogram.assert_called_once_with(
        MetricName.LLM_REQUEST_DURATION,
        pytest.approx(0.35),
        labels={"provider": "llm", "status": "success"},
    )


def test_native_media_ingestion_records_failures_and_bounded_duration_labels() -> None:
    """Verify ingest_single_video records INGESTION_FAILURES and MEDIA_INGESTION_DURATION without channel_id."""
    mock_metrics = MagicMock(spec=MetricsPort)
    adapter = NativeMediaIngestionAdapter(
        metrics_port=mock_metrics,
        http_client=MagicMock(),
        transcriber=MagicMock(),
    )

    with patch.object(adapter, "_fetch_video_metadata", return_value=None):
        assert adapter.ingest_single_video("https://youtube.com/watch?v=test_01234") is None

    mock_metrics.increment_counter.assert_called_once_with(
        MetricName.INGESTION_FAILURES,
        1.0,
        labels={"error_type": "empty_metadata"},
    )
    hist_args = mock_metrics.observe_histogram.call_args
    assert hist_args[0][0] == MetricName.MEDIA_INGESTION_DURATION
    assert hist_args[1]["labels"] == {"modality": "url", "status": "failure"}
    assert "channel_id" not in hist_args[1]["labels"]

    mock_metrics.reset_mock()
    with (
        patch.object(adapter, "_fetch_video_metadata", side_effect=RuntimeError("yt-dlp boom")),
        pytest.raises(RuntimeError, match="yt-dlp boom"),
    ):
        adapter.ingest_single_video("https://youtube.com/watch?v=test_01234")

    mock_metrics.increment_counter.assert_called_once_with(
        MetricName.INGESTION_FAILURES,
        1.0,
        labels={"error_type": "RuntimeError"},
    )
    hist_err_args = mock_metrics.observe_histogram.call_args
    assert hist_err_args[0][0] == MetricName.MEDIA_INGESTION_DURATION
    assert hist_err_args[1]["labels"] == {"modality": "url", "status": "failure"}


def test_discover_batch_sources_emits_discovered_and_queue_metrics(tmp_path: Path) -> None:
    """Verify DiscoverBatchSourcesUseCase emits BATCH_SOURCES_DISCOVERED and DISCOVERY_QUEUE_SIZE."""
    seed_playlist = tmp_path / "seeds.txt"
    seed_playlist.write_text("https://youtube.com/@guardchannel\n", encoding="utf-8")

    mock_metrics = MagicMock(spec=MetricsPort)
    mock_ingestion = MagicMock()
    mock_ingestion.discover_channel_feed.return_value = [
        DiscoveredMediaItem(
            content_id=ContentId("vid_guard_1"),
            title="Guard Video",
            published_at=datetime.now(UTC),
            media_url="https://youtube.com/watch?v=vid_guard_1",
            channel_name=ChannelName("GuardChan"),
        )
    ]
    use_case = DiscoverBatchSourcesUseCase(
        media_ingestion_port=mock_ingestion,
        discovery_paths=DiscoveryPaths(
            raw_dir=tmp_path / "raw",
            playlist_path=seed_playlist,
            priority_texts_dir=tmp_path / "priority",
        ),
        metrics_port=mock_metrics,
    )
    query = BatchDiscoveryQuery(
        explicit_manifest=None,
        raw_dir=tmp_path / "raw",
        priority_texts_dir=tmp_path / "priority",
        playlist_path=seed_playlist,
        enable_channel_crawler=True,
        scan_raw=False,
        filter_criteria=SyncFilterCriteria(),
    )

    discovered = list(use_case.execute(query))
    assert len(discovered) == 1
    mock_metrics.increment_counter.assert_any_call(
        MetricName.BATCH_SOURCES_DISCOVERED,
        1.0,
        labels={"modality": "url"},
    )
    queue_calls = [call[0][0] for call in mock_metrics.set_gauge.call_args_list]
    assert MetricName.DISCOVERY_QUEUE_SIZE in queue_calls
