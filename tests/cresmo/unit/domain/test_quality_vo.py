"""Exhaustive Unit Tests for Quality Value Objects (ADR-029, SPEC-012).

Tests every boundary, invariant, string formatting, and mutant branch in:
src/cresmo/domain/value_objects/quality.py
"""

from __future__ import annotations

import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.quality import (
    DEFAULT_FLUID_PROSE_WEIGHTS,
    DEFAULT_MECHANICAL_VETO_CRITERIA,
    CandidateText,
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
    StageEvaluationSpec,
    compute_composite_verdict,
    resolve_stage_scoring_policy,
)


class TestJudgeCriterion:
    """Test criterion enum values."""

    def test_criterion_enum_values(self) -> None:
        assert JudgeCriterion.ORALITY_REMOVAL.value == "orality_removal"
        assert JudgeCriterion.SEMANTIC_FAITHFULNESS.value == "semantic_faithfulness"
        assert JudgeCriterion.NER_PRESERVATION.value == "ner_preservation"
        assert JudgeCriterion.STRUCTURAL_COMPLIANCE.value == "structural_compliance"
        assert JudgeCriterion.INVENTORY_COHERENCE.value == "inventory_coherence"
        assert JudgeCriterion.INDEX_SYNTHESIS_QUALITY.value == "index_synthesis_quality"


class TestCandidateText:
    """Invariants and behaviors of CandidateText."""

    def test_valid_candidate_text(self) -> None:
        ct = CandidateText(text="Clean transformed text", stage_name="fluid_prose")
        assert ct.text == "Clean transformed text"
        assert ct.stage_name == "fluid_prose"
        assert ct.metadata == {}

    def test_candidate_text_with_metadata(self) -> None:
        meta = {"model": "gemini-2.0-flash", "tokens": 128}
        ct = CandidateText(text="Result", stage_name="indexing", metadata=meta)
        assert ct.metadata == meta

    @pytest.mark.parametrize("empty_text", ["", "   ", "\n\t"])
    def test_empty_text_raises_validation_error(self, empty_text: str) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^CandidateText for 'fluid_prose' cannot be empty or whitespace\.$",
        ):
            CandidateText(text=empty_text, stage_name="fluid_prose")

    @pytest.mark.parametrize("empty_stage", ["", "   ", "\t"])
    def test_empty_stage_name_raises_validation_error(self, empty_stage: str) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^CandidateText stage_name cannot be empty or whitespace\.$",
        ):
            CandidateText(text="Some text", stage_name=empty_stage)


class TestCriterionScore:
    """Invariants and behaviors of CriterionScore."""

    def test_valid_criterion_score(self) -> None:
        cs = CriterionScore(
            criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
            score=0.88,
            passed=True,
            reasoning="Faithful semantics",
            improvement_suggestion="Keep it up",
        )
        assert cs.criterion == JudgeCriterion.SEMANTIC_FAITHFULNESS
        assert cs.score == 0.88
        assert cs.passed is True
        assert cs.reasoning == "Faithful semantics"
        assert cs.improvement_suggestion == "Keep it up"

    def test_criterion_score_defaults(self) -> None:
        cs = CriterionScore(
            criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
            score=0.5,
            passed=True,
        )
        assert cs.reasoning == ""
        assert cs.improvement_suggestion == ""

    @pytest.mark.parametrize("boundary_score", [0.0, 1.0])
    def test_criterion_score_exact_boundaries(self, boundary_score: float) -> None:
        cs = CriterionScore(
            criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
            score=boundary_score,
            passed=True,
        )
        assert cs.score == boundary_score

    @pytest.mark.parametrize("invalid_score", [-0.01, 1.01])
    def test_criterion_score_out_of_bounds_raises_value_error(self, invalid_score: float) -> None:
        with pytest.raises(
            ValueError,
            match=rf"^Score must be between 0\.0 and 1\.0, got: {invalid_score}$",
        ):
            CriterionScore(
                criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
                score=invalid_score,
                passed=True,
            )


