"""Unit tests for Unified Zero-Fallback Judge Calibration Harness (scripts/calibrate_judges.py).

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI with Cooldown-Aware Checkpointing
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle
    - ADR-060: Gap Filler Judge Criteria v2
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cresmo.application.evals import (
    STAGE_SPECS,
    CalibrationCheckpointStore,
    ConfusionMatrix,
    evaluate_single_item,
    parse_model_specs,
    parse_stage_specs,
    run_calibration_suite,
    run_stage_calibration,
)
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.llm.gemini_pool import CredentialPoolExhaustedError


def test_stage_specs_cover_all_stages_with_canonical_criteria() -> None:
    assert set(STAGE_SPECS.keys()) == {"fluid_prose", "gap_filler"}
    assert len(STAGE_SPECS["fluid_prose"].required_criteria) == 6
    assert len(STAGE_SPECS["gap_filler"].required_criteria) == 7
    assert (
        JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION
        in STAGE_SPECS["gap_filler"].required_criteria
    )


def test_confusion_matrix_sdt_metrics() -> None:
    perfect = ConfusionMatrix(hit=10, pedantismo_beta=0, permissivo_alfa=0, rejeicao=10)
    assert perfect.total_valid == 20
    assert perfect.accuracy == 1.0
    assert perfect.precision == 1.0
    assert perfect.recall == 1.0
    assert perfect.f1 == 1.0

    empty = ConfusionMatrix()
    assert empty.total_valid == 0
    assert empty.accuracy == 0.0
    assert empty.precision == 0.0
    assert empty.recall == 0.0
    assert empty.f1 == 0.0

    mixed = ConfusionMatrix(hit=8, pedantismo_beta=2, permissivo_alfa=2, rejeicao=8)
    assert mixed.accuracy == pytest.approx(0.80)
    assert mixed.precision == pytest.approx(0.80)
    assert mixed.recall == pytest.approx(0.80)
    assert mixed.f1 == pytest.approx(0.80)


@pytest.mark.parametrize(
    ("stage_name", "criterion", "raw_text", "cand_text"),
    [
        (
            "fluid_prose",
            JudgeCriterion.ORALITY_REMOVAL,
            "Transcrição original",
            "## Texto Válido\n\nCorpo em prosa.",
        ),
        (
            "gap_filler",
            JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
            "Transcrição fluida original",
            "## Texto Expandido\n\nCorpo em prosa com detalhes.\n\n### Extra Info\n\n1. Dado.",
        ),
    ],
)
def test_evaluate_single_item_uniform_for_all_stages(
    stage_name: str,
    criterion: JudgeCriterion,
    raw_text: str,
    cand_text: str,
) -> None:
    mock_judge = MagicMock(spec=LlmJudgePort)
    mock_judge.evaluate.return_value = JudgeEvaluation(
        target_stage=stage_name,
        passed=True,
        overall_score=0.95,
        criteria_scores=(
            CriterionScore(
                criterion=criterion,
                score=0.95,
                passed=True,
                reasoning="Verified",
            ),
        ),
        provider="gemini",
    )

    item = {
        "id": "item_01",
        "input": {"raw_text": raw_text, "candidate_text": cand_text},
        "expected_output": {"verdict": "PASS"},
        "metadata": {"criterion": criterion.value},
    }

    res = evaluate_single_item(mock_judge, STAGE_SPECS[stage_name], item)
    actual, expected, score, reasoning = res

    assert actual == "PASS"
    assert expected == "PASS"
    assert score == 0.95
    assert res.target_actual == "PASS"
    assert res.target_score == 0.95
    assert reasoning == "Verified"
    ctx = mock_judge.evaluate.call_args.args[0]
    assert ctx.stage_name == stage_name
    assert ctx.required_criteria == STAGE_SPECS[stage_name].required_criteria


def test_checkpoint_resumes_from_previous_point_and_respects_cooldown(tmp_path: Path) -> None:
    store = CalibrationCheckpointStore(checkpoint_dir=tmp_path)
    items = [
        {
            "id": "item_1",
            "input": {"raw_text": "raw1", "candidate_text": "cand1"},
            "expected_output": {"verdict": "PASS"},
            "metadata": {"criterion": "orality_removal", "difficulty": "easy"},
        },
        {
            "id": "item_2",
            "input": {"raw_text": "raw2", "candidate_text": "cand2"},
            "expected_output": {"verdict": "FAIL"},
            "metadata": {"criterion": "orality_removal", "difficulty": "easy"},
        },
    ]

    ok_eval = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=True,
        overall_score=0.95,
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                score=0.95,
                passed=True,
                reasoning="Clean",
            ),
        ),
        provider="gemini",
    )
    reject_eval = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.10,
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.ORALITY_REMOVAL,
                score=0.10,
                passed=False,
                reasoning="Orality found",
            ),
        ),
        provider="gemini",
    )

    mock_judge = MagicMock(spec=LlmJudgePort)
    mock_judge.evaluate.side_effect = [
        ok_eval,
        CredentialPoolExhaustedError(
            retry_after_seconds=3600.0,
            message="All Gemini credentials in cooldown.",
        ),
    ]

    clock = {"now": 1000.0}

    with pytest.raises(CredentialPoolExhaustedError):
        run_stage_calibration(
            judge=mock_judge,
            spec=STAGE_SPECS["fluid_prose"],
            items=items,
            provider="gemini",
            model="gemini-4-hydrogen",
            config_hash="hash-v1",
            checkpoint_store=store,
            delay=0.0,
            jitter=0.0,
            max_retry_wait=60.0,
            now_fn=lambda: clock["now"],
        )

    assert mock_judge.evaluate.call_count == 2
    assert store.active_cooldown_until(
        "fluid_prose", "gemini", "gemini-4-hydrogen", now=1500.0
    ) == pytest.approx(4600.0)
    # Shared across stage for same (provider, model)
    assert store.active_cooldown_until(
        "gap_filler", "gemini", "gemini-4-hydrogen", now=1500.0
    ) == pytest.approx(4600.0)

    # Restart BEFORE cooldown expires -> must skip immediately with 0 LLM calls
    mock_judge.evaluate.reset_mock()
    assert (
        store.active_cooldown_until("fluid_prose", "gemini", "gemini-4-hydrogen", now=2000.0)
        is not None
    )

    # Advance clock past cooldown expiry -> resumes strictly from item_2 with item_1 replayed from JSON
    clock["now"] = 4605.0
    mock_judge.evaluate.side_effect = [reject_eval]

    results = run_stage_calibration(
        judge=mock_judge,
        spec=STAGE_SPECS["fluid_prose"],
        items=items,
        provider="gemini",
        model="gemini-4-hydrogen",
        config_hash="hash-v1",
        checkpoint_store=store,
        delay=0.0,
        jitter=0.0,
        max_retry_wait=60.0,
        now_fn=lambda: clock["now"],
    )

    assert mock_judge.evaluate.call_count == 1  # ONLY item_2 was called!
    assert results.target_isolated.hit == 1
    assert results.target_isolated.rejeicao == 1
    assert results.target_isolated.accuracy == 1.0


def test_short_cooldown_waits_and_retries_without_abort(tmp_path: Path) -> None:
    store = CalibrationCheckpointStore(checkpoint_dir=tmp_path)
    items = [
        {
            "id": "eg_01",
            "input": {"raw_text": "raw1", "candidate_text": "cand1"},
            "expected_output": {"verdict": "PASS"},
            "metadata": {"criterion": "epistemic_grounding_segregation", "difficulty": "easy"},
        },
    ]

    mock_judge = MagicMock(spec=LlmJudgePort)
    mock_judge.evaluate.side_effect = [
        CredentialPoolExhaustedError(retry_after_seconds=2.0, message="Short RPM window"),
        JudgeEvaluation(
            target_stage="gap_filler",
            passed=True,
            overall_score=0.92,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
                    score=0.92,
                    passed=True,
                    reasoning="Verified",
                ),
            ),
            provider="gemini",
        ),
    ]

    slept: list[float] = []
    results = run_stage_calibration(
        judge=mock_judge,
        spec=STAGE_SPECS["gap_filler"],
        items=items,
        provider="gemini",
        model="gemini-4-hydrogen",
        config_hash="hash-gf",
        checkpoint_store=store,
        delay=0.0,
        jitter=0.0,
        max_retry_wait=10.0,
        sleep_fn=slept.append,
    )

    assert mock_judge.evaluate.call_count == 2
    assert slept and slept[0] >= 2.0
    assert results.target_isolated.hit == 1


def test_checkpoint_invalidates_items_when_config_hash_changes(tmp_path: Path) -> None:
    store = CalibrationCheckpointStore(checkpoint_dir=tmp_path)
    store.record_item(
        stage="gap_filler",
        provider="gemini",
        model="gemini-4-hydrogen",
        config_hash="old-hash",
        item_id="eg_01",
        payload={
            "actual": "PASS",
            "expected": "PASS",
            "score": 0.9,
            "reasoning": "old",
            "target_actual": "PASS",
            "target_score": 0.9,
        },
    )

    loaded = store.load_completed_items(
        stage="gap_filler",
        provider="gemini",
        model="gemini-4-hydrogen",
        config_hash="new-hash",
    )
    assert loaded == {}


def test_cli_always_disables_fallback_and_runs_all_stages_by_default(tmp_path: Path) -> None:
    passed_eval_fp = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=True,
        overall_score=0.95,
        criteria_scores=tuple(
            CriterionScore(criterion=c, score=0.95, passed=True, reasoning="ok")
            for c in STAGE_SPECS["fluid_prose"].required_criteria
        ),
        provider="gemini",
    )
    failed_eval_fp = JudgeEvaluation(
        target_stage="fluid_prose",
        passed=False,
        overall_score=0.10,
        criteria_scores=tuple(
            CriterionScore(criterion=c, score=0.10, passed=False, reasoning="fail")
            for c in STAGE_SPECS["fluid_prose"].required_criteria
        ),
        provider="gemini",
    )
    passed_eval_gf = JudgeEvaluation(
        target_stage="gap_filler",
        passed=True,
        overall_score=0.95,
        criteria_scores=tuple(
            CriterionScore(criterion=c, score=0.95, passed=True, reasoning="ok")
            for c in STAGE_SPECS["gap_filler"].required_criteria
        ),
        provider="gemini",
    )
    failed_eval_gf = JudgeEvaluation(
        target_stage="gap_filler",
        passed=False,
        overall_score=0.10,
        criteria_scores=tuple(
            CriterionScore(criterion=c, score=0.10, passed=False, reasoning="fail")
            for c in STAGE_SPECS["gap_filler"].required_criteria
        ),
        provider="gemini",
    )

    mock_judge = MagicMock(spec=LlmJudgePort)
    # seed items: 5 for fluid_prose (P, F, F, P, F), 2 for gap_filler (P, F)
    mock_judge.evaluate.side_effect = [
        passed_eval_fp,
        failed_eval_fp,
        failed_eval_fp,
        passed_eval_fp,
        failed_eval_fp,
        passed_eval_gf,
        failed_eval_gf,
    ]

    factory_calls: list[dict[str, object]] = []

    def _fake_factory(
        *,
        provider: str,
        model: str,
        threshold: float,
        enable_fallback: bool,
    ) -> LlmJudgePort:
        factory_calls.append(
            {
                "provider": provider,
                "model": model,
                "threshold": threshold,
                "enable_fallback": enable_fallback,
            }
        )
        return mock_judge

    outcome = run_calibration_suite(
        selected_stages=parse_stage_specs(None, None),
        selected_models=parse_model_specs(["gemini:gemini-4-hydrogen"], None, "gemini"),
        judge_factory=_fake_factory,
        stage_thresholds={"fluid_prose": 0.75, "gap_filler": 0.75},
        seed_only=True,
        checkpoint_dir=tmp_path / "checkpoints",
        reports_dir=tmp_path / "reports",
        delay=0.0,
        jitter=0.0,
    )

    assert not outcome.has_errors
    assert len(factory_calls) == 2  # both fluid_prose and gap_filler ran by default
    for call in factory_calls:
        assert call["enable_fallback"] is False


def test_parse_helpers_handle_comma_and_repeated_flags() -> None:
    assert parse_stage_specs(None, None) == ["fluid_prose", "gap_filler"]
    assert parse_stage_specs(["fluid_prose,gap_filler"], None) == ["fluid_prose", "gap_filler"]
    assert parse_stage_specs(None, "gap_filler") == ["gap_filler"]
    assert parse_model_specs(["gemini:a,gemini:b", "ollama:c"], None, "gemini") == [
        ("gemini", "a"),
        ("gemini", "b"),
        ("ollama", "c"),
    ]
