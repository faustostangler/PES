"""Hermetic unit tests for calibration specs, parsers, thresholds, and config hashing.

Conforms to:
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

import pytest

from cresmo.application.evals.calibration_metrics import CalibrationVerdict, ConfusionMatrix
from cresmo.application.evals.specs import (
    CalibrationThresholds,
    build_stage_specs,
    classify_verdict,
    compute_config_hash,
    parse_model_specs,
    parse_stage_specs,
    resolve_model_spec,
    sanitize_report_filename,
)
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.quality import JudgeCriterion


class TestCalibrationSpecs:
    """Unit tests covering stage specs, parsing, verdicts, and hash determinism."""

    def test_build_stage_specs_points_to_datasets_and_seeds(self, tmp_path: Path) -> None:
        ds = tmp_path / "datasets"
        seeds = tmp_path / "custom_seeds"
        specs = build_stage_specs(datasets_dir=ds, seeds_dir=seeds)

        assert set(specs.keys()) == {"fluid_prose", "gap_filler", "long_expander", "wide_expander"}
        fp = specs["fluid_prose"]
        assert fp.stage_name == "fluid_prose"
        assert fp.label == "Stage 1: Fluid Prose"
        assert fp.prompt_key is PromptKey.JUDGE_FLUID_PROSE
        assert fp.default_golden_set_path == ds / "fluid_prose_golden_set.json"
        assert fp.default_seed_path == seeds / "fluid_prose_seed.json"
        assert len(fp.required_criteria) == 6

        gf = specs["gap_filler"]
        assert gf.stage_name == "gap_filler"
        assert gf.label == "Stage 2: Gap Filler"
        assert gf.prompt_key is PromptKey.JUDGE_GAP_FILLER
        assert gf.default_golden_set_path == ds / "gap_filler_golden_set.json"
        assert gf.default_seed_path == seeds / "gap_filler_seed.json"
        assert JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION in gf.required_criteria
        assert len(gf.required_criteria) == 7

        le = specs["long_expander"]
        assert le.stage_name == "long_expander"
        assert le.label == "Stage 3: Long Expander"
        assert le.prompt_key is PromptKey.JUDGE_LONG_EXPANDER
        assert le.default_golden_set_path == ds / "long_expander_golden_set.json"
        assert le.default_seed_path == seeds / "long_expander_seed.json"
        assert JudgeCriterion.LONGUE_DUREE_STRATIFICATION in le.required_criteria
        assert len(le.required_criteria) == 5

        we = specs["wide_expander"]
        assert we.stage_name == "wide_expander"
        assert we.label == "Stage 4: Wide Expander"
        assert we.prompt_key is PromptKey.JUDGE_WIDE_EXPANDER
        assert we.default_golden_set_path == ds / "wide_expander_golden_set.json"
        assert we.default_seed_path == seeds / "wide_expander_seed.json"
        assert JudgeCriterion.SYNCHRONIC_CONNECTIVITY in we.required_criteria
        assert JudgeCriterion.COMPARATIVE_PARALLELISM in we.required_criteria
        assert len(we.required_criteria) == 5

        default_seed_specs = build_stage_specs(datasets_dir=ds)
        assert default_seed_specs["fluid_prose"].default_seed_path == (
            ds / "seeds" / "fluid_prose_seed.json"
        )
        assert default_seed_specs["gap_filler"].default_seed_path == (
            ds / "seeds" / "gap_filler_seed.json"
        )
        assert default_seed_specs["long_expander"].default_seed_path == (
            ds / "seeds" / "long_expander_seed.json"
        )
        assert default_seed_specs["wide_expander"].default_seed_path == (
            ds / "seeds" / "wide_expander_seed.json"
        )

    @pytest.mark.parametrize(
        ("spec_str", "default_prov", "expected"),
        [
            ("gemini:gemini-3.5-flash-lite", "ollama", ("gemini", "gemini-3.5-flash-lite")),
            ("ollama:qwen3:8b", "gemini", ("ollama", "qwen3:8b")),
            ("gemini-3.8-flash", "ollama", ("gemini", "gemini-3.8-flash")),
            ("gemma-4-31b-it", "ollama", ("gemini", "gemma-4-31b-it")),
            ("ollama-qwen", "gemini", ("ollama", "ollama-qwen")),
            ("typesafe-mini", "gemini", ("typesafe", "typesafe-mini")),
            ("custom-model", "ollama", ("ollama", "custom-model")),
        ],
    )
    def test_resolve_model_spec_infers_provider(
        self, spec_str: str, default_prov: str, expected: tuple[str, str]
    ) -> None:
        assert resolve_model_spec(spec_str, default_provider=default_prov) == expected
        assert resolve_model_spec("custom-model") == ("gemini", "custom-model")

    def test_parse_stage_specs_and_model_specs_deduplicate_and_validate(
        self, tmp_path: Path
    ) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        assert parse_stage_specs(None, None, stage_specs=specs) == [
            "fluid_prose",
            "gap_filler",
            "long_expander",
            "wide_expander",
        ]
        assert parse_stage_specs(["all"], None, stage_specs=specs) == [
            "fluid_prose",
            "gap_filler",
            "long_expander",
            "wide_expander",
        ]
        assert parse_stage_specs(
            ["fluid-prose,gap_filler", "fluid_prose"], None, stage_specs=specs
        ) == [
            "fluid_prose",
            "gap_filler",
        ]
        assert parse_stage_specs(None, "gap-filler", stage_specs=specs) == ["gap_filler"]
        assert parse_stage_specs(None, "fluid_prose,gap_filler", stage_specs=specs) == [
            "fluid_prose",
            "gap_filler",
        ]

        with pytest.raises(
            ValueError,
            match=(
                r"Unknown stage 'bogus'\. Valid stages: "
                r"fluid_prose, gap_filler, long_expander, wide_expander, all\."
            ),
        ):
            parse_stage_specs(["bogus"], None, stage_specs=specs)

        assert parse_model_specs(
            ["gemini:m1,ollama:m2", "gemini:m1"], None, default_provider="gemini"
        ) == [("gemini", "m1"), ("ollama", "m2")]
        assert parse_model_specs(["custom-model"], None, default_provider="ollama") == [
            ("ollama", "custom-model")
        ]
        assert parse_model_specs(None, "gemini-3.8-flash") == [("gemini", "gemini-3.8-flash")]
        assert parse_model_specs(None, "   ", default_models=("m_a", "gemini:m_a")) == [
            ("gemini", "m_a")
        ]

    def test_sanitize_report_filename_strips_provider_prefix_and_bad_chars(self) -> None:
        assert (
            sanitize_report_filename("fluid_prose", "gemini", "gemini:Models/Flash 2.5")
            == "llm_judge_fluid_prose_gemini_Models_Flash_2.5.txt"
        )

    def test_classify_verdict_respects_custom_and_default_thresholds(self) -> None:
        cm_approved = ConfusionMatrix(
            hit=9, correct_rejection=8, false_reject_beta=3, false_accept_alpha=0
        )
        assert cm_approved.accuracy == pytest.approx(0.85)
        assert classify_verdict(cm_approved) is CalibrationVerdict.APPROVED

        cm_pre = ConfusionMatrix(
            hit=9, correct_rejection=8, false_reject_beta=2, false_accept_alpha=1
        )
        assert cm_pre.accuracy == pytest.approx(0.85)
        assert classify_verdict(cm_pre) is CalibrationVerdict.PRE_CALIBRATED

        cm_pre_edge = ConfusionMatrix(
            hit=8, correct_rejection=8, false_reject_beta=4, false_accept_alpha=0
        )
        assert cm_pre_edge.accuracy == pytest.approx(0.80)
        assert classify_verdict(cm_pre_edge) is CalibrationVerdict.PRE_CALIBRATED

        cm_rejected = ConfusionMatrix(
            hit=7, correct_rejection=8, false_reject_beta=4, false_accept_alpha=1
        )
        assert cm_rejected.accuracy == pytest.approx(0.75)
        assert classify_verdict(cm_rejected) is CalibrationVerdict.REJECTED

        custom = CalibrationThresholds(
            approved_min_accuracy=0.70,
            approved_max_false_accept=1,
            pre_calibrated_min_accuracy=0.60,
        )
        assert classify_verdict(cm_rejected, custom) is CalibrationVerdict.APPROVED

    def test_compute_config_hash_is_deterministic_and_handles_lookup_errors(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        specs = build_stage_specs(datasets_dir=tmp_path)
        spec = specs["fluid_prose"]
        items: list[dict[str, Any]] = [{"id": "a", "text": "São Paulo — café"}]
        received_keys: list[PromptKey] = []

        def _ok_lookup(key: PromptKey) -> dict[str, str]:
            received_keys.append(key)
            return {"system_prompt": "sys", "user_prompt": "usr"}

        digest = compute_config_hash(spec, items, 0.851234567, prompt_lookup=_ok_lookup)
        assert received_keys == [PromptKey.JUDGE_FLUID_PROSE]
        expected_canonical = {
            "stage": "fluid_prose",
            "threshold": 0.851235,
            "required_criteria": [c.value for c in spec.required_criteria],
            "prompt": {"system_prompt": "sys", "user_prompt": "usr"},
            "items": items,
        }
        assert (
            digest
            == hashlib.sha256(
                json.dumps(expected_canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()
        )

        def _failing_lookup(_key: PromptKey) -> dict[str, str]:
            raise KeyError("catalog offline")

        with caplog.at_level(logging.DEBUG, logger="cresmo.application.evals.specs"):
            fallback_digest = compute_config_hash(spec, items, 0.85, prompt_lookup=_failing_lookup)
        assert any(
            rec.name == "cresmo.application.evals.specs"
            and "Prompt lookup unavailable for config hash" in rec.getMessage()
            for rec in caplog.records
        )
        default_canonical = {
            "stage": "fluid_prose",
            "threshold": 0.85,
            "required_criteria": [c.value for c in spec.required_criteria],
            "prompt": {"system_prompt": "", "user_prompt": ""},
            "items": items,
        }
        expected_default_digest = hashlib.sha256(
            json.dumps(default_canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        assert fallback_digest == expected_default_digest
        assert compute_config_hash(spec, items, 0.85, prompt_lookup=None) == expected_default_digest