class TestJudgeEvaluation:
    """Invariants and behaviors of JudgeEvaluation."""

    def test_valid_judge_evaluation(self) -> None:
        s1 = CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 0.9, True)
        je = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=0.9,
            criteria_scores=(s1,),
            provider="gemini",
            latency_ms=15.5,
            trace_id="tr-123",
        )
        assert je.target_stage == "fluid_prose"
        assert je.passed is True
        assert je.overall_score == 0.9
        assert je.criteria_scores == (s1,)
        assert je.provider == "gemini"
        assert je.latency_ms == 15.5
        assert je.trace_id == "tr-123"

    def test_judge_evaluation_defaults(self) -> None:
        je = JudgeEvaluation(
            target_stage="raw_indexing",
            passed=False,
            overall_score=0.4,
            criteria_scores=(),
            provider="ollama",
        )
        assert je.latency_ms == 0.0
        assert je.trace_id is None

    @pytest.mark.parametrize("boundary_overall", [0.0, 1.0])
    def test_overall_score_boundaries(self, boundary_overall: float) -> None:
        je = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=True,
            overall_score=boundary_overall,
            criteria_scores=(),
            provider="gemini",
        )
        assert je.overall_score == boundary_overall

    @pytest.mark.parametrize("invalid_overall", [-0.01, 1.01])
    def test_overall_score_out_of_bounds_raises_value_error(self, invalid_overall: float) -> None:
        with pytest.raises(
            ValueError,
            match=rf"^Overall score must be between 0\.0 and 1\.0, got: {invalid_overall}$",
        ):
            JudgeEvaluation(
                target_stage="fluid_prose",
                passed=False,
                overall_score=invalid_overall,
                criteria_scores=(),
                provider="gemini",
            )

    def test_get_score_found_and_not_found(self) -> None:
        s1 = CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 0.9, True)
        s2 = CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.8, True)
        je = JudgeEvaluation(
            target_stage="stage",
            passed=True,
            overall_score=0.85,
            criteria_scores=(s1, s2),
            provider="gemini",
        )
        assert je.get_score(JudgeCriterion.ORALITY_REMOVAL) is s1
        assert je.get_score(JudgeCriterion.SEMANTIC_FAITHFULNESS) is s2
        assert je.get_score(JudgeCriterion.NER_PRESERVATION) is None

    def test_extract_critique_all_passed(self) -> None:
        s1 = CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 0.9, True)
        je = JudgeEvaluation(
            target_stage="stage",
            passed=True,
            overall_score=0.9,
            criteria_scores=(s1,),
            provider="gemini",
        )
        assert je.extract_critique() == "Quality threshold not met."

    def test_extract_critique_with_failures_and_suggestions(self) -> None:
        s1 = CriterionScore(
            criterion=JudgeCriterion.ORALITY_REMOVAL,
            score=0.4,
            passed=False,
            reasoning="Too many fillers",
            improvement_suggestion="Strip 'tipo assim'",
        )
        s2 = CriterionScore(
            criterion=JudgeCriterion.NER_PRESERVATION,
            score=0.5,
            passed=False,
            reasoning="Lost entity X",
            improvement_suggestion="",
        )
        s3 = CriterionScore(
            criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
            score=0.95,
            passed=True,
            reasoning="Faithful",
        )
        je = JudgeEvaluation(
            target_stage="stage",
            passed=False,
            overall_score=0.6,
            criteria_scores=(s1, s2, s3),
            provider="gemini",
        )
        expected = (
            "- orality_removal: Too many fillers (Suggestion: Strip 'tipo assim')\n"
            "- ner_preservation: Lost entity X"
        )
        assert je.extract_critique() == expected


class TestEvaluationContext:
    """Invariants and defaults of EvaluationContext."""

    def test_evaluation_context_fields_and_defaults(self) -> None:
        ctx = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="source text",
            candidate_text="candidate text",
        )
        assert ctx.stage_name == "fluid_prose"
        assert ctx.raw_text == "source text"
        assert ctx.candidate_text == "candidate text"
        assert ctx.metadata == {}
        assert ctx.trace_id is None
        assert ctx.required_criteria == ()
        assert ctx.observation_id is None


