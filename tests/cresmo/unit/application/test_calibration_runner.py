"""Comprehensive unit tests for stage-agnostic calibration runner, checkpoints, and reports."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    ConfusionMatrix,
    ItemEvaluationResult,
    ModelBenchmarkSummary,
)
from cresmo.application.evals.calibration_runner import (
    FLUID_PROSE_SEED_DATA,
    GAP_FILLER_SEED_DATA,
    CalibrationCheckpointStore,
    CooldownActiveError,
    _extract_cooldown_seconds,
    _format_matrix_2x2,
    _is_transient_retryable_error,
    _record_item_into_results,
    build_stage_specs,
    compute_config_hash,
    evaluate_single_item,
    generate_calibration_report,
    load_stage_dataset,
    parse_model_specs,
    parse_stage_specs,
    print_benchmark_summary,
    resolve_model_spec,
    run_calibration_suite,
    run_stage_calibration,
    sanitize_report_filename,
    save_calibration_report,
)
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.exceptions import RateLimitExceededError
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
)


def _make_item(
    item_id: str = "it_1",
    *,
    raw_text: str = "raw",
    candidate_text: str = "cand",
    verdict: str = "PASS",
    criterion: str = "orality_removal",
    difficulty: str = "easy",
    anomaly: str = "",
) -> dict[str, Any]:
    return {
        "id": item_id,
        "input": {"raw_text": raw_text, "candidate_text": candidate_text},
        "expected_output": {"verdict": verdict},
        "metadata": {
            "criterion": criterion,
            "difficulty": difficulty,
            "expected_anomaly": anomaly,
        },
    }


def _make_eval(
    *,
    stage: str = "fluid_prose",
    passed: bool = True,
    score: float = 0.9,
    criteria_scores: tuple[CriterionScore, ...] = (),
    provider: str = "gemini",
) -> JudgeEvaluation:
    return JudgeEvaluation(
        target_stage=stage,
        passed=passed,
        overall_score=score,
        criteria_scores=criteria_scores,
        provider=provider,
    )


def _make_rate_limit(msg: str, retry_after: float | None = None) -> RateLimitExceededError:
    err = RateLimitExceededError(msg)
    if retry_after is not None:
        err.retry_after_seconds = retry_after
    return err


class TestSpecAndCliParsingHelpers:
    """Tests for stage spec construction, model/stage CLI parsers, and hash/dataset helpers."""

    def test_cooldown_active_error_clamps_negative_seconds(self) -> None:
        err = CooldownActiveError(-5.0, "Cooldown msg")
        assert err.retry_after_seconds == 0.0
        assert str(err) == "Cooldown msg"

        pos = CooldownActiveError(12.5, "Wait 12s")
        assert pos.retry_after_seconds == 12.5

    def test_build_stage_specs_constructs_both_canonical_stages(self, tmp_path: Path) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        assert list(specs.keys()) == ["fluid_prose", "gap_filler"]

        fp = specs["fluid_prose"]
        assert fp.stage_name == "fluid_prose"
        assert fp.label == "Stage 1: Fluid Prose"
        assert fp.prompt_key == PromptKey.JUDGE_FLUID_PROSE
        assert fp.default_golden_set_path == tmp_path / "fluid_prose_golden_set.json"
        assert fp.required_criteria == (
            JudgeCriterion.ORALITY_REMOVAL,
            JudgeCriterion.SEMANTIC_FAITHFULNESS,
            JudgeCriterion.EPISTEMIC_CRITIQUE,
            JudgeCriterion.NER_PRESERVATION,
            JudgeCriterion.STRUCTURAL_COMPLIANCE,
            JudgeCriterion.AUTHORIAL_VOICE,
        )
        assert fp.seed_items == FLUID_PROSE_SEED_DATA

        gf = specs["gap_filler"]
        assert gf.stage_name == "gap_filler"
        assert gf.label == "Stage 2: Gap Filler"
        assert gf.prompt_key == PromptKey.JUDGE_GAP_FILLER
        assert gf.default_golden_set_path == tmp_path / "gap_filler_golden_set.json"
        assert gf.required_criteria == (
            JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
            JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION,
            JudgeCriterion.BRAUDELIAN_STRATIFICATION,
            JudgeCriterion.GENEALOGY_HIDDEN_AGENCY,
            JudgeCriterion.COMPETING_HYPOTHESES,
            JudgeCriterion.EXTRA_INFO_GRANULARITY,
            JudgeCriterion.LINEAR_STYLE_NATURALISM,
        )
        assert gf.seed_items == GAP_FILLER_SEED_DATA

    def test_resolve_model_spec_handles_explicit_prefixes_and_heuristics(self) -> None:
        assert resolve_model_spec("  Ollama : llama3:8b ") == ("ollama", "llama3:8b")
        assert resolve_model_spec("gemini-4-hydrogen") == ("gemini", "gemini-4-hydrogen")
        assert resolve_model_spec("GEMINI-pro", default_provider="ollama") == (
            "gemini",
            "GEMINI-pro",
        )
        assert resolve_model_spec("ollama-qwen", default_provider="gemini") == (
            "ollama",
            "ollama-qwen",
        )
        assert resolve_model_spec("typesafe-jev", default_provider="gemini") == (
            "typesafe",
            "typesafe-jev",
        )
        assert resolve_model_spec("custom-only") == ("gemini", "custom-only")
        assert resolve_model_spec("custom-model", default_provider=" OpenRouter ") == (
            "openrouter",
            "custom-model",
        )

    def test_parse_stage_specs_supports_hyphens_all_dedup_and_errors(self, tmp_path: Path) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        assert parse_stage_specs([], None, stage_specs=specs) == ["fluid_prose", "gap_filler"]
        assert parse_stage_specs(["fluid_prose", "ALL"], None, stage_specs=specs) == [
            "fluid_prose",
            "gap_filler",
        ]
        assert parse_stage_specs(
            [" fluid-prose , gap-filler ", "fluid_prose"], None, stage_specs=specs
        ) == ["fluid_prose", "gap_filler"]
        assert parse_stage_specs(None, "fluid-prose, gap_filler", stage_specs=specs) == [
            "fluid_prose",
            "gap_filler",
        ]

        with pytest.raises(
            ValueError,
            match=r"^Unknown stage 'bad-stage'\. Valid stages: fluid_prose, gap_filler, all\.$",
        ):
            parse_stage_specs(["bad-stage"], None, stage_specs=specs)

    def test_parse_model_specs_handles_single_default_and_dedup(self) -> None:
        assert parse_model_specs(None, "solo-model") == [("gemini", "solo-model")]
        assert parse_model_specs(
            ["gemini:m1, gemini:m1", " ,ollama:qwen "], None, default_provider="gemini"
        ) == [("gemini", "m1"), ("ollama", "qwen")]
        assert parse_model_specs(None, " ollama:qwen ", default_provider="gemini") == [
            ("ollama", "qwen")
        ]
        assert parse_model_specs(
            None,
            "   ",
            default_provider="Ollama",
            default_models=("model-a", "gemini-b", "model-a"),
        ) == [("ollama", "model-a"), ("gemini", "gemini-b")]

    def test_sanitize_report_filename_normalizes_separators(self) -> None:
        assert (
            sanitize_report_filename("gap_filler", "ollama", "ollama:QwenZ/3:8b@Local")
            == "llm_judge_gap_filler_ollama_QwenZ_3_8b_Local.txt"
        )
        assert (
            sanitize_report_filename("fluid_prose", "gemini", "gemini-4.0_flash")
            == "llm_judge_fluid_prose_gemini_gemini-4.0_flash.txt"
        )

    def test_compute_config_hash_is_deterministic_and_handles_lookup_errors(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        fp_spec = specs["fluid_prose"]
        items = [_make_item("i1", raw_text="Ação", candidate_text="Coração")]

        prompt_payload = {"system_prompt": "s-ação", "user_prompt": "u"}
        seen_keys: list[PromptKey] = []

        def _ok_lookup(key: PromptKey) -> dict[str, str]:
            seen_keys.append(key)
            return dict(prompt_payload)

        h1 = compute_config_hash(fp_spec, items, 0.7500001, prompt_lookup=_ok_lookup)
        assert seen_keys == [PromptKey.JUDGE_FLUID_PROSE]
        h2 = compute_config_hash(
            fp_spec,
            items,
            0.7500002,
            prompt_lookup=lambda _key: {"user_prompt": "u", "system_prompt": "s-ação"},
        )
        assert h1 == h2
        expected_canonical = {
            "stage": "fluid_prose",
            "threshold": 0.75,
            "required_criteria": [c.value for c in fp_spec.required_criteria],
            "prompt": prompt_payload,
            "items": items,
        }
        expected_h1 = hashlib.sha256(
            json.dumps(expected_canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        assert h1 == expected_h1

        h_diff_thresh = compute_config_hash(
            fp_spec,
            items,
            0.80,
            prompt_lookup=lambda _key: prompt_payload,
        )
        assert h_diff_thresh != h1

        def _failing_lookup(_key: PromptKey) -> dict[str, str]:
            raise RuntimeError("prompt boom")

        caplog.clear()
        with caplog.at_level(logging.DEBUG, logger="cresmo.application.evals.calibration_runner"):
            h_fallback = compute_config_hash(fp_spec, items, 0.75, prompt_lookup=_failing_lookup)
            h_none = compute_config_hash(fp_spec, items, 0.75, prompt_lookup=None)

        assert h_fallback == h_none
        default_canonical = {
            **expected_canonical,
            "prompt": {"system_prompt": "", "user_prompt": ""},
        }
        expected_default = hashlib.sha256(
            json.dumps(default_canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        assert h_none == expected_default
        assert any(
            r.name == "cresmo.application.evals.calibration_runner"
            and r.getMessage() == "Prompt lookup unavailable for config hash: prompt boom"
            for r in caplog.records
        )

    def test_load_stage_dataset_handles_seed_file_empty_and_missing(self, tmp_path: Path) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        seed_loaded = load_stage_dataset(
            spec, dataset_path=tmp_path / "custom.json", seed_only=True
        )
        assert len(seed_loaded) == len(spec.seed_items)
        assert seed_loaded[0] == spec.seed_items[0]

        missing_loaded = load_stage_dataset(spec, dataset_path=None, seed_only=False)
        assert len(missing_loaded) == len(spec.seed_items)

        empty_path = tmp_path / "empty.json"
        empty_path.write_text("[]", encoding="utf-8")
        assert len(load_stage_dataset(spec, dataset_path=empty_path, seed_only=False)) == len(
            spec.seed_items
        )

        dict_path = tmp_path / "dict.json"
        dict_path.write_text('{"bad": 1}', encoding="utf-8")
        assert len(load_stage_dataset(spec, dataset_path=dict_path, seed_only=False)) == len(
            spec.seed_items
        )

        valid_path = tmp_path / "valid.json"
        custom_items = [_make_item("custom_1")]
        valid_path.write_text(json.dumps(custom_items), encoding="utf-8")
        assert load_stage_dataset(spec, dataset_path=valid_path, seed_only=False) == custom_items


class TestCheckpointStoreAndRetryClassification:
    """Tests for atomic JSON checkpoints, cooldown persistence, and retry predicates."""

    def test_checkpoint_store_read_write_corruption_and_cooldown_lifecycle(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cp_dir = tmp_path / "nested" / "cp"
        store = CalibrationCheckpointStore(checkpoint_dir=cp_dir)
        # First atomic write on deeply uncreated directory proves parents=True & exist_ok=True
        store._write_json_atomic(cp_dir / "init.json", {"ok": True})
        store._write_json_atomic(cp_dir / "init.json", {"ok": True})
        assert store._slug("  Model_AZ-9.1/x ") == "Model_AZ-9.1_x"
        assert store._shared_key("  GeMiNi ", " M/1 ") == "gemini:M/1"
        target_path = store._target_path("fluid_prose", "gemini", "gemini:m/1")
        assert target_path.name == "fluid_prose__gemini__gemini_m_1.json"

        # Non-existent -> empty dict
        assert store._read_json(target_path) == {}

        # Invalid JSON and non-dict JSON -> empty dict
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text("{corrupt", encoding="utf-8")
        assert store._read_json(target_path) == {}
        target_path.write_text("[1, 2]", encoding="utf-8")
        assert store._read_json(target_path) == {}

        # Atomic JSON preserves non-ASCII characters and indent=2, using .json.tmp
        seen_tmp_suffixes: list[str] = []
        orig_replace = os.replace

        def _spied_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
            seen_tmp_suffixes.append(Path(src).name)
            orig_replace(src, dst)

        monkeypatch.setattr("os.replace", _spied_replace)
        unicode_file = cp_dir / "unicode.json"
        store._write_json_atomic(unicode_file, {"texto": "Ação e Coração"})
        assert seen_tmp_suffixes[-1] == "unicode.json.tmp"
        assert unicode_file.read_bytes().decode("utf-8") == '{\n  "texto": "Ação e Coração"\n}'
        monkeypatch.undo()

        # Record cooldown writes target metadata and shared cooldowns using max(prev, new)
        store.record_cooldown("fluid_prose", "gemini", "m1", 2000.0)
        m1_path = store._target_path("fluid_prose", "gemini", "m1")
        raw_cd = json.loads(m1_path.read_text(encoding="utf-8"))
        assert raw_cd == {
            "stage": "fluid_prose",
            "provider": "gemini",
            "model": "m1",
            "cooldown_until": 2000.0,
        }
        assert json.loads(store._cooldowns_path.read_text(encoding="utf-8")) == {
            "gemini:m1": 2000.0
        }
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1", now=1999.0) == 2000.0
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1", now=2000.0) is None
        assert store.active_cooldown_until("gap_filler", "gemini", "m1", now=1500.0) == 2000.0

        # Lower timestamp does not overwrite higher existing cooldown in either file
        store.record_cooldown("fluid_prose", "gemini", "m1", 1500.0)
        assert json.loads(m1_path.read_text(encoding="utf-8"))["cooldown_until"] == 2000.0
        assert json.loads(store._cooldowns_path.read_text(encoding="utf-8"))["gemini:m1"] == 2000.0
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1", now=1000.0) == 2000.0

        # Higher timestamp updates both target and shared cooldowns
        store.record_cooldown("fluid_prose", "gemini", "m1", 3000.0)
        assert json.loads(m1_path.read_text(encoding="utf-8"))["cooldown_until"] == 3000.0
        assert json.loads(store._cooldowns_path.read_text(encoding="utf-8"))["gemini:m1"] == 3000.0

        # Target-only cooldown strictly exceeding shared cooldown is respected
        raw_target_high = json.loads(m1_path.read_text(encoding="utf-8"))
        raw_target_high["cooldown_until"] = 3500.0
        store._write_json_atomic(m1_path, raw_target_high)
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1", now=1000.0) == 3500.0
        raw_target_high["cooldown_until"] = 3000.0
        store._write_json_atomic(m1_path, raw_target_high)

        # Record multiple items preserving existing items on matching config_hash + resetting on mismatch
        store.record_item("fluid_prose", "gemini", "m1", "h1", "i1", {"actual": "PASS"})
        store.record_item("fluid_prose", "gemini", "m1", "h1", "i2", {"actual": "FAIL"})
        raw_saved = json.loads(m1_path.read_text(encoding="utf-8"))
        assert raw_saved["stage"] == "fluid_prose"
        assert raw_saved["provider"] == "gemini"
        assert raw_saved["model"] == "m1"
        assert raw_saved["config_hash"] == "h1"
        assert raw_saved["cooldown_until"] == 3000.0
        assert raw_saved["updated_at"].endswith("+00:00")
        assert raw_saved["items"] == {"i1": {"actual": "PASS"}, "i2": {"actual": "FAIL"}}

        # Corrupt items dict / non-dict item entries handled safely
        raw_saved["items"]["bad_entry"] = "not-a-dict"
        store._write_json_atomic(m1_path, raw_saved)
        assert store.load_completed_items("fluid_prose", "gemini", "m1", "h1") == {
            "i1": {"actual": "PASS"},
            "i2": {"actual": "FAIL"},
        }

        # Config hash mismatch resets previous items in checkpoint file on next record_item
        store.record_item("fluid_prose", "gemini", "m1", "h_new", "i3", {"actual": "PASS"})
        raw_reset = json.loads(m1_path.read_text(encoding="utf-8"))
        assert raw_reset["items"] == {"i3": {"actual": "PASS"}}
        assert store.load_completed_items("fluid_prose", "gemini", "m1", "h1") == {}

        # Default now uses time.time()
        monkeypatch.setattr("cresmo.application.evals.calibration_runner.time.time", lambda: 2999.0)
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1") == 3000.0

        # Preserve another model in shared cooldowns while clearing m1
        store.record_cooldown("gap_filler", "gemini", "other", 4000.0)
        store.clear_cooldown("fluid_prose", "gemini", "m1")
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1", now=1000.0) is None
        after_clear_target = json.loads(m1_path.read_text(encoding="utf-8"))
        assert "cooldown_until" not in after_clear_target
        assert after_clear_target["items"] == {"i3": {"actual": "PASS"}}
        assert json.loads(store._cooldowns_path.read_text(encoding="utf-8")) == {
            "gemini:other": 4000.0
        }
        # Calling clear again when already cleared is a safe no-op without KeyError
        store.clear_cooldown("fluid_prose", "gemini", "m1")

        # Write failure cleans up temp file and re-raises
        err_path = cp_dir / "fail.json"
        monkeypatch.setattr("os.replace", MagicMock(side_effect=OSError("disk full")))
        with pytest.raises(OSError, match="disk full"):
            store._write_json_atomic(err_path, {"ok": 1})
        assert not (cp_dir / "fail.tmp").exists()

    def test_extract_cooldown_and_transient_retry_classification(self) -> None:
        assert _extract_cooldown_seconds(ValueError("x")) is None
        assert _extract_cooldown_seconds(_make_rate_limit("rl", -2.0)) == 0.0
        assert _extract_cooldown_seconds(_make_rate_limit("rl", 9.5)) == 9.5

        rl_no_attr = RateLimitExceededError("rl")
        assert _extract_cooldown_seconds(rl_no_attr) is None

        assert _is_transient_retryable_error(RateLimitExceededError("503")) is False
        sentinel_exc = RuntimeError("503")
        assert (
            _is_transient_retryable_error(
                sentinel_exc, is_quota_exhausted=lambda e: e is sentinel_exc
            )
            is False
        )
        # Mixed quota + transient keywords MUST classify as non-transient quota exhaustion
        for q_msg in (
            "RESOURCE_EXHAUSTED 503",
            "HTTP 429 timeout",
            "Quota Exceeded 504",
            "Too many requests service unavailable",
        ):
            assert _is_transient_retryable_error(RuntimeError(q_msg)) is False
        for t_msg in (
            "HTTP 503",
            "Error 504",
            "Service UNAVAILABLE",
            "Request Timeout",
            "Connection Reset by peer",
            "operation timed out",
        ):
            assert _is_transient_retryable_error(RuntimeError(t_msg)) is True
        assert _is_transient_retryable_error(ValueError("bad schema payload")) is False


class TestItemEvaluationAndResultRecording:
    """Tests for evaluate_single_item and _record_item_into_results."""

    def test_evaluate_single_item_extracts_target_criterion_and_handles_missing_criterion(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.return_value = _make_eval(
            passed=True,
            score=0.90,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.40,
                    passed=False,
                    reasoning="Orality defect details",
                ),
            ),
        )

        item = _make_item(
            "i_crit",
            raw_text="raw input A",
            candidate_text="cand output A",
            verdict=" pass ",
            criterion="orality_removal",
        )
        res = evaluate_single_item(mock_judge, spec, item)
        eval_ctx = mock_judge.evaluate.call_args.args[0]
        assert eval_ctx.raw_text == "raw input A"
        assert eval_ctx.candidate_text == "cand output A"
        assert eval_ctx.stage_name == "fluid_prose"
        assert eval_ctx.required_criteria == spec.required_criteria
        assert res.actual == "PASS"
        assert res.expected == "PASS"
        assert res.score == 0.90
        assert res.target_actual == "FAIL"
        assert res.target_score == 0.40
        assert res.reasoning == "Orality defect details"

        # Item without metadata dict falls back safely to empty criterion -> global
        no_meta_item = {
            "id": "no_meta",
            "input": {"raw_text": "raw_nm", "candidate_text": "cand_nm"},
            "expected_output": {"verdict": "PASS"},
        }
        mock_judge.evaluate.return_value = _make_eval(passed=True, score=0.88, criteria_scores=())
        res_nm = evaluate_single_item(mock_judge, spec, no_meta_item)
        assert res_nm.target_actual == "PASS"
        assert res_nm.target_score == 0.88

        # Invalid criterion string falls back cleanly to global
        bad_crit_item = _make_item("i_bad", verdict="FAIL", criterion="nonexistent_crit")
        mock_judge.evaluate.return_value = _make_eval(
            passed=False,
            score=0.25,
            criteria_scores=(),
        )
        res_bad = evaluate_single_item(mock_judge, spec, bad_crit_item)
        assert res_bad.actual == "FAIL"
        assert res_bad.target_actual == "FAIL"
        assert res_bad.target_score == 0.25
        assert res_bad.reasoning == "Quality threshold not met."

        # Valid criterion present, but reasoning empty -> retains global critique; missing score -> keeps global
        valid_no_reason = _make_eval(
            passed=False,
            score=0.30,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.80,
                    passed=True,
                    reasoning="",
                ),
            ),
        )
        mock_judge.evaluate.return_value = valid_no_reason
        res_empty_r = evaluate_single_item(mock_judge, spec, item)
        assert res_empty_r.target_actual == "PASS"
        assert res_empty_r.target_score == 0.80
        assert res_empty_r.reasoning == "Quality threshold not met."

    def test_record_item_into_results_populates_slices_and_disagreements(self) -> None:
        results = CalibrationResultSet()
        item_ok = {"input": {}, "expected_output": {"verdict": "PASS"}}
        status_ok = _record_item_into_results(
            results,
            item_ok,
            ItemEvaluationResult(
                actual="PASS",
                expected="PASS",
                score=0.95,
                reasoning="ok",
                target_actual="PASS",
                target_score=0.95,
            ),
        )
        assert status_ok == "HIT"
        assert results.overall.hit == 1
        assert results.target_isolated.hit == 1
        assert results.by_criterion["general"].hit == 1
        assert results.by_difficulty["typical"].hit == 1
        assert results.disagreements == []

        item_bad = _make_item(
            "bad_1",
            verdict="FAIL",
            criterion="ner_preservation",
            difficulty="hard",
            anomaly="missing entity",
        )
        status_bad = _record_item_into_results(
            results,
            item_bad,
            ItemEvaluationResult(
                actual="PASS",
                expected="FAIL",
                score=0.72,
                reasoning="missed anomaly",
                target_actual="PASS",
                target_score=0.65,
            ),
        )
        assert status_bad == "PERMISSIVO_ALFA"
        assert len(results.disagreements) == 1
        assert results.disagreements[0] == {
            "id": "bad_1",
            "criterion": "ner_preservation",
            "difficulty": "hard",
            "expected": "FAIL",
            "actual_target": "PASS",
            "actual_global": "PASS",
            "score": 0.65,
            "anomaly": "missing entity",
            "reasoning": "missed anomaly",
        }

        # Missing id and expected_anomaly use clean default strings
        item_min_bad = {"input": {}, "expected_output": {"verdict": "PASS"}, "metadata": {}}
        _record_item_into_results(
            results,
            item_min_bad,
            ItemEvaluationResult(
                actual="FAIL",
                expected="PASS",
                score=0.40,
                reasoning="false positive rejection",
                target_actual="FAIL",
                target_score=0.40,
            ),
        )
        assert results.disagreements[1]["id"] == "item"
        assert results.disagreements[1]["anomaly"] == ""


class TestStageAndSuiteExecutionAndReports:
    """Tests for run_stage_calibration retry/abort, report rendering, and suite outcomes."""

    def test_run_stage_calibration_retries_transient_errors_then_aborts_on_fourth(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        store = CalibrationCheckpointStore(checkpoint_dir=tmp_path / "cp")
        # Legacy checkpoint without id/reasoning/target_actual/target_score + full checkpoint item
        legacy_item = {
            "input": {"raw_text": "r_leg", "candidate_text": "c_leg"},
            "expected_output": {"verdict": "PASS"},
        }
        legacy_bad = _make_item(
            "legacy_bad", verdict="FAIL", criterion="orality_removal", difficulty="easy"
        )
        resumed_disagree = _make_item(
            "resumed_bad", verdict="FAIL", criterion="orality_removal", difficulty="hard"
        )
        store.record_item(
            stage="fluid_prose",
            provider="gemini",
            model="m1",
            config_hash="h1",
            item_id="item",
            payload={"actual": "PASS", "expected": "PASS", "score": 0.9},
        )
        store.record_item(
            stage="fluid_prose",
            provider="gemini",
            model="m1",
            config_hash="h1",
            item_id="legacy_bad",
            payload={"actual": "PASS", "expected": "FAIL", "score": 0.12},
        )
        store.record_item(
            stage="fluid_prose",
            provider="gemini",
            model="m1",
            config_hash="h1",
            item_id="resumed_bad",
            payload={
                "actual": "FAIL",
                "expected": "FAIL",
                "score": 0.9,
                "reasoning": "custom restored reason",
                "target_actual": "PASS",
                "target_score": 0.85,
            },
        )

        # Pending items t1 (triggers transient retry loop) and t2
        items = [legacy_item, legacy_bad, resumed_disagree, _make_item("t1"), _make_item("t2")]

        good_eval = _make_eval(
            passed=True,
            score=0.91,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.ORALITY_REMOVAL,
                    score=0.91,
                    passed=True,
                    reasoning="ok",
                ),
            ),
        )
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.side_effect = [
            RuntimeError("503 unavailable"),
            RuntimeError("timeout"),
            RuntimeError("504 gateway"),
            good_eval,
            good_eval,
        ]
        monkeypatch.setattr(
            "cresmo.application.evals.calibration_runner.random.uniform", lambda _a, b: b * 0.25
        )
        slept: list[float] = []
        emitted: list[str] = []
        # Exercise default delay=4.2, jitter=0.8, max_retry_wait=60.0
        results = run_stage_calibration(
            judge=mock_judge,
            spec=spec,
            items=items,
            provider="gemini",
            model="m1",
            config_hash="h1",
            checkpoint_store=store,
            now_fn=lambda: 100.0,
            sleep_fn=slept.append,
            emit_fn=emitted.append,
        )
        assert results.skipped_from_checkpoint == 3
        assert results.evaluated_items == 2
        assert results.overall.hit == 3
        assert results.overall.permissivo_alfa == 1
        assert results.overall.rejeicao == 1
        assert results.target_isolated.hit == 3
        assert results.target_isolated.permissivo_alfa == 2
        assert len(results.disagreements) == 2
        assert results.disagreements[0] == {
            "id": "legacy_bad",
            "criterion": "orality_removal",
            "difficulty": "easy",
            "expected": "FAIL",
            "actual_target": "PASS",
            "actual_global": "PASS",
            "score": 0.12,
            "anomaly": "",
            "reasoning": "",
        }
        assert results.disagreements[1]["actual_global"] == "FAIL"
        assert results.disagreements[1]["reasoning"] == "custom restored reason"
        assert results.disagreements[1]["actual_target"] == "PASS"
        assert results.disagreements[1]["score"] == 0.85
        assert slept == [3.0, 6.0, 12.0, pytest.approx(4.4)]
        assert emitted == [
            "\n" + "=" * 72,
            "CALIBRATING [FLUID_PROSE] -> gemini:m1",
            "Checkpoint resume: 3/5 restored, 2 pending.",
            "Pacing: 4.2s base delay + up to 0.8s jitter between calls",
            "=" * 72,
            "  [RETRY 1/3] Transient error on 't1': 503 unavailable. Waiting 3.0s...",
            "  [RETRY 2/3] Transient error on 't1': timeout. Waiting 6.0s...",
            "  [RETRY 3/3] Transient error on 't1': 504 gateway. Waiting 12.0s...",
            f"[04/05] [{'t1':<28}] Exp: {'PASS':<4} | Target: {'PASS':<4} (0.91) -> HIT",
            f"[05/05] [{'t2':<28}] Exp: {'PASS':<4} | Target: {'PASS':<4} (0.91) -> HIT",
        ]
        # Verify stored checkpoint payload schema for pending item
        cp_items = store.load_completed_items("fluid_prose", "gemini", "m1", "h1")
        assert cp_items["t1"]["target_actual"] == "PASS"
        assert cp_items["t1"]["target_score"] == 0.91
        assert "reasoning" in cp_items["t1"]

        # Fractional delay (0 < 0.4 <= 1) and delay - jitter < 0 with delay + jitter <= 1
        emitted_frac: list[str] = []
        slept_frac: list[float] = []
        mock_judge_frac = MagicMock(spec=LlmJudgePort)
        mock_judge_frac.evaluate.return_value = good_eval
        run_stage_calibration(
            judge=mock_judge_frac,
            spec=spec,
            items=[_make_item("fr1"), _make_item("fr2")],
            provider="gemini",
            model="m_frac",
            config_hash="h_frac",
            checkpoint_store=store,
            delay=0.4,
            jitter=0.5,
            sleep_fn=slept_frac.append,
            emit_fn=emitted_frac.append,
        )
        assert slept_frac == [pytest.approx(0.525)]
        assert emitted_frac[2] == "Pacing: 0.4s base delay + up to 0.5s jitter between calls"

        # delay=0.0 with pending items omits pacing banner, skips sleep, and falls back to item_1
        no_id_pending = {
            "input": {"raw_text": "r_pend", "candidate_text": "c_pend"},
            "expected_output": {"verdict": "PASS"},
        }
        emitted_nodelay: list[str] = []
        slept_nodelay: list[float] = []
        mock_judge_fast = MagicMock(spec=LlmJudgePort)
        mock_judge_fast.evaluate.return_value = good_eval
        run_stage_calibration(
            judge=mock_judge_fast,
            spec=spec,
            items=[no_id_pending, _make_item("f2")],
            provider="gemini",
            model="m_fast",
            config_hash="h_fast",
            checkpoint_store=store,
            delay=0.0,
            jitter=0.0,
            sleep_fn=slept_nodelay.append,
            emit_fn=emitted_nodelay.append,
        )
        assert slept_nodelay == []
        assert all("Pacing:" not in line for line in emitted_nodelay)
        assert all("Checkpoint resume:" not in line for line in emitted_nodelay)
        cp_fast = store.load_completed_items("fluid_prose", "gemini", "m_fast", "h_fast")
        assert "item_1" in cp_fast

        # delay > 0 with 0 pending items (all restored) omits pacing banner
        emitted_all_resumed: list[str] = []
        run_stage_calibration(
            judge=MagicMock(spec=LlmJudgePort),
            spec=spec,
            items=[_make_item("f2")],
            provider="gemini",
            model="m_fast",
            config_hash="h_fast",
            checkpoint_store=store,
            delay=1.0,
            jitter=0.0,
            emit_fn=emitted_all_resumed.append,
        )
        assert emitted_all_resumed[2] == "Checkpoint resume: 1/1 restored, 0 pending."
        assert all("Pacing:" not in line for line in emitted_all_resumed)

        # is_quota_exhausted predicate is forwarded -> aborts without retry on attempt 1
        quota_judge = MagicMock(spec=LlmJudgePort)
        quota_err = RuntimeError("503 disguised quota")
        quota_judge.evaluate.side_effect = quota_err
        with pytest.raises(RuntimeError, match="503 disguised quota"):
            run_stage_calibration(
                judge=quota_judge,
                spec=spec,
                items=[_make_item("q1")],
                provider="gemini",
                model="m_quota",
                config_hash="hq",
                checkpoint_store=store,
                is_quota_exhausted=lambda e: e is quota_err,
                delay=0.0,
                jitter=0.0,
                sleep_fn=lambda _s: pytest.fail("Should not sleep on quota exhaustion"),
                emit_fn=lambda _s: None,
            )

        # 4 consecutive transient errors -> raises
        mock_judge.evaluate.side_effect = [
            RuntimeError("503"),
            RuntimeError("503"),
            RuntimeError("503"),
            RuntimeError("503"),
        ]
        with pytest.raises(RuntimeError, match="503"):
            run_stage_calibration(
                judge=mock_judge,
                spec=spec,
                items=[_make_item("t3")],
                provider="gemini",
                model="m1",
                config_hash="h2",
                checkpoint_store=store,
                delay=0.0,
                jitter=0.0,
                sleep_fn=lambda _s: None,
                emit_fn=lambda _s: None,
            )

    def test_run_stage_calibration_rejects_active_cooldown_and_parks_long_cooldown(
        self, tmp_path: Path
    ) -> None:
        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        store = CalibrationCheckpointStore(checkpoint_dir=tmp_path / "cp")
        store.record_cooldown("fluid_prose", "gemini", "m1", 500.2)

        with pytest.raises(
            CooldownActiveError, match=r"Cooldown active for gemini:m1 \(0s"
        ) as exc_info:
            run_stage_calibration(
                judge=MagicMock(spec=LlmJudgePort),
                spec=spec,
                items=[_make_item("x1")],
                provider="gemini",
                model="m1",
                config_hash="h1",
                checkpoint_store=store,
                now_fn=lambda: 500.0,
                emit_fn=lambda _s: None,
            )
        assert exc_info.value.retry_after_seconds == pytest.approx(0.2)

        store.clear_cooldown("fluid_prose", "gemini", "m1")
        # Exact boundary retry_after == max_retry_wait retries once then succeeds
        boundary_judge = MagicMock(spec=LlmJudgePort)
        boundary_eval = _make_eval(passed=True, score=0.9)
        boundary_judge.evaluate.side_effect = [
            _make_rate_limit("rl_exact", 60.0),
            boundary_eval,
        ]
        boundary_slept: list[float] = []
        run_stage_calibration(
            judge=boundary_judge,
            spec=spec,
            items=[_make_item("b1")],
            provider="gemini",
            model="m_bound",
            config_hash="hb",
            checkpoint_store=store,
            delay=0.0,
            jitter=0.0,
            now_fn=lambda: 1000.0,
            sleep_fn=boundary_slept.append,
            emit_fn=lambda _s: None,
        )
        assert boundary_slept == [60.5]

        # 6 consecutive short cooldowns -> exceeds max 5 retries and parks using max(retry_after, max_retry_wait)
        mock_judge = MagicMock(spec=LlmJudgePort)
        mock_judge.evaluate.side_effect = [_make_rate_limit("rl", 0.1)] * 6
        slept: list[float] = []
        emitted: list[str] = []
        with pytest.raises(RateLimitExceededError):
            run_stage_calibration(
                judge=mock_judge,
                spec=spec,
                items=[_make_item("x2")],
                provider="gemini",
                model="m1",
                config_hash="h1",
                checkpoint_store=store,
                now_fn=lambda: 1000.0,
                sleep_fn=slept.append,
                emit_fn=emitted.append,
            )
        assert slept == [1.0] * 5
        assert store.active_cooldown_until("fluid_prose", "gemini", "m1", now=1000.0) == 1060.0
        assert "[COOLDOWN WAIT 5/5]" in "\n".join(emitted)
        assert "[COOLDOWN ABORT]" in "\n".join(emitted)

    def test_report_generation_saving_and_summary_formatting(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class _FakeDatetime:
            @classmethod
            def now(cls, tz: Any = None) -> datetime:
                assert tz is UTC
                return datetime(2026, 5, 6, 7, 8, 9, tzinfo=tz)

        monkeypatch.setattr("cresmo.application.evals.calibration_runner.datetime", _FakeDatetime)

        spec = build_stage_specs(datasets_dir=tmp_path)["fluid_prose"]
        results = CalibrationResultSet(evaluated_items=1, skipped_from_checkpoint=1)
        results.overall.record("PASS", "PASS")
        results.overall.record("FAIL", "PASS")
        results.target_isolated.record("PASS", "PASS")
        results.target_isolated.record("FAIL", "PASS")
        slice_m = ConfusionMatrix(hit=2, rejeicao=1, permissivo_alfa=1, pedantismo_beta=1)
        results.by_criterion["orality_removal"] = slice_m
        results.by_difficulty["easy"] = slice_m
        long_reason = "R" * 210
        results.disagreements.append(
            {
                "id": "d_01",
                "criterion": "orality_removal",
                "difficulty": "easy",
                "expected": "FAIL",
                "actual_target": "PASS",
                "score": 0.77,
                "reasoning": long_reason,
            }
        )

        m_text = _format_matrix_2x2("MATRIX TITLE", results.target_isolated)
        assert m_text.splitlines() == [
            "",
            "=" * 80,
            "MATRIX TITLE",
            "-" * 80,
            f"{'Ground Truth \\ Judge':<28} | {'Judge: PASS':<20} | {'Judge: FAIL':<20} | {'Total':<8}",
            "-" * 80,
            f"{'PASS (Valid Output)':<28} | {'HIT (TP): 1':<20} | {'PEDANT (FN): 0':<20} | {1:<8}",
            f"{'FAIL (Defective Output)':<28} | {'PERMISSIVE (FP): 1':<20} | {'REJECT (TN): 0':<20} | {1:<8}",
            "-" * 80,
            f"{'Total by Judge':<28} | {2:<20} | {0:<20} | {2:<8}",
            "=" * 80,
        ]

        nested_out = tmp_path / "nested_dir" / "reports" / "out.txt"
        saved = save_calibration_report(
            spec,
            results,
            output_path=nested_out,
            provider="gemini",
            model="m1",
        )
        assert saved.exists()
        content = generate_calibration_report(spec, results, provider="gemini", model="m1")
        assert saved.read_text(encoding="utf-8") == content
        assert content.endswith("\n")
        assert not content.endswith("XX\nXX")

        expected_sdt = [
            f"{i.code:<4} {i.name:<28} | {i.formatted_value:<10} | {i.diagnosis}"
            for i in results.target_isolated.get_all_metrics()
        ]
        slice_row = (
            f"{slice_m.accuracy * 100:5.1f}% | {slice_m.precision * 100:5.1f}% | "
            f"{slice_m.recall * 100:5.1f}% | {slice_m.f1:5.3f} | {slice_m.d_prime:6.2f}"
        )
        expected_report = (
            "\n".join(
                [
                    "=" * 80,
                    "LLM JUDGE CALIBRATION REPORT (STAGE 1: FLUID PROSE)",
                    "=" * 80,
                    "Timestamp:       2026-05-06 07:08:09 UTC",
                    "Stage:           fluid_prose",
                    "Provider:        gemini",
                    "Model:           m1",
                    "Fallback Mode:   DISABLED (enable_fallback=False)",
                    "Valid Items:     2 (fresh=1, resumed=1)",
                    _format_matrix_2x2(
                        "2x2 CONFUSION MATRIX (ISOLATED TARGET CRITERION)", results.target_isolated
                    ),
                    "\n" + "=" * 80,
                    "15 SIGNAL DETECTION THEORY (SDT) METRICS (TARGET ISOLATED)",
                    "-" * 80,
                    f"{'Code':<4} {'Metric':<28} | {'Value':<10} | {'Diagnosis'}",
                    "-" * 80,
                    *expected_sdt,
                    _format_matrix_2x2(
                        "2x2 CONFUSION MATRIX (GLOBAL COMPOSITE GATE)", results.overall
                    ),
                    "\n" + "=" * 80,
                    "SLICE BREAKDOWN BY CRITERION",
                    "-" * 80,
                    f"{'Criterion':<34} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'d-prime':<7}",
                    "-" * 80,
                    f"{'orality_removal':<34} | {5:<4} | {slice_row}",
                    "\n" + "=" * 80,
                    "SLICE BREAKDOWN BY DIFFICULTY",
                    "-" * 80,
                    f"{'Difficulty':<18} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'d-prime':<7}",
                    "-" * 80,
                    f"{'easy':<18} | {5:<4} | {slice_row}",
                    "\n" + "=" * 80,
                    "DISAGREEMENTS",
                    "-" * 80,
                    f"[d_01] crit=orality_removal diff=easy exp=FAIL got=PASS (0.77): {'R' * 180}",
                ]
            )
            + "\n"
        )
        assert content == expected_report

        emitted: list[str] = []
        print_benchmark_summary(
            [
                ModelBenchmarkSummary(
                    stage="fluid_prose",
                    provider="gemini",
                    model="m1",
                    status="APROVADO",
                    accuracy=0.875,
                    d_prime=2.5,
                    f1=0.812,
                    precision=0.80,
                    recall=0.75,
                    alpha_fpr=0.125,
                    evaluated_total=10,
                    dataset_total=10,
                ),
                ModelBenchmarkSummary(
                    stage="gap_filler",
                    provider="gemini",
                    model="m2",
                    status="COOLDOWN",
                    evaluated_total=3,
                    dataset_total=10,
                    cooldown_remaining_s=120.0,
                ),
                ModelBenchmarkSummary(
                    stage="gap_filler",
                    provider="ollama",
                    model="qwen",
                    status="ERRO",
                    evaluated_total=0,
                    dataset_total=10,
                    error_message="X" * 50,
                ),
            ],
            emit_fn=emitted.append,
        )
        assert emitted == [
            "\n" + "=" * 116,
            "UNIFIED LLM JUDGE CALIBRATION SUMMARY (ZERO-FALLBACK)",
            "=" * 116,
            f"{'Stage':<12} | {'Model':<32} | {'Status':<11} | {'Done':<7} | {'Acc':<6} | {'d-prime':<7} | {'F1':<6} | {'Prec':<6} | {'Rec':<6} | {'FPR':<6}",
            "-" * 116,
            f"{'fluid_prose':<12} | {'gemini:m1':<32} | {'APROVADO':<11} | {'10/10':<7} | {'87.5%':>6} | {'2.50':>7} | {'0.812':>6} | {'80.0%':>6} | {'75.0%':>6} | {'12.5%':>6}",
            f"{'gap_filler':<12} | {'gemini:m2':<32} | {'COOLDOWN':<11} | {'3/10':<7} | retry in 120s",
            f"{'gap_filler':<12} | {'ollama:qwen':<32} | {'ERRO':<11} | {'0/10':<7} | {'X' * 32}",
            "=" * 116 + "\n",
        ]

    def test_run_calibration_suite_status_paths_cooldown_and_errors(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        with pytest.raises(
            ValueError, match=r"^--dataset-path can only be used with a single --stage\.$"
        ):
            run_calibration_suite(
                selected_stages=["fluid_prose", "gap_filler"],
                selected_models=[("gemini", "m1")],
                judge_factory=MagicMock(),
                stage_thresholds={},
                dataset_path=tmp_path / "ds.json",
            )

        # Exact status thresholds: APROVADO (0.85, 0 FP), PRE-CALIB (0.85 w/ 1 FP; 0.80 w/ 0 FP), REPROVADO (0.75)
        def _verdict_eval(passed: bool, score: float) -> JudgeEvaluation:
            return _make_eval(
                passed=passed,
                score=score,
                criteria_scores=(
                    CriterionScore(
                        criterion=JudgeCriterion.ORALITY_REMOVAL,
                        score=score,
                        passed=passed,
                        reasoning="ok",
                    ),
                ),
            )

        ds_status = tmp_path / "status_20.json"
        items_20 = [_make_item(f"p_{i}", verdict="PASS") for i in range(17)] + [
            _make_item(f"f_{i}", verdict="FAIL") for i in range(3)
        ]
        ds_status.write_text(json.dumps(items_20), encoding="utf-8")

        seen_factory_calls: list[tuple[str, str, float, bool]] = []
        slept_default: list[float] = []

        def _factory_aprov(
            *, provider: str, model: str, threshold: float, enable_fallback: bool
        ) -> LlmJudgePort:
            seen_factory_calls.append((provider, model, threshold, enable_fallback))
            j = MagicMock(spec=LlmJudgePort)
            j.evaluate.side_effect = [_verdict_eval(True, 0.9) for _ in range(17)] + [
                _verdict_eval(False, 0.2) for _ in range(3)
            ]
            return j

        out_file = tmp_path / "single_report.txt"
        emitted: list[str] = []
        outcome_ok = run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m_aprov")],
            judge_factory=_factory_aprov,
            stage_thresholds={},
            dataset_path=ds_status,
            checkpoint_dir=tmp_path / "cp_aprov",
            output_path=out_file,
            prompt_lookup=lambda _k: {"system_prompt": "sys-v1", "user_prompt": "usr"},
            sleep_fn=slept_default.append,
            emit_fn=emitted.append,
        )
        assert outcome_ok.has_errors is False
        report_written = out_file.read_text(encoding="utf-8")
        assert "Provider:        gemini" in report_written
        assert "Model:           m_aprov" in report_written
        assert seen_factory_calls == [("gemini", "m_aprov", 0.75, False)]
        # 19 inter-item sleeps at default delay=4.2 + uniform(0, 0.8)
        assert len(slept_default) == 19
        assert all(4.2 <= s <= 5.0 for s in slept_default)
        s0 = outcome_ok.summaries[0]
        assert s0.stage == "fluid_prose"
        assert s0.provider == "gemini"
        assert s0.model == "m_aprov"
        assert s0.status == "APROVADO"
        assert s0.accuracy == pytest.approx(1.0)
        assert s0.evaluated_total == 20
        assert s0.dataset_total == 20
        assert "Stages scheduled (1): fluid_prose" in emitted[0]
        assert "UNIFIED LLM JUDGE CALIBRATION SUMMARY (ZERO-FALLBACK)" in "\n".join(emitted)

        # Re-running with changed prompt invalidates hash
        re_judge = MagicMock(spec=LlmJudgePort)
        re_judge.evaluate.side_effect = [_verdict_eval(True, 0.9) for _ in range(17)] + [
            _verdict_eval(False, 0.2) for _ in range(3)
        ]
        run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m_aprov")],
            judge_factory=lambda **_kw: re_judge,
            stage_thresholds={},
            dataset_path=ds_status,
            checkpoint_dir=tmp_path / "cp_aprov",
            output_path=out_file,
            prompt_lookup=lambda _k: {"system_prompt": "sys-v2", "user_prompt": "usr"},
            sleep_fn=lambda _s: None,
            emit_fn=lambda _s: None,
        )
        assert re_judge.evaluate.call_count == 20

        # Multi-model single-stage with explicit output directory (proves single_target=False for >1 model)
        ds_bounds = tmp_path / "bounds.json"
        ds_bounds.write_text(json.dumps(items_20), encoding="utf-8")

        def _factory_bounds(
            *, provider: str, model: str, threshold: float, enable_fallback: bool
        ) -> LlmJudgePort:
            j = MagicMock(spec=LlmJudgePort)
            if model == "m_085_clean":
                j.evaluate.side_effect = (
                    [_verdict_eval(True, 0.9)] * 14
                    + [_verdict_eval(False, 0.2)] * 3
                    + [_verdict_eval(False, 0.2)] * 3
                )
            elif model == "m_085_fp":
                # 15 hit + 2 FN + 1 FP + 2 TN -> acc=0.85, FP=1, prec=15/16, rec=15/17, fpr=1/3, d_prime != 0
                j.evaluate.side_effect = (
                    [_verdict_eval(True, 0.9)] * 15
                    + [_verdict_eval(False, 0.2)] * 2
                    + [_verdict_eval(True, 0.8)]
                    + [_verdict_eval(False, 0.2)] * 2
                )
            elif model == "m_080":
                j.evaluate.side_effect = (
                    [_verdict_eval(True, 0.9)] * 13
                    + [_verdict_eval(False, 0.2)] * 4
                    + [_verdict_eval(False, 0.2)] * 3
                )
            else:
                j.evaluate.side_effect = (
                    [_verdict_eval(True, 0.9)] * 12
                    + [_verdict_eval(False, 0.2)] * 5
                    + [_verdict_eval(False, 0.2)] * 3
                )
            return j

        multi_bounds_dir = tmp_path / "multi_bounds_dir"
        bounds_out = run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[
                ("gemini", "m_085_clean"),
                ("gemini", "m_085_fp"),
                ("gemini", "m_080"),
                ("gemini", "m_075"),
            ],
            judge_factory=_factory_bounds,
            stage_thresholds={"fluid_prose": 0.75},
            dataset_path=ds_bounds,
            checkpoint_dir=tmp_path / "cp_bounds",
            output_path=multi_bounds_dir,
            delay=0.0,
            jitter=0.0,
            sleep_fn=lambda _s: None,
            emit_fn=lambda _s: None,
        )
        bounds_map = {s.model: s for s in bounds_out.summaries}
        assert {k: v.status for k, v in bounds_map.items()} == {
            "m_085_clean": "APROVADO",
            "m_085_fp": "PRE-CALIB",
            "m_080": "PRE-CALIB",
            "m_075": "REPROVADO",
        }
        fp_sum = bounds_map["m_085_fp"]
        assert fp_sum.stage == "fluid_prose"
        assert fp_sum.provider == "gemini"
        assert fp_sum.accuracy == pytest.approx(0.85)
        assert fp_sum.precision == pytest.approx(15 / 16)
        assert fp_sum.recall == pytest.approx(15 / 17)
        assert fp_sum.alpha_fpr == pytest.approx(1 / 3)
        assert fp_sum.f1 == pytest.approx(30 / 33)
        assert fp_sum.d_prime > 0.0
        assert fp_sum.evaluated_total == 20
        assert fp_sum.dataset_total == 20
        assert (multi_bounds_dir / "llm_judge_fluid_prose_gemini_m_085_fp.txt").exists()

        # output_path=None places reports inside custom reports_dir
        default_reports_dir = tmp_path / "default_reports"
        one_item_ds = tmp_path / "one.json"
        one_item_ds.write_text(json.dumps([_make_item("o1", verdict="PASS")]), encoding="utf-8")
        one_judge = MagicMock(spec=LlmJudgePort)
        one_judge.evaluate.return_value = _verdict_eval(True, 0.95)
        run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m_default_dir")],
            judge_factory=lambda **_kw: one_judge,
            stage_thresholds={},
            dataset_path=one_item_ds,
            checkpoint_dir=tmp_path / "cp_defdir",
            reports_dir=default_reports_dir,
            output_path=None,
            delay=0.0,
            jitter=0.0,
            sleep_fn=lambda _s: None,
            emit_fn=lambda _s: None,
        )
        assert (default_reports_dir / "llm_judge_fluid_prose_gemini_m_default_dir.txt").exists()

        # Forwarded non-default delay/jitter/max_retry_wait/now_fn/emit_fn + default max_retry_wait=60.0
        monkeypatch.setattr(
            "cresmo.application.evals.calibration_runner.random.uniform", lambda _a, b: b * 0.5
        )
        slept_nondef: list[float] = []
        emitted_nondef: list[str] = []
        two_item_ds = tmp_path / "two.json"
        two_item_ds.write_text(
            json.dumps([_make_item("n1", verdict="PASS"), _make_item("n2", verdict="PASS")]),
            encoding="utf-8",
        )
        two_judge = MagicMock(spec=LlmJudgePort)
        two_judge.evaluate.return_value = _verdict_eval(True, 0.95)
        run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m_nondef")],
            judge_factory=lambda **_kw: two_judge,
            stage_thresholds={},
            dataset_path=two_item_ds,
            checkpoint_dir=tmp_path / "cp_nondef",
            output_path=tmp_path / "nondef.txt",
            delay=0.3,
            jitter=0.2,
            sleep_fn=slept_nondef.append,
            emit_fn=emitted_nondef.append,
        )
        assert slept_nondef == [pytest.approx(0.4)]
        assert "Pacing: 0.3s base delay + up to 0.2s jitter between calls" in "\n".join(
            emitted_nondef
        )
        assert "UNIFIED LLM JUDGE CALIBRATION SUMMARY (ZERO-FALLBACK)" in "\n".join(emitted_nondef)

        # Custom max_retry_wait=5.0 + now_fn=lambda: 1234.0 vs default max_retry_wait=60.0
        rl_custom_judge = MagicMock(spec=LlmJudgePort)
        rl_custom_judge.evaluate.side_effect = _make_rate_limit("rl10", 10.0)
        custom_cd_dir = tmp_path / "cp_custom_mrw"
        run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m_mrw5")],
            judge_factory=lambda **_kw: rl_custom_judge,
            stage_thresholds={},
            dataset_path=one_item_ds,
            checkpoint_dir=custom_cd_dir,
            output_path=tmp_path / "mrw5.txt",
            max_retry_wait=5.0,
            delay=0.0,
            jitter=0.0,
            now_fn=lambda: 1234.0,
            sleep_fn=lambda _s: pytest.fail("Should abort immediately when 10 > 5"),
            emit_fn=lambda _s: None,
        )
        assert rl_custom_judge.evaluate.call_count == 1
        assert (
            CalibrationCheckpointStore(custom_cd_dir).active_cooldown_until(
                "fluid_prose", "gemini", "m_mrw5", now=1234.0
            )
            == 1244.0
        )

        # Default max_retry_wait=60.0 aborts immediately on 60.5s (not 61.0)
        rl_def_judge = MagicMock(spec=LlmJudgePort)
        rl_def_judge.evaluate.side_effect = _make_rate_limit("rl60_5", 60.5)
        run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "m_mrw_def")],
            judge_factory=lambda **_kw: rl_def_judge,
            stage_thresholds={},
            dataset_path=one_item_ds,
            checkpoint_dir=tmp_path / "cp_def_mrw",
            output_path=tmp_path / "mrw_def.txt",
            delay=0.0,
            jitter=0.0,
            now_fn=lambda: 2000.0,
            sleep_fn=lambda _s: pytest.fail("Should abort immediately when 60.5 > default 60.0"),
            emit_fn=lambda _s: None,
        )
        assert rl_def_judge.evaluate.call_count == 1

        # Multi-stage + output_path directory + stage_thresholds key lookup
        specs = build_stage_specs(datasets_dir=tmp_path)
        multi_stage_dir = tmp_path / "multi_stage_dir"
        quota_flag_seen: list[bool] = []
        thresholds_seen: list[float] = []

        def _factory_multi_stage(
            *, provider: str, model: str, threshold: float, enable_fallback: bool
        ) -> LlmJudgePort:
            thresholds_seen.append(threshold)
            j = MagicMock(spec=LlmJudgePort)
            j.evaluate.return_value = _verdict_eval(True, 0.95)
            return j

        emitted_ms: list[str] = []
        multi_res = run_calibration_suite(
            selected_stages=["fluid_prose", "gap_filler"],
            selected_models=[("gemini", "m1")],
            judge_factory=_factory_multi_stage,
            stage_thresholds={"fluid_prose": 0.8},
            stage_specs=specs,
            seed_only=True,
            checkpoint_dir=tmp_path / "cp_ms",
            output_path=multi_stage_dir,
            delay=0.0,
            jitter=0.0,
            is_quota_exhausted=lambda _e: quota_flag_seen.append(True) or False,
            sleep_fn=lambda _s: None,
            emit_fn=emitted_ms.append,
        )
        assert multi_res.has_errors is False
        assert thresholds_seen == [0.8, 0.75]
        assert "Stages scheduled (2): fluid_prose, gap_filler" in emitted_ms[0]
        assert "Models scheduled (1): gemini:m1" in emitted_ms[1]
        assert (multi_stage_dir / "llm_judge_fluid_prose_gemini_m1.txt").exists()
        assert (multi_stage_dir / "llm_judge_gap_filler_gemini_m1.txt").exists()

        # Active cooldown pre-skip + caught runtime error + caught rate-limit cooldown + summary fields
        store = CalibrationCheckpointStore(checkpoint_dir=tmp_path / "cp2")
        items_seed = list(specs["fluid_prose"].seed_items)
        cfg_cool = compute_config_hash(specs["fluid_prose"], items_seed, 0.75)
        store.record_item(
            "fluid_prose", "gemini", "cool_model", cfg_cool, items_seed[0]["id"], {"actual": "PASS"}
        )
        store.record_cooldown("fluid_prose", "gemini", "cool_model", 1000.3)

        def _factory_mixed(
            *, provider: str, model: str, threshold: float, enable_fallback: bool
        ) -> LlmJudgePort:
            assert provider == "gemini"
            assert threshold == 0.75
            assert enable_fallback is False
            j = MagicMock(spec=LlmJudgePort)
            if model == "rl_model":
                j.evaluate.side_effect = _make_rate_limit("rl", 900.0)
            elif model == "err_model":
                j.evaluate.side_effect = [RuntimeError("503")]
            return j

        emitted2: list[str] = []
        outcome_mixed = run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[
                ("gemini", "cool_model"),
                ("gemini", "rl_model"),
                ("gemini", "err_model"),
            ],
            judge_factory=_factory_mixed,
            stage_thresholds={"fluid_prose": 0.75},
            seed_only=True,
            checkpoint_dir=tmp_path / "cp2",
            output_path=tmp_path / "multi_out",
            delay=0.0,
            jitter=0.0,
            is_quota_exhausted=lambda _e: quota_flag_seen.append(True) or True,
            now_fn=lambda: 1000.0,
            sleep_fn=lambda _s: pytest.fail("Should not sleep"),
            emit_fn=emitted2.append,
        )
        assert quota_flag_seen == [True]
        assert outcome_mixed.has_errors is True
        by_model = {s.model: s for s in outcome_mixed.summaries}
        assert by_model["cool_model"] == ModelBenchmarkSummary(
            stage="fluid_prose",
            provider="gemini",
            model="cool_model",
            status="COOLDOWN",
            evaluated_total=1,
            dataset_total=len(items_seed),
            cooldown_remaining_s=pytest.approx(0.3),
        )
        assert by_model["rl_model"] == ModelBenchmarkSummary(
            stage="fluid_prose",
            provider="gemini",
            model="rl_model",
            status="COOLDOWN",
            evaluated_total=0,
            dataset_total=len(items_seed),
            cooldown_remaining_s=pytest.approx(900.0),
        )
        assert by_model["err_model"] == ModelBenchmarkSummary(
            stage="fluid_prose",
            provider="gemini",
            model="err_model",
            status="ERRO",
            evaluated_total=0,
            dataset_total=len(items_seed),
            error_message="503",
        )
        emitted2_text = "\n".join(emitted2)
        assert (
            "Models scheduled (3): gemini:cool_model, gemini:rl_model, gemini:err_model"
            in emitted2_text
        )
        assert (
            f"[COOLDOWN SKIP] fluid_prose | gemini:cool_model in cooldown for 0s (1/{len(items_seed)} checkpointed)."
            in emitted2_text
        )
        assert "[ERROR] fluid_prose | gemini:err_model failed: 503" in emitted2_text
        assert "UNIFIED LLM JUDGE CALIBRATION SUMMARY (ZERO-FALLBACK)" in emitted2_text

        # Non-zero evaluated_total preserved on rate-limit cooldown and error paths
        two_item_ds = tmp_path / "two_items.json"
        two_items = [_make_item("i1", verdict="PASS"), _make_item("i2", verdict="PASS")]
        two_item_ds.write_text(json.dumps(two_items), encoding="utf-8")
        store_partial = CalibrationCheckpointStore(checkpoint_dir=tmp_path / "cp_partial")
        cfg_partial = compute_config_hash(specs["fluid_prose"], two_items, 0.75)
        for mod in ("rl_partial", "err_partial"):
            store_partial.record_item(
                "fluid_prose",
                "gemini",
                mod,
                cfg_partial,
                "i1",
                {
                    "actual": "PASS",
                    "expected": "PASS",
                    "score": 0.9,
                    "target_actual": "PASS",
                    "target_score": 0.9,
                },
            )

        def _factory_partial(
            *, provider: str, model: str, threshold: float, enable_fallback: bool
        ) -> LlmJudgePort:
            j = MagicMock(spec=LlmJudgePort)
            if model == "rl_partial":
                j.evaluate.side_effect = _make_rate_limit("rl", 900.0)
            elif model == "err_partial":
                j.evaluate.side_effect = [RuntimeError("503")]
            return j

        outcome_partial = run_calibration_suite(
            selected_stages=["fluid_prose"],
            selected_models=[("gemini", "rl_partial"), ("gemini", "err_partial")],
            judge_factory=_factory_partial,
            stage_thresholds={"fluid_prose": 0.75},
            stage_specs=specs,
            dataset_path=two_item_ds,
            checkpoint_dir=tmp_path / "cp_partial",
            output_path=None,
            delay=0.0,
            jitter=0.0,
            is_quota_exhausted=lambda _e: True,
            now_fn=lambda: 1000.0,
            sleep_fn=lambda _s: pytest.fail("Should not sleep"),
            emit_fn=lambda _s: None,
        )
        by_partial = {s.model: s for s in outcome_partial.summaries}
        assert by_partial["rl_partial"].evaluated_total == 1
        assert by_partial["rl_partial"].status == "COOLDOWN"
        assert by_partial["rl_partial"].cooldown_remaining_s == pytest.approx(900.0)
        assert by_partial["err_partial"].evaluated_total == 1
        assert by_partial["err_partial"].status == "ERRO"
        assert by_partial["err_partial"].error_message == "503"
