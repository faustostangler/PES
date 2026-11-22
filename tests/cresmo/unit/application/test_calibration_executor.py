"""Hermetic unit tests for single-stage calibration executor, retries, and cooldowns.

Conforms to:
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from cresmo.application.evals.executor import (
    CalibrationEvent,
    CalibrationEventKind,
    CooldownActiveError,
    evaluate_single_item,
    extract_cooldown_seconds,
    is_transient_retryable_error,
    run_stage_calibration,
)
from cresmo.application.evals.specs import build_stage_specs
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.exceptions import QuotaPoolExhaustedError, RateLimitExceededError
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
)
from tests.doubles.evals_fakes import InMemoryCalibrationCheckpointFake


def _make_item(
    item_id: str = "it_1",
    *,
    verdict: str = "PASS",
    criterion: str = "orality_removal",
    difficulty: str = "easy",
) -> dict[str, Any]:
    return {
        "id": item_id,
        "input": {"raw_text": "raw", "candidate_text": "cand"},
        "expected_output": {"verdict": verdict},
        "metadata": {
            "criterion": criterion,
            "difficulty": difficulty,
            "expected_anomaly": "none",
        },
    }


def _make_eval(
    *,
    passed: bool = True,
    score: float = 0.9,
    criterion: JudgeCriterion | None = None,
    crit_passed: bool | None = None,
    crit_score: float = 0.9,
    crit_reasoning: str = "Targeted",
) -> JudgeEvaluation:
    scores = (
        (
            CriterionScore(
                criterion=criterion,
                score=crit_score,
                passed=passed if crit_passed is None else crit_passed,
                reasoning=crit_reasoning,
            ),
        )
        if criterion is not None
        else ()
    )
    return JudgeEvaluation(
        target_stage="fluid_prose",
        passed=passed,
        overall_score=score,
        criteria_scores=scores,
        provider="gemini",
    )


class TestCalibrationExecutor:
    """Hermetic unit tests verifying pure executor behavior without disk I/O or print."""

    def test_extract_cooldown_and_transient_retry_classification(self) -> None:
        pool_err = QuotaPoolExhaustedError("cooldown", retry_after_seconds=42.5)
        assert extract_cooldown_seconds(pool_err) == 42.5
        assert extract_cooldown_seconds(QuotaPoolExhaustedError("c", retry_after_seconds=0.25)) == (
            0.25
        )
        assert extract_cooldown_seconds(QuotaPoolExhaustedError("c", retry_after_seconds=-5.0)) == (
            0.0
        )
        rate_no_attr = RateLimitExceededError("429")
        assert extract_cooldown_seconds(rate_no_attr) is None
        assert extract_cooldown_seconds(RuntimeError("generic")) is None

        for transient_msg in (
            "HTTP 503",
            "HTTP 504",
            "service unavailable",
            "request timeout",
            "Connection reset by peer",
            "socket timed out",
        ):
            assert is_transient_retryable_error(RuntimeError(transient_msg)) is True

        for quota_msg in (
            "503 resource_exhausted",
            "503 429",
            "503 quota exceeded",
            "503 too many requests",
        ):
            assert is_transient_retryable_error(RuntimeError(quota_msg)) is False

        assert is_transient_retryable_error(pool_err) is False
        seen_exc: list[Exception] = []
        wrapper_err = RuntimeError("timeout wrapper")

        def _is_quota(exc: Exception) -> bool:
            seen_exc.append(exc)
            return exc is wrapper_err

        assert (
            is_transient_retryable_error(
                wrapper_err,
                is_quota_exhausted=_is_quota,
            )
            is False
        )
        assert seen_exc == [wrapper_err]
        assert is_transient_retryable_error(ValueError("validation bug")) is False

    def test_evaluate_single_item_extracts_target_criterion_and_handles_missing_criterion(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        mock_judge = MagicMock(spec=LlmJudgePort)
        eval_obj = _make_eval(
            passed=False,
            score=0.2,
            criterion=JudgeCriterion.ORALITY_REMOVAL,
            crit_passed=True,
            crit_score=0.95,
            crit_reasoning="Criterion clean",
        )
        mock_judge.evaluate.return_value = eval_obj

        res = evaluate_single_item(mock_judge, spec, _make_item())
        ctx = mock_judge.evaluate.call_args.args[0]
        assert ctx.raw_text == "raw"
        assert ctx.candidate_text == "cand"
        assert ctx.stage_name == "fluid_prose"
        assert ctx.required_criteria == spec.required_criteria
        assert res.actual == "FAIL"
        assert res.expected == "PASS"
        assert res.target_actual == "PASS"
        assert res.target_score == 0.95
        assert res.reasoning == "Criterion clean"

        invalid_meta_item = _make_item(criterion="nonexistent_criterion")
        fallback_res = evaluate_single_item(mock_judge, spec, invalid_meta_item)
        assert fallback_res.target_actual == "FAIL"
        assert fallback_res.target_score == 0.2
        assert fallback_res.reasoning == eval_obj.extract_critique()

        no_meta_item: dict[str, Any] = {
            "id": "no_meta",
            "input": {"raw_text": "raw", "candidate_text": "cand"},
            "expected_output": {"verdict": "PASS"},
        }
        no_meta_res = evaluate_single_item(mock_judge, spec, no_meta_item)
        assert no_meta_res.target_actual == "FAIL"
        assert no_meta_res.target_score == 0.2
        assert no_meta_res.reasoning == eval_obj.extract_critique()

        empty_meta_item: dict[str, Any] = {**no_meta_item, "metadata": {}}
        empty_meta_res = evaluate_single_item(mock_judge, spec, empty_meta_item)
        assert empty_meta_res.target_actual == "FAIL"
        assert empty_meta_res.reasoning == eval_obj.extract_critique()

    def test_run_stage_calibration_raises_cooldown_active_error_when_in_cooldown(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        checkpoint = InMemoryCalibrationCheckpointFake()
        checkpoint.record_cooldown("fluid_prose", "gemini", "m1", 2500.0)
        judge = MagicMock(spec=LlmJudgePort)

        with pytest.raises(CooldownActiveError) as exc_info:
            run_stage_calibration(
                judge=judge,
                spec=spec,
                items=[_make_item()],
                provider="gemini",
                model="m1",
                config_hash="h1",
                checkpoint_store=checkpoint,
                now_fn=lambda: 2000.0,
            )

        assert exc_info.value.retry_after_seconds == pytest.approx(500.0)
        assert str(exc_info.value) == "Cooldown active for gemini:m1 (500s remaining)."
        judge.evaluate.assert_not_called()

        checkpoint.record_cooldown("fluid_prose", "gemini", "m_sub", 2000.4)
        with pytest.raises(CooldownActiveError) as sub_sec_exc:
            run_stage_calibration(
                judge=judge,
                spec=spec,
                items=[_make_item()],
                provider="gemini",
                model="m_sub",
                config_hash="h1",
                checkpoint_store=checkpoint,
                now_fn=lambda: 2000.0,
            )
        assert sub_sec_exc.value.retry_after_seconds == pytest.approx(0.4)
        assert str(sub_sec_exc.value) == "Cooldown active for gemini:m_sub (0s remaining)."

    def test_run_stage_calibration_resumes_checkpoints_retries_and_emits_events(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        checkpoint = InMemoryCalibrationCheckpointFake()
        checkpoint.record_item(
            stage="fluid_prose",
            provider="gemini",
            model="m1",
            config_hash="hash-1",
            item_id="it_1",
            payload={
                "actual": "PASS",
                "expected": "PASS",
                "score": 0.95,
                "reasoning": "cached",
                "target_actual": "PASS",
                "target_score": 0.95,
            },
        )
        checkpoint.record_cooldown("fluid_prose", "gemini", "m1", 500.0)

        judge = MagicMock(spec=LlmJudgePort)
        judge.evaluate.side_effect = [
            QuotaPoolExhaustedError("short burst", retry_after_seconds=2.0),
            RuntimeError("503 backend unavailable"),
            _make_eval(
                passed=False,
                score=0.1,
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                crit_passed=False,
                crit_score=0.1,
            ),
        ]

        slept: list[float] = []
        events: list[CalibrationEvent] = []
        items = [_make_item("it_1", verdict="PASS"), _make_item("it_2", verdict="FAIL")]

        results = run_stage_calibration(
            judge=judge,
            spec=spec,
            items=items,
            provider="gemini",
            model="m1",
            config_hash="hash-1",
            checkpoint_store=checkpoint,
            delay=1.0,
            jitter=0.4,
            max_retry_wait=60.0,
            now_fn=lambda: 1000.0,
            sleep_fn=slept.append,
            uniform_fn=lambda _a, _b: 0.25,
            on_event=events.append,
        )

        assert results.skipped_from_checkpoint == 1
        assert results.evaluated_items == 1
        assert results.target_isolated.hit == 1
        assert results.target_isolated.correct_rejection == 1
        assert results.target_isolated.accuracy == 1.0
        assert results.by_criterion["orality_removal"].hit == 1
        assert results.by_criterion["orality_removal"].correct_rejection == 1
        assert results.by_difficulty["easy"].hit == 1
        assert results.by_difficulty["easy"].correct_rejection == 1
        assert slept == [2.5, 3.0]
        assert checkpoint.active_cooldown_until("fluid_prose", "gemini", "m1", now=100.0) is None
        saved_items = checkpoint.load_completed_items("fluid_prose", "gemini", "m1", "hash-1")
        assert saved_items["it_2"] == {
            "actual": "FAIL",
            "expected": "FAIL",
            "score": 0.1,
            "reasoning": "Targeted",
            "target_actual": "FAIL",
            "target_score": 0.1,
        }
        by_kind = {e.kind: e for e in events}
        assert by_kind[CalibrationEventKind.STAGE_STARTED] == CalibrationEvent(
            kind=CalibrationEventKind.STAGE_STARTED,
            message="CALIBRATING [FLUID_PROSE] -> gemini:m1",
            stage="fluid_prose",
            provider="gemini",
            model="m1",
        )
        assert by_kind[CalibrationEventKind.CHECKPOINT_RESUMED] == CalibrationEvent(
            kind=CalibrationEventKind.CHECKPOINT_RESUMED,
            message="Checkpoint resume: 1/2 restored, 1 pending.",
            stage="fluid_prose",
            provider="gemini",
            model="m1",
        )
        assert by_kind[CalibrationEventKind.PACING_INFO] == CalibrationEvent(
            kind=CalibrationEventKind.PACING_INFO,
            message="Pacing: 1.0s base delay + up to 0.4s jitter between calls",
            stage="fluid_prose",
            provider="gemini",
            model="m1",
        )
        assert by_kind[CalibrationEventKind.COOLDOWN_WAIT] == CalibrationEvent(
            kind=CalibrationEventKind.COOLDOWN_WAIT,
            message="  [COOLDOWN WAIT 1/5] it_2: waiting 2.5s (short burst)",
            stage="fluid_prose",
            provider="gemini",
            model="m1",
            item_id="it_2",
        )
        assert by_kind[CalibrationEventKind.RETRY_WAIT] == CalibrationEvent(
            kind=CalibrationEventKind.RETRY_WAIT,
            message=(
                "  [RETRY 1/3] Transient error on 'it_2': 503 backend unavailable. Waiting 3.0s..."
            ),
            stage="fluid_prose",
            provider="gemini",
            model="m1",
            item_id="it_2",
        )
        assert by_kind[CalibrationEventKind.ITEM_EVALUATED] == CalibrationEvent(
            kind=CalibrationEventKind.ITEM_EVALUATED,
            message="[02/02] [it_2                        ] Exp: FAIL | Target: FAIL (0.10) -> CORRECT_REJECTION",
            stage="fluid_prose",
            provider="gemini",
            model="m1",
            item_id="it_2",
        )

    def test_run_stage_calibration_long_cooldown_records_parked_timestamp_and_aborts(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        checkpoint = InMemoryCalibrationCheckpointFake()
        judge = MagicMock(spec=LlmJudgePort)
        judge.evaluate.side_effect = QuotaPoolExhaustedError(
            "daily limit", retry_after_seconds=3600.0
        )
        events: list[CalibrationEvent] = []
        slept: list[float] = []

        with pytest.raises(QuotaPoolExhaustedError):
            run_stage_calibration(
                judge=judge,
                spec=spec,
                items=[_make_item("it_1"), _make_item("it_2")],
                provider="gemini",
                model="m1",
                config_hash="hash-1",
                checkpoint_store=checkpoint,
                max_retry_wait=60.0,
                now_fn=lambda: 1000.0,
                sleep_fn=slept.append,
                on_event=events.append,
            )

        assert slept == []
        assert checkpoint.active_cooldown_until("fluid_prose", "gemini", "m1", now=1500.0) == 4600.0
        abort_events = [e for e in events if e.kind is CalibrationEventKind.COOLDOWN_ABORT]
        assert abort_events == [
            CalibrationEvent(
                kind=CalibrationEventKind.COOLDOWN_ABORT,
                message=(
                    "  [COOLDOWN ABORT] fluid_prose | gemini:m1 parked for 3600s (checkpoint saved)."
                ),
                stage="fluid_prose",
                provider="gemini",
                model="m1",
                item_id="it_1",
            )
        ]

    def test_run_stage_calibration_exhausts_transient_retries_and_paces_between_items(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        checkpoint = InMemoryCalibrationCheckpointFake()
        judge = MagicMock(spec=LlmJudgePort)
        judge.evaluate.side_effect = [
            RuntimeError("503 unavailable"),
            RuntimeError("503 unavailable"),
            RuntimeError("503 unavailable"),
            RuntimeError("503 unavailable"),
        ]
        slept: list[float] = []
        with pytest.raises(RuntimeError, match="503 unavailable"):
            run_stage_calibration(
                judge=judge,
                spec=spec,
                items=[_make_item("it_1")],
                provider="gemini",
                model="m1",
                config_hash="h1",
                checkpoint_store=checkpoint,
                delay=0.0,
                jitter=0.0,
                sleep_fn=slept.append,
            )
        assert slept == [3.0, 6.0, 12.0]

        # Pacing between 2 pending items + disagreement recording
        judge_ok = MagicMock(spec=LlmJudgePort)
        judge_ok.evaluate.side_effect = [
            _make_eval(
                passed=False,
                score=0.2,
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                crit_passed=False,
                crit_score=0.2,
                crit_reasoning="Strict reject",
            ),
            _make_eval(
                passed=True,
                score=0.9,
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                crit_passed=True,
                crit_score=0.9,
            ),
        ]
        paced: list[float] = []
        res = run_stage_calibration(
            judge=judge_ok,
            spec=spec,
            items=[_make_item("a1", verdict="PASS"), _make_item("a2", verdict="PASS")],
            provider="gemini",
            model="m2",
            config_hash="h2",
            checkpoint_store=checkpoint,
            delay=2.0,
            jitter=1.0,
            sleep_fn=paced.append,
            uniform_fn=lambda _a, b: b * 0.5,
        )
        assert paced == [2.5]
        assert res.evaluated_items == 2
        assert len(res.disagreements) == 1
        assert res.disagreements[0] == {
            "id": "a1",
            "criterion": "orality_removal",
            "difficulty": "easy",
            "expected": "PASS",
            "actual_target": "FAIL",
            "actual_global": "FAIL",
            "score": 0.2,
            "anomaly": "none",
            "reasoning": "Strict reject",
        }

    def test_run_stage_calibration_checkpoint_fallbacks_defaults_and_events(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        checkpoint = InMemoryCalibrationCheckpointFake()
        # Seed two items: one without id/metadata/optional payload keys, one with distinct target fields
        checkpoint.record_item(
            stage="fluid_prose",
            provider="gemini",
            model="m_res",
            config_hash="h_res",
            item_id="item",
            payload={"actual": "FAIL", "expected": "PASS", "score": 0.3},
        )
        checkpoint.record_item(
            stage="fluid_prose",
            provider="gemini",
            model="m_res",
            config_hash="h_res",
            item_id="it_diff",
            payload={
                "actual": "PASS",
                "expected": "PASS",
                "score": 0.9,
                "reasoning": "Cached critique",
                "target_actual": "FAIL",
                "target_score": 0.4,
            },
        )

        item_no_meta: dict[str, Any] = {
            "input": {"raw_text": "r", "candidate_text": "c"},
            "expected_output": {"verdict": "PASS"},
        }
        item_with_meta: dict[str, Any] = {
            "id": "it_diff",
            "input": {"raw_text": "r", "candidate_text": "c"},
            "expected_output": {"verdict": "PASS"},
            "metadata": {
                "criterion": "orality_removal",
                "difficulty": "hard",
                "expected_anomaly": "drift",
            },
        }
        judge = MagicMock(spec=LlmJudgePort)
        events: list[CalibrationEvent] = []
        res = run_stage_calibration(
            judge=judge,
            spec=spec,
            items=[item_no_meta, item_with_meta],
            provider="gemini",
            model="m_res",
            config_hash="h_res",
            checkpoint_store=checkpoint,
            delay=1.0,
            jitter=0.0,
            on_event=events.append,
        )
        judge.evaluate.assert_not_called()
        assert res.skipped_from_checkpoint == 2
        assert res.overall.hit == 1
        assert res.overall.false_reject_beta == 1
        assert res.target_isolated.false_reject_beta == 2
        assert res.by_criterion["general"].false_reject_beta == 1
        assert res.by_difficulty["typical"].false_reject_beta == 1
        assert res.by_criterion["orality_removal"].false_reject_beta == 1
        assert res.by_difficulty["hard"].false_reject_beta == 1
        assert res.disagreements == [
            {
                "id": "item",
                "criterion": "general",
                "difficulty": "typical",
                "expected": "PASS",
                "actual_target": "FAIL",
                "actual_global": "FAIL",
                "score": 0.3,
                "anomaly": "",
                "reasoning": "",
            },
            {
                "id": "it_diff",
                "criterion": "orality_removal",
                "difficulty": "hard",
                "expected": "PASS",
                "actual_target": "FAIL",
                "actual_global": "PASS",
                "score": 0.4,
                "anomaly": "drift",
                "reasoning": "Cached critique",
            },
        ]
        # No pending items => PACING_INFO must not be emitted even when delay > 0
        assert all(e.kind is not CalibrationEventKind.PACING_INFO for e in events)

        # Pending item without explicit id gets fallback id "item_1"; delay=0 emits no PACING_INFO
        # and skipped_from_checkpoint=0 emits no CHECKPOINT_RESUMED.
        judge2 = MagicMock(spec=LlmJudgePort)
        judge2.evaluate.return_value = _make_eval(passed=True, score=0.95)
        events2: list[CalibrationEvent] = []
        slept2: list[float] = []
        run_stage_calibration(
            judge=judge2,
            spec=spec,
            items=[item_no_meta, item_no_meta],
            provider="gemini",
            model="m_noid",
            config_hash="h_noid",
            checkpoint_store=checkpoint,
            delay=0.0,
            jitter=0.0,
            sleep_fn=slept2.append,
            on_event=events2.append,
        )
        assert slept2 == []
        assert all(e.kind is not CalibrationEventKind.CHECKPOINT_RESUMED for e in events2)
        assert all(e.kind is not CalibrationEventKind.PACING_INFO for e in events2)
        item_events = [e for e in events2 if e.kind is CalibrationEventKind.ITEM_EVALUATED]
        assert [e.item_id for e in item_events] == ["item_1", "item_2"]
        saved_noid = checkpoint.load_completed_items("fluid_prose", "gemini", "m_noid", "h_noid")
        assert "item_1" in saved_noid
        assert "item_2" in saved_noid

    def test_run_stage_calibration_cooldown_boundaries_defaults_and_pacing(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        checkpoint = InMemoryCalibrationCheckpointFake()

        # Default delay=4.2, jitter=0.8, max_retry_wait=60.0
        judge_def = MagicMock(spec=LlmJudgePort)
        judge_def.evaluate.side_effect = [
            _make_eval(passed=True, score=0.9),
            _make_eval(passed=True, score=0.9),
        ]
        slept_def: list[float] = []
        uniform_calls: list[tuple[float, float]] = []
        events_def: list[CalibrationEvent] = []

        def _record_uniform_def(a: float, b: float) -> float:
            uniform_calls.append((a, b))
            return b

        run_stage_calibration(
            judge=judge_def,
            spec=spec,
            items=[_make_item("d1"), _make_item("d2")],
            provider="gemini",
            model="m_def",
            config_hash="h_def",
            checkpoint_store=checkpoint,
            sleep_fn=slept_def.append,
            uniform_fn=_record_uniform_def,
            on_event=events_def.append,
        )
        assert uniform_calls == [(0.0, 0.8)]
        assert slept_def == [pytest.approx(5.0)]
        assert any(
            e.kind is CalibrationEventKind.PACING_INFO
            and e.message == "Pacing: 4.2s base delay + up to 0.8s jitter between calls"
            for e in events_def
        )

        # Default max_retry_wait=60.0 aborts on 60.5s cooldown without sleeping
        judge_605 = MagicMock(spec=LlmJudgePort)
        judge_605.evaluate.side_effect = QuotaPoolExhaustedError("burst", retry_after_seconds=60.5)
        slept_605: list[float] = []
        with pytest.raises(QuotaPoolExhaustedError):
            run_stage_calibration(
                judge=judge_605,
                spec=spec,
                items=[_make_item("d605")],
                provider="gemini",
                model="m_605",
                config_hash="h_605",
                checkpoint_store=checkpoint,
                now_fn=lambda: 100.0,
                sleep_fn=slept_605.append,
            )
        assert slept_605 == []

        # Exact boundary retry_after == max_retry_wait (60.0) retries, sub-0.5s clamps to 0.5+0.5=1.0,
        # and 5 consecutive short cooldowns succeed on 6th call
        judge_five = MagicMock(spec=LlmJudgePort)
        judge_five.evaluate.side_effect = [
            QuotaPoolExhaustedError("b1", retry_after_seconds=60.0),
            QuotaPoolExhaustedError("b2", retry_after_seconds=0.2),
            QuotaPoolExhaustedError("b3", retry_after_seconds=1.0),
            QuotaPoolExhaustedError("b4", retry_after_seconds=1.0),
            QuotaPoolExhaustedError("b5", retry_after_seconds=1.0),
            _make_eval(passed=True, score=0.9),
        ]
        slept_five: list[float] = []
        res_five = run_stage_calibration(
            judge=judge_five,
            spec=spec,
            items=[_make_item("f1")],
            provider="gemini",
            model="m_five",
            config_hash="h_five",
            checkpoint_store=checkpoint,
            delay=0.0,
            jitter=0.0,
            max_retry_wait=60.0,
            sleep_fn=slept_five.append,
        )
        assert res_five.evaluated_items == 1
        assert slept_five == [60.5, 1.0, 1.5, 1.5, 1.5]

        # 6th consecutive short cooldown aborts after 5 waits
        judge_six = MagicMock(spec=LlmJudgePort)
        judge_six.evaluate.side_effect = [
            QuotaPoolExhaustedError(f"b{i}", retry_after_seconds=1.0) for i in range(6)
        ]
        slept_six: list[float] = []
        with pytest.raises(QuotaPoolExhaustedError):
            run_stage_calibration(
                judge=judge_six,
                spec=spec,
                items=[_make_item("s1")],
                provider="gemini",
                model="m_six",
                config_hash="h_six",
                checkpoint_store=checkpoint,
                delay=0.0,
                jitter=0.0,
                max_retry_wait=60.0,
                now_fn=lambda: 100.0,
                sleep_fn=slept_six.append,
            )
        assert len(slept_six) == 5

        # is_quota_exhausted callback prevents transient retry on 503 error
        judge_q = MagicMock(spec=LlmJudgePort)
        judge_q.evaluate.side_effect = RuntimeError("503 unavailable")
        slept_q: list[float] = []
        with pytest.raises(RuntimeError, match="503 unavailable"):
            run_stage_calibration(
                judge=judge_q,
                spec=spec,
                items=[_make_item("q1")],
                provider="gemini",
                model="m_q",
                config_hash="h_q",
                checkpoint_store=checkpoint,
                delay=0.0,
                jitter=0.0,
                is_quota_exhausted=lambda _e: True,
                sleep_fn=slept_q.append,
            )
        assert slept_q == []

        # Pacing with delay=0.2, jitter=0.3 (delay + jitter == 0.5 < 1 and delay - jitter < 0)
        judge_small = MagicMock(spec=LlmJudgePort)
        judge_small.evaluate.side_effect = [
            _make_eval(passed=True, score=0.9),
            _make_eval(passed=True, score=0.9),
        ]
        slept_small: list[float] = []
        uniform_small: list[tuple[float, float]] = []

        def _record_uniform_small(a: float, b: float) -> float:
            uniform_small.append((a, b))
            return b

        run_stage_calibration(
            judge=judge_small,
            spec=spec,
            items=[_make_item("sm1"), _make_item("sm2")],
            provider="gemini",
            model="m_sm",
            config_hash="h_sm",
            checkpoint_store=checkpoint,
            delay=0.2,
            jitter=0.3,
            sleep_fn=slept_small.append,
            uniform_fn=_record_uniform_small,
        )
        assert uniform_small == [(0.0, 0.3)]
        assert slept_small == [pytest.approx(0.5)]

    def test_application_evals_modules_have_zero_io_prints_or_layer_leaks(self) -> None:
        evals_dir = Path(__file__).resolve().parents[4] / "src" / "cresmo" / "application" / "evals"
        forbidden_modules = ("cresmo.infrastructure", "cresmo.presentation", "os")
        forbidden_calls = {"print", "read_text", "write_text", "mkdir", "replace"}

        for py_file in sorted(evals_dir.glob("*.py")):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not any(
                            alias.name == f or alias.name.startswith(f"{f}.")
                            for f in forbidden_modules
                        ), f"Forbidden import {alias.name} in {py_file.name}"
                elif isinstance(node, ast.ImportFrom) and node.module:
                    assert not any(
                        node.module == f or node.module.startswith(f"{f}.")
                        for f in forbidden_modules
                    ), f"Forbidden import {node.module} in {py_file.name}"
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        assert node.func.id not in forbidden_calls, (
                            f"Forbidden call {node.func.id}() in {py_file.name}"
                        )
                    elif isinstance(node.func, ast.Attribute):
                        assert node.func.attr not in forbidden_calls, (
                            f"Forbidden call .{node.func.attr}() in {py_file.name}"
                        )