class TestStageEvaluationSpec:
    """Invariants of StageEvaluationSpec."""

    def test_spec_defaults(self) -> None:
        spec = StageEvaluationSpec()
        assert spec.required_criteria == ()
        assert spec.metadata == {}
        assert spec.max_attempts == 1
        # Default candidate_extractor stringifies
        assert spec.candidate_extractor(123) == "123"

    @pytest.mark.parametrize("invalid_attempts", [0, -1, -5])
    def test_max_attempts_less_than_1_raises_value_error(self, invalid_attempts: int) -> None:
        with pytest.raises(
            ValueError,
            match=rf"^max_attempts must be >= 1, got {invalid_attempts}$",
        ):
            StageEvaluationSpec(max_attempts=invalid_attempts)


class TestWeightedAverageAndMechanicalVeto:
    """Tests for Weighted Average + Mechanical Veto (Two-Layered Quality Gate)."""

    def test_perfect_scores_pass_without_veto(self) -> None:
        scores = (
            CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 1.0, True),
            CriterionScore(JudgeCriterion.NER_PRESERVATION, 1.0, True),
            CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 1.0, True),
            CriterionScore(JudgeCriterion.EPISTEMIC_CRITIQUE, 1.0, True),
            CriterionScore(JudgeCriterion.STRUCTURAL_COMPLIANCE, 1.0, True),
            CriterionScore(JudgeCriterion.AUTHORIAL_VOICE, 1.0, True),
        )
        eval_res = JudgeEvaluation.create_with_composite_verdict(
            target_stage="fluid_prose",
            criteria_scores=scores,
            provider="gemini",
        )
        assert eval_res.overall_score == 1.0
        assert eval_res.passed is True
        assert eval_res.is_vetoed is False
        assert len(eval_res.veto_reasons) == 0

    def test_high_average_vetoed_by_semantic_faithfulness(self) -> None:
        # Faithfulness = 0.70 (< 0.80 veto threshold), all others = 1.0
        # Weighted avg: 0.25*0.70 + 0.25*1.0 + 0.20*1.0 + 0.10*1.0 + 0.10*1.0 + 0.10*1.0 = 0.925
        scores = (
            CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.70, False),
            CriterionScore(JudgeCriterion.NER_PRESERVATION, 1.0, True),
            CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 1.0, True),
            CriterionScore(JudgeCriterion.EPISTEMIC_CRITIQUE, 1.0, True),
            CriterionScore(JudgeCriterion.STRUCTURAL_COMPLIANCE, 1.0, True),
            CriterionScore(JudgeCriterion.AUTHORIAL_VOICE, 1.0, True),
        )
        eval_res = JudgeEvaluation.create_with_composite_verdict(
            target_stage="fluid_prose",
            criteria_scores=scores,
            provider="gemini",
        )
        # Even with high overall score (0.925), mechanical veto MUST reject the sample
        assert eval_res.overall_score == pytest.approx(0.925, abs=1e-3)
        assert eval_res.passed is False
        assert eval_res.is_vetoed is True
        assert any("semantic_faithfulness" in r for r in eval_res.veto_reasons)
        critique = eval_res.extract_critique()
        assert "[CRITICAL MECHANICAL VETO]" in critique

    def test_high_average_vetoed_by_ner_preservation(self) -> None:
        # NER = 0.60 (< 0.80 veto threshold), all others = 1.0
        scores = (
            CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 1.0, True),
            CriterionScore(JudgeCriterion.NER_PRESERVATION, 0.60, False),
            CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 1.0, True),
            CriterionScore(JudgeCriterion.EPISTEMIC_CRITIQUE, 1.0, True),
            CriterionScore(JudgeCriterion.STRUCTURAL_COMPLIANCE, 1.0, True),
            CriterionScore(JudgeCriterion.AUTHORIAL_VOICE, 1.0, True),
        )
        eval_res = JudgeEvaluation.create_with_composite_verdict(
            target_stage="fluid_prose",
            criteria_scores=scores,
            provider="gemini",
        )
        assert eval_res.passed is False
        assert eval_res.is_vetoed is True
        assert any("ner_preservation" in r for r in eval_res.veto_reasons)

    def test_minor_criterion_low_does_not_veto_if_weighted_avg_passes(self) -> None:
        # Voice = 0.50 (weight 0.10), all others = 1.0
        # Weighted avg: 0.25*1.0 + 0.25*1.0 + 0.20*1.0 + 0.10*1.0 + 0.10*1.0 + 0.10*0.50 = 0.95
        scores = (
            CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 1.0, True),
            CriterionScore(JudgeCriterion.NER_PRESERVATION, 1.0, True),
            CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 1.0, True),
            CriterionScore(JudgeCriterion.EPISTEMIC_CRITIQUE, 1.0, True),
            CriterionScore(JudgeCriterion.STRUCTURAL_COMPLIANCE, 1.0, True),
            CriterionScore(JudgeCriterion.AUTHORIAL_VOICE, 0.50, False),
        )
        eval_res = JudgeEvaluation.create_with_composite_verdict(
            target_stage="fluid_prose",
            criteria_scores=scores,
            provider="gemini",
        )
        assert eval_res.overall_score == pytest.approx(0.95, abs=1e-3)
        assert eval_res.is_vetoed is False
        assert eval_res.passed is True

    def test_weighted_avg_fails_even_without_veto_if_score_below_threshold(self) -> None:
        # All pass veto threshold (0.80), but multiple criteria are 0.70
        # Faithfulness = 0.80, NER = 0.80, Orality = 0.70, Epistemic = 0.70, Struct = 0.70, Voice = 0.70
        # Weighted avg = 0.25*0.8 + 0.25*0.8 + 0.20*0.7 + 0.10*0.7 + 0.10*0.7 + 0.10*0.7 = 0.75 (< 0.80)
        scores = (
            CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.80, True),
            CriterionScore(JudgeCriterion.NER_PRESERVATION, 0.80, True),
            CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 0.70, False),
            CriterionScore(JudgeCriterion.EPISTEMIC_CRITIQUE, 0.70, False),
            CriterionScore(JudgeCriterion.STRUCTURAL_COMPLIANCE, 0.70, False),
            CriterionScore(JudgeCriterion.AUTHORIAL_VOICE, 0.70, False),
        )
        eval_res = JudgeEvaluation.create_with_composite_verdict(
            target_stage="fluid_prose",
            criteria_scores=scores,
            provider="gemini",
        )
        assert eval_res.overall_score == pytest.approx(0.75, abs=1e-3)
        assert eval_res.is_vetoed is False
        assert eval_res.passed is False

    def test_long_expander_scoring_policy_and_empirical_veto(self) -> None:
        from cresmo.domain.value_objects import (
            LONG_EXPANDER_CANONICAL_WEIGHTS,
            LONG_EXPANDER_MECHANICAL_VETO_CRITERIA,
            resolve_stage_scoring_policy,
        )

        weights, vetoes = resolve_stage_scoring_policy("long_expander")
        assert weights == LONG_EXPANDER_CANONICAL_WEIGHTS
        assert vetoes == LONG_EXPANDER_MECHANICAL_VETO_CRITERIA
        assert weights[JudgeCriterion.LONGUE_DUREE_STRATIFICATION] == 0.35
        assert sum(weights.values()) == pytest.approx(1.0)
        assert JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING in vetoes
        assert JudgeCriterion.EXTRA_INFO_GRANULARITY in vetoes

        # Empirical grounding 0.50 (< 0.80 veto) rejects despite high weighted avg
        # 0.35*1.0 + 0.25*0.50 + 0.20*1.0 + 0.10*1.0 + 0.10*1.0 = 0.875 >= 0.80
        scores = (
            CriterionScore(JudgeCriterion.LONGUE_DUREE_STRATIFICATION, 1.0, True),
            CriterionScore(JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING, 0.50, False),
            CriterionScore(JudgeCriterion.HISTORICAL_PALIMPSEST, 1.0, True),
            CriterionScore(JudgeCriterion.EXTRA_INFO_GRANULARITY, 1.0, True),
            CriterionScore(JudgeCriterion.IMPLICIT_FRAMING_STYLE, 1.0, True),
        )
        eval_res = JudgeEvaluation.create_with_composite_verdict(
            target_stage="long_expander",
            criteria_scores=scores,
            provider="gemini",
        )
        assert eval_res.overall_score == pytest.approx(0.875, abs=1e-3)
        assert eval_res.is_vetoed is True
        assert eval_res.passed is False
        assert any("empirical_historical_grounding" in r for r in eval_res.veto_reasons)

    def test_wide_expander_scoring_policy_and_empirical_veto(self) -> None:
        from cresmo.domain.value_objects import (
            WIDE_EXPANDER_CANONICAL_WEIGHTS,
            WIDE_EXPANDER_MECHANICAL_VETO_CRITERIA,
            resolve_stage_scoring_policy,
        )

        weights, vetoes = resolve_stage_scoring_policy("wide_expander")
        assert weights == WIDE_EXPANDER_CANONICAL_WEIGHTS
        assert vetoes == WIDE_EXPANDER_MECHANICAL_VETO_CRITERIA
        assert weights[JudgeCriterion.SYNCHRONIC_CONNECTIVITY] == 0.30
        assert weights[JudgeCriterion.COMPARATIVE_PARALLELISM] == 0.30
        assert sum(weights.values()) == pytest.approx(1.0)
        assert JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING in vetoes
        assert JudgeCriterion.EXTRA_INFO_GRANULARITY in vetoes

        # Empirical grounding 0.50 (< 0.80 veto) rejects despite high weighted avg
        # 0.30*1.0 + 0.30*1.0 + 0.20*0.50 + 0.10*1.0 + 0.10*1.0 = 0.90 >= 0.80
        scores = (
            CriterionScore(JudgeCriterion.SYNCHRONIC_CONNECTIVITY, 1.0, True),
            CriterionScore(JudgeCriterion.COMPARATIVE_PARALLELISM, 1.0, True),
            CriterionScore(JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING, 0.50, False),
            CriterionScore(JudgeCriterion.EXTRA_INFO_GRANULARITY, 1.0, True),
            CriterionScore(JudgeCriterion.IMPLICIT_FRAMING_STYLE, 1.0, True),
        )
        eval_res = JudgeEvaluation.create_with_composite_verdict(
            target_stage="wide_expander",
            criteria_scores=scores,
            provider="gemini",
        )
        assert eval_res.overall_score == pytest.approx(0.90, abs=1e-3)
        assert eval_res.is_vetoed is True
        assert eval_res.passed is False
        assert any("empirical_historical_grounding" in r for r in eval_res.veto_reasons)

    def test_compute_composite_verdict_boundaries_defaults_and_fallbacks(self) -> None:
        # Empty criteria returns zeroed failing verdict
        assert compute_composite_verdict(()) == (0.0, False, False, ())

        # Zero total_weight falls back safely to 0.0
        zero_weight_scores = (CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 0.9, True),)
        assert compute_composite_verdict(
            zero_weight_scores,
            weights={JudgeCriterion.ORALITY_REMOVAL: 0.0},
        ) == (0.0, False, False, ())

        # Unmapped criterion falls back to weight=1.0, dividing by total_weight and rounding to 4 decimals
        # (0.5 * 1.0 + 1.0 * 0.1) / (1.0 + 0.1) = 0.6 / 1.1 = 0.5455
        fallback_scores = (
            CriterionScore(JudgeCriterion.INVENTORY_COHERENCE, 0.5, True),
            CriterionScore(JudgeCriterion.AUTHORIAL_VOICE, 1.0, True),
        )
        overall, passed, is_vetoed, reasons = compute_composite_verdict(fallback_scores)
        assert overall == 0.5455
        assert passed is False
        assert is_vetoed is False
        assert reasons == ()

        # Exact default pass_threshold=0.80 boundary passes; default veto_threshold=0.80 accepts 0.80
        boundary_pass = (
            CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.80, True),
            CriterionScore(JudgeCriterion.NER_PRESERVATION, 0.80, True),
            CriterionScore(JudgeCriterion.ORALITY_REMOVAL, 0.80, True),
        )
        assert compute_composite_verdict(boundary_pass) == (0.8, True, False, ())

        # Default veto_threshold=0.80 vetoes 0.79 even when criterion passed=True
        boundary_veto = (CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.79, True),)
        score_v, passed_v, vetoed_v, reasons_v = compute_composite_verdict(boundary_veto)
        assert score_v == 0.79
        assert passed_v is False
        assert vetoed_v is True
        assert reasons_v == (
            "Mechanical Veto on critical criterion 'semantic_faithfulness': score 0.79 < threshold 0.80",
        )

        # Veto criterion with score >= veto_threshold but passed=False still triggers mechanical veto
        failed_flag_veto = (CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.90, False),)
        _, passed_f, vetoed_f, reasons_f = compute_composite_verdict(failed_flag_veto)
        assert passed_f is False
        assert vetoed_f is True
        assert reasons_f == (
            "Mechanical Veto on critical criterion 'semantic_faithfulness': score 0.90 < threshold 0.80",
        )

    def test_create_with_composite_verdict_forwards_metadata_and_thresholds(self) -> None:
        assert resolve_stage_scoring_policy("unknown_stage") == (
            DEFAULT_FLUID_PROSE_WEIGHTS,
            DEFAULT_MECHANICAL_VETO_CRITERIA,
        )

        scores = (
            CriterionScore(JudgeCriterion.SEMANTIC_FAITHFULNESS, 0.90, True),
            CriterionScore(JudgeCriterion.NER_PRESERVATION, 0.90, True),
        )

        default_eval = JudgeEvaluation.create_with_composite_verdict(
            target_stage="fluid_prose",
            criteria_scores=scores,
            provider="gemini",
        )
        assert default_eval.target_stage == "fluid_prose"
        assert default_eval.provider == "gemini"
        assert default_eval.latency_ms == 0.0
        assert default_eval.trace_id is None
        assert default_eval.passed is True

        pass_threshold_failed = JudgeEvaluation.create_with_composite_verdict(
            target_stage="fluid_prose",
            criteria_scores=scores,
            provider="ollama",
            pass_threshold=0.95,
            veto_threshold=0.80,
            latency_ms=12.5,
            trace_id="trace_custom_99",
        )
        assert pass_threshold_failed.target_stage == "fluid_prose"
        assert pass_threshold_failed.provider == "ollama"
        assert pass_threshold_failed.latency_ms == 12.5
        assert pass_threshold_failed.trace_id == "trace_custom_99"
        assert pass_threshold_failed.is_vetoed is False
        assert pass_threshold_failed.passed is False

        veto_threshold_failed = JudgeEvaluation.create_with_composite_verdict(
            target_stage="fluid_prose",
            criteria_scores=scores,
            provider="gemini",
            pass_threshold=0.80,
            veto_threshold=0.95,
        )
        assert veto_threshold_failed.is_vetoed is True
        assert veto_threshold_failed.passed is False

    def test_extract_critique_veto_header_and_multiple_reasons_formatting(self) -> None:
        # is_vetoed=True with empty veto_reasons must not emit empty veto prefix
        no_reasons_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.7,
            criteria_scores=(),
            provider="gemini",
            is_vetoed=True,
            veto_reasons=(),
        )
        assert no_reasons_eval.extract_critique() == "Quality threshold not met."

        # is_vetoed=False with non-empty veto_reasons must not emit veto prefix
        not_vetoed_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.7,
            criteria_scores=(),
            provider="gemini",
            is_vetoed=False,
            veto_reasons=("stale reason",),
        )
        assert not_vetoed_eval.extract_critique() == "Quality threshold not met."

        # Multiple veto reasons join with '; ' under exact header
        multi_veto_eval = JudgeEvaluation(
            target_stage="fluid_prose",
            passed=False,
            overall_score=0.5,
            criteria_scores=(
                CriterionScore(
                    criterion=JudgeCriterion.NER_PRESERVATION,
                    score=0.5,
                    passed=False,
                    reasoning="Missing name",
                ),
            ),
            provider="gemini",
            is_vetoed=True,
            veto_reasons=("Veto A", "Veto B"),
        )
        assert multi_veto_eval.extract_critique() == (
            "[CRITICAL MECHANICAL VETO]: Veto A; Veto B\n- ner_preservation: Missing name"
        )
