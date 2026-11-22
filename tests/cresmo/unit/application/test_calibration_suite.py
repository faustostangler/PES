"""Hermetic unit tests for calibration suite orchestration using in-memory fakes.

Conforms to:
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from cresmo.application.evals.calibration_metrics import CalibrationVerdict
from cresmo.application.evals.executor import CalibrationEvent, CalibrationEventKind
from cresmo.application.evals.specs import (
    CalibrationThresholds,
    build_stage_specs,
    compute_config_hash,
)
from cresmo.application.evals.suite import run_calibration_suite
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.exceptions import QuotaPoolExhaustedError
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
)
from tests.doubles.evals_fakes import (
    InMemoryCalibrationCheckpointFake,
    InMemoryCalibrationDatasetFake,
    InMemoryCalibrationReportWriterFake,
)


def _sample_items() -> list[dict[str, Any]]:
    return [
        {
            "id": "p1",
            "input": {"raw_text": "r1", "candidate_text": "c1"},
            "expected_output": {"verdict": "PASS"},
            "metadata": {"criterion": "orality_removal", "difficulty": "easy"},
        },
        {
            "id": "f1",
            "input": {"raw_text": "r2", "candidate_text": "c2"},
            "expected_output": {"verdict": "FAIL"},
            "metadata": {"criterion": "orality_removal", "difficulty": "easy"},
        },
    ]


class TestCalibrationSuite:
    """Hermetic tests verifying suite scheduling, verdicts, cooldown skip, and error isolation."""

    def test_suite_validates_dataset_path_single_stage_invariant(self, tmp_path: Path) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        with pytest.raises(
            ValueError,
            match=r"^--dataset-path can only be used with a single --stage\.$",
        ):
            run_calibration_suite(
                selected_stages=["fluid_prose", "gap_filler"],
                selected_models=[("gemini", "m1")],
                judge_factory=MagicMock(),
                stage_thresholds={"fluid_prose": 0.75, "gap_filler": 0.75},
                stage_specs=specs,
                checkpoint_store=InMemoryCalibrationCheckpointFake(),
                dataset_loader=InMemoryCalibrationDatasetFake(),
                report_writer=InMemoryCalibrationReportWriterFake(),
                dataset_path=tmp_path / "one.json",
            )

        # Single stage with dataset_path succeeds and forwards both default_golden_set_path & dataset_path
        custom_path = tmp_path / "custom.json"
        load_calls: list[tuple[str, Path, Path, Path | None, bool]] = []

        class _RecordingDatasetLoader(InMemoryCalibrationDatasetFake):
            def load_items(
                self,
                stage: str,
                default_golden_set_path: Path,
                default_seed_path: Path,
                *,
                dataset_path: Path | None = None,
                seed_only: bool = False,
            ) -> list[dict[str, Any]]:
                load_calls.append(
                    (stage, default_golden_set_path, default_seed_path, dataset_path, seed_only)
                )
                return _sample_items()

        judge = MagicMock(spec=LlmJudgePort)
        judge.evaluate.side_effect = [
            JudgeEvaluation(
                target_stage="fluid_prose",
                passed=True,
                overall_score=0.95,
                criteria_scores=(),
                provider="gemini",
            ),
            JudgeEvaluation(
                target_stage="fluid_prose",
                passed=False,
                overall_score=0.10,
                criteria_scores=(),
                provider="gemini",
            ),
        ]
        outcome = run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m1")],
            judge_factory=lambda **_: judge,
            stage_thresholds={"fluid_prose": 0.75},
            stage_specs=specs,
            checkpoint_store=InMemoryCalibrationCheckpointFake(),
            dataset_loader=_RecordingDatasetLoader(),
            report_writer=InMemoryCalibrationReportWriterFake(),
            dataset_path=custom_path,
            delay=0.0,
            jitter=0.0,
        )
        assert outcome.has_errors is False
        assert load_calls == [
            (
                "fluid_prose",
                specs["fluid_prose"].default_golden_set_path,
                specs["fluid_prose"].default_seed_path,
                custom_path,
                False,
            )
        ]

    def test_suite_handles_approved_cooldown_skip_and_error_targets(self, tmp_path: Path) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        items = [
            *_sample_items(),
            {
                "id": "p2",
                "input": {"raw_text": "r3", "candidate_text": "c3"},
                "expected_output": {"verdict": "PASS"},
                "metadata": {"criterion": "orality_removal", "difficulty": "easy"},
            },
            {
                "id": "f2",
                "input": {"raw_text": "r4", "candidate_text": "c4"},
                "expected_output": {"verdict": "FAIL"},
                "metadata": {"criterion": "orality_removal", "difficulty": "easy"},
            },
        ]

        def _prompt_lookup(_key: PromptKey) -> dict[str, str]:
            return {"system_prompt": "sys-v1", "user_prompt": "usr-v1"}

        expected_hash = compute_config_hash(
            specs["fluid_prose"],
            items,
            0.82,
            prompt_lookup=_prompt_lookup,
        )
        checkpoint = InMemoryCalibrationCheckpointFake()
        checkpoint.record_cooldown("fluid_prose", "gemini", "m_cooling", 1000.4)
        checkpoint.record_item(
            stage="fluid_prose",
            provider="gemini",
            model="m_cooling",
            config_hash=expected_hash,
            item_id="p1",
            payload={"actual": "PASS", "expected": "PASS", "score": 0.9},
        )
        datasets = InMemoryCalibrationDatasetFake(
            golden_by_stage={"fluid_prose": items},
        )
        writer = InMemoryCalibrationReportWriterFake()

        pass_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.95,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.95,
                    passed=True,
                    reasoning="ok",
                ),
            ),
            provider="gemini",
        )
        fail_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.10,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.10,
                    passed=False,
                    reasoning="bad",
                ),
            ),
            provider="gemini",
        )

        judge_ok = MagicMock(spec=LlmJudgePort)
        judge_ok.evaluate.side_effect = [pass_eval, fail_eval, pass_eval, fail_eval]
        judge_partial = MagicMock(spec=LlmJudgePort)
        judge_partial.evaluate.side_effect = [pass_eval, pass_eval, pass_eval, fail_eval]
        judge_quota = MagicMock(spec=LlmJudgePort)
        judge_quota.evaluate.side_effect = [
            pass_eval,
            QuotaPoolExhaustedError("429", retry_after_seconds=120.0),
        ]
        judge_boom = MagicMock(spec=LlmJudgePort)
        judge_boom.evaluate.side_effect = [pass_eval, RuntimeError("Crash")]

        factory_seen: list[tuple[str, str, float, bool]] = []

        def _factory(
            *, provider: str, model: str, threshold: float, enable_fallback: bool
        ) -> LlmJudgePort:
            assert enable_fallback is False
            factory_seen.append((provider, model, threshold, enable_fallback))
            if model == "m_ok":
                return judge_ok
            if model == "m_partial":
                return judge_partial
            if model == "m_quota":
                return judge_quota
            return judge_boom

        events: list[CalibrationEvent] = []
        outcome = run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[
                ("gemini", "m_cooling"),
                ("gemini", "m_ok"),
                ("gemini", "m_partial"),
                ("gemini", "m_quota"),
                ("gemini", "m_boom"),
            ],
            judge_factory=_factory,
            stage_thresholds={"fluid_prose": 0.82},
            stage_specs=specs,
            checkpoint_store=checkpoint,
            dataset_loader=datasets,
            report_writer=writer,
            verdict_thresholds=CalibrationThresholds(
                approved_min_accuracy=0.50,
                approved_max_false_accept=1,
                pre_calibrated_min_accuracy=0.40,
            ),
            reports_dir=tmp_path / "reports",
            delay=0.0,
            jitter=0.0,
            prompt_lookup=_prompt_lookup,
            report_builder=lambda spec, res, p, m: (
                f"REPORT:{spec.stage_name}:{p}:{m}:{res.accuracy:.2f}"
            ),
            now_fn=lambda: 1000.0,
            on_event=events.append,
        )

        assert outcome.has_errors is True
        assert factory_seen == [
            ("gemini", "m_ok", 0.82, False),
            ("gemini", "m_partial", 0.82, False),
            ("gemini", "m_quota", 0.82, False),
            ("gemini", "m_boom", 0.82, False),
        ]
        by_model = {s.model: s for s in outcome.summaries}

        cool = by_model["m_cooling"]
        assert cool.stage == "fluid_prose"
        assert cool.provider == "gemini"
        assert cool.status is CalibrationVerdict.COOLDOWN
        assert cool.evaluated_total == 1
        assert cool.dataset_total == 4
        assert cool.cooldown_remaining_s == pytest.approx(0.4)

        ok_sum = by_model["m_ok"]
        assert ok_sum.stage == "fluid_prose"
        assert ok_sum.provider == "gemini"
        assert ok_sum.status is CalibrationVerdict.APPROVED
        assert ok_sum.accuracy == 1.0
        assert ok_sum.d_prime > 0.0
        assert ok_sum.f1 == 1.0
        assert ok_sum.precision == 1.0
        assert ok_sum.recall == 1.0
        assert ok_sum.alpha_fpr == 0.0
        assert ok_sum.evaluated_total == 4
        assert ok_sum.dataset_total == 4

        partial = by_model["m_partial"]
        assert partial.status is CalibrationVerdict.APPROVED
        assert partial.accuracy == pytest.approx(0.75)
        assert partial.precision == pytest.approx(2 / 3)
        assert partial.recall == pytest.approx(1.0)
        assert partial.f1 == pytest.approx(0.8)
        assert partial.alpha_fpr == pytest.approx(0.5)

        quota_sum = by_model["m_quota"]
        assert quota_sum.stage == "fluid_prose"
        assert quota_sum.provider == "gemini"
        assert quota_sum.status is CalibrationVerdict.COOLDOWN
        assert quota_sum.evaluated_total == 1
        assert quota_sum.dataset_total == 4
        assert quota_sum.cooldown_remaining_s == pytest.approx(120.0)

        boom_sum = by_model["m_boom"]
        assert boom_sum.stage == "fluid_prose"
        assert boom_sum.provider == "gemini"
        assert boom_sum.status is CalibrationVerdict.ERROR
        assert boom_sum.evaluated_total == 1
        assert boom_sum.dataset_total == 4
        assert boom_sum.error_message == "Crash"

        ok_report_path = tmp_path / "reports" / "llm_judge_fluid_prose_gemini_m_ok.txt"
        assert ok_report_path in writer.written_reports
        assert writer.written_reports[ok_report_path] == "REPORT:fluid_prose:gemini:m_ok:1.00"

        skip_events = [e for e in events if e.kind is CalibrationEventKind.COOLDOWN_SKIP]
        assert skip_events == [
            CalibrationEvent(
                kind=CalibrationEventKind.COOLDOWN_SKIP,
                message="[COOLDOWN SKIP] fluid_prose | gemini:m_cooling in cooldown for 0s (1/4 checkpointed).",
                stage="fluid_prose",
                provider="gemini",
                model="m_cooling",
            )
        ]
        report_events = [e for e in events if e.kind is CalibrationEventKind.REPORT_SAVED]
        assert (
            CalibrationEvent(
                kind=CalibrationEventKind.REPORT_SAVED,
                message=f"Saved calibration report: {ok_report_path}",
                stage="fluid_prose",
                provider="gemini",
                model="m_ok",
            )
            in report_events
        )
        err_events = [e for e in events if e.kind is CalibrationEventKind.TARGET_ERROR]
        assert err_events == [
            CalibrationEvent(
                kind=CalibrationEventKind.TARGET_ERROR,
                message="[ERROR] fluid_prose | gemini:m_boom failed: Crash",
                stage="fluid_prose",
                provider="gemini",
                model="m_boom",
            )
        ]
        assert any(e.kind is CalibrationEventKind.ITEM_EVALUATED for e in events)
        assert checkpoint.load_completed_items("fluid_prose", "gemini", "m_ok", expected_hash) != {}

    def test_suite_routes_output_path_for_single_and_multi_targets(self, tmp_path: Path) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        datasets = InMemoryCalibrationDatasetFake(golden_by_stage={"fluid_prose": _sample_items()})
        pass_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.95,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.95,
                    passed=True,
                    reasoning="ok",
                ),
            ),
            provider="gemini",
        )
        fail_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.10,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.10,
                    passed=False,
                    reasoning="bad",
                ),
            ),
            provider="gemini",
        )

        def _make_factory() -> Any:
            def _factory(
                *, provider: str, model: str, threshold: float, enable_fallback: bool
            ) -> LlmJudgePort:
                _ = (provider, model, threshold, enable_fallback)
                j = MagicMock(spec=LlmJudgePort)
                j.evaluate.side_effect = [pass_eval, fail_eval]
                return j

            return _factory

        single_writer = InMemoryCalibrationReportWriterFake()
        exact_file = tmp_path / "custom_report.txt"
        run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m1")],
            judge_factory=_make_factory(),
            stage_thresholds={"fluid_prose": 0.75},
            stage_specs=specs,
            checkpoint_store=InMemoryCalibrationCheckpointFake(),
            dataset_loader=datasets,
            report_writer=single_writer,
            output_path=exact_file,
            delay=0.0,
            jitter=0.0,
            report_builder=lambda _s, _r, _p, _m: "SINGLE",
        )
        assert exact_file in single_writer.written_reports

        multi_writer = InMemoryCalibrationReportWriterFake()
        out_dir = tmp_path / "multi_reports"
        run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m1"), ("gemini", "m2")],
            judge_factory=_make_factory(),
            stage_thresholds={"fluid_prose": 0.75},
            stage_specs=specs,
            checkpoint_store=InMemoryCalibrationCheckpointFake(),
            dataset_loader=datasets,
            report_writer=multi_writer,
            output_path=out_dir,
            delay=0.0,
            jitter=0.0,
            report_builder=lambda _s, _r, _p, m: f"MULTI:{m}",
        )
        assert out_dir / "llm_judge_fluid_prose_gemini_m1.txt" in multi_writer.written_reports
        assert out_dir / "llm_judge_fluid_prose_gemini_m2.txt" in multi_writer.written_reports

    def test_suite_defaults_forwarding_and_multi_stage_events(self, tmp_path: Path) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        datasets = InMemoryCalibrationDatasetFake(
            golden_by_stage={
                "fluid_prose": _sample_items(),
                "gap_filler": _sample_items(),
            }
        )
        pass_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.95,
            criteria_scores=(),
            provider="gemini",
        )
        fail_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.10,
            criteria_scores=(),
            provider="gemini",
        )

        seen_thresholds: list[float] = []

        def _default_factory(
            *, provider: str, model: str, threshold: float, enable_fallback: bool
        ) -> LlmJudgePort:
            _ = (provider, enable_fallback)
            seen_thresholds.append(threshold)
            j = MagicMock(spec=LlmJudgePort)
            if model == "m2":
                j.evaluate.side_effect = QuotaPoolExhaustedError("burst", retry_after_seconds=60.5)
            else:
                j.evaluate.side_effect = [pass_eval, fail_eval]
            return j

        slept: list[float] = []
        events: list[CalibrationEvent] = []
        outcome = run_calibration_suite(
            selected_stages=["fluid_prose", "gap_filler"],
            selected_models=[("gemini", "m1"), ("gemini", "m2")],
            judge_factory=_default_factory,
            stage_thresholds={},
            stage_specs=specs,
            checkpoint_store=InMemoryCalibrationCheckpointFake(),
            dataset_loader=datasets,
            report_writer=InMemoryCalibrationReportWriterFake(),
            now_fn=lambda: 500.0,
            sleep_fn=slept.append,
            on_event=events.append,
        )
        assert outcome.has_errors is False
        assert seen_thresholds == [0.75, 0.75, 0.75]
        assert events[0] == CalibrationEvent(
            kind=CalibrationEventKind.SUITE_STARTED,
            message=(
                "Stages scheduled (2): fluid_prose, gap_filler | "
                "Models scheduled (2): gemini:m1, gemini:m2"
            ),
        )
        assert any(
            e.kind is CalibrationEventKind.PACING_INFO
            and e.message == "Pacing: 4.2s base delay + up to 0.8s jitter between calls"
            for e in events
        )
        # m1 paces between its 2 items in each stage (2 sleeps); m2 aborts on 60.5s > 60.0s default
        assert len(slept) == 2
        assert all(4.2 <= s <= 5.0 for s in slept)

        # Forwarding of is_quota_exhausted, max_retry_wait, delay, jitter, sleep_fn, now_fn
        checkpoint2 = InMemoryCalibrationCheckpointFake()
        judge_503 = MagicMock(spec=LlmJudgePort)
        judge_503.evaluate.side_effect = RuntimeError("503 unavailable")
        judge_short_cd = MagicMock(spec=LlmJudgePort)
        judge_short_cd.evaluate.side_effect = QuotaPoolExhaustedError(
            "burst", retry_after_seconds=10.0
        )

        slept2: list[float] = []
        events2: list[CalibrationEvent] = []
        judge_paced = MagicMock(spec=LlmJudgePort)
        judge_paced.evaluate.side_effect = [pass_eval, fail_eval]

        def _fwd_factory2(
            *, provider: str, model: str, threshold: float, enable_fallback: bool
        ) -> LlmJudgePort:
            _ = (provider, threshold, enable_fallback)
            if model == "m_503":
                return judge_503
            if model == "m_cd":
                return judge_short_cd
            return judge_paced

        outcome2 = run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m_503"), ("gemini", "m_cd"), ("gemini", "m_paced")],
            judge_factory=_fwd_factory2,
            stage_thresholds={"fluid_prose": 0.75},
            stage_specs=specs,
            checkpoint_store=checkpoint2,
            dataset_loader=datasets,
            report_writer=InMemoryCalibrationReportWriterFake(),
            delay=0.5,
            jitter=0.2,
            max_retry_wait=5.0,
            is_quota_exhausted=lambda _e: True,
            now_fn=lambda: 2000.0,
            sleep_fn=slept2.append,
            on_event=events2.append,
        )
        assert len(slept2) == 1
        assert 0.5 <= slept2[0] <= 0.7
        assert any(
            e.kind is CalibrationEventKind.PACING_INFO
            and e.message == "Pacing: 0.5s base delay + up to 0.2s jitter between calls"
            for e in events2
        )
        assert outcome2.has_errors is True
        assert checkpoint2.active_cooldown_until("fluid_prose", "gemini", "m_cd", now=2000.0) == (
            2010.0
        )
