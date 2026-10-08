"""Exhaustive Unit Tests for Quality Value Objects (ADR-029, SPEC-012).

Tests every boundary, invariant, string formatting, and mutant branch in:
src/cresmo/domain/value_objects/quality.py
"""

from __future__ import annotations

from typing import Any
import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.quality import (
    CandidateText,
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
    StageEvaluationSpec,
    TypedVerdict,
    VerdictType,
)


class TestJudgeCriterionAndVerdictType:
    """Test enums and string values."""

    def test_criterion_enum_values(self) -> None:
        assert JudgeCriterion.ORALITY_REMOVAL.value == "orality_removal"
        assert JudgeCriterion.SEMANTIC_FAITHFULNESS.value == "semantic_faithfulness"
        assert JudgeCriterion.NER_PRESERVATION.value == "ner_preservation"
        assert JudgeCriterion.STRUCTURAL_COMPLIANCE.value == "structural_compliance"
        assert JudgeCriterion.INVENTORY_COHERENCE.value == "inventory_coherence"
        assert JudgeCriterion.INDEX_SYNTHESIS_QUALITY.value == "index_synthesis_quality"

    def test_verdict_type_enum_values(self) -> None:
        assert VerdictType.NOUL.value == "noul"
        assert VerdictType.CHOICE.value == "choice"
        assert VerdictType.SCORE.value == "score"


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


class TestTypedVerdict:
    """Invariants and behaviors of TypedVerdict."""

    def test_valid_typed_verdict(self) -> None:
        tv = TypedVerdict(
            criterion=JudgeCriterion.ORALITY_REMOVAL,
            verdict_type=VerdictType.SCORE,
            passed=True,
            score=0.92,
            choice_value="accepted",
            confidence=0.95,
            reasoning="Passed without speech artifacts.",
            improvement_suggestion="None needed",
        )
        assert tv.criterion == JudgeCriterion.ORALITY_REMOVAL
        assert tv.verdict_type == VerdictType.SCORE
        assert tv.passed is True
        assert tv.score == 0.92
        assert tv.choice_value == "accepted"
        assert tv.confidence == 0.95
        assert tv.reasoning == "Passed without speech artifacts."
        assert tv.improvement_suggestion == "None needed"

    def test_typed_verdict_defaults(self) -> None:
        tv = TypedVerdict(
            criterion=JudgeCriterion.NER_PRESERVATION,
            verdict_type=VerdictType.NOUL,
            passed=False,
            score=0.0,
        )
        assert tv.choice_value is None
        assert tv.confidence is None
        assert tv.reasoning == ""
        assert tv.improvement_suggestion == ""

    @pytest.mark.parametrize("boundary_score", [0.0, 1.0])
    def test_score_exact_boundaries(self, boundary_score: float) -> None:
        tv = TypedVerdict(
            criterion=JudgeCriterion.NER_PRESERVATION,
            verdict_type=VerdictType.SCORE,
            passed=True,
            score=boundary_score,
        )
        assert tv.score == boundary_score

    @pytest.mark.parametrize("invalid_score", [-0.01, 1.01, -1.0, 2.0])
    def test_invalid_score_raises_value_error(self, invalid_score: float) -> None:
        with pytest.raises(
            ValueError,
            match=rf"^Score must be between 0\.0 and 1\.0, got: {invalid_score}$",
        ):
            TypedVerdict(
                criterion=JudgeCriterion.NER_PRESERVATION,
                verdict_type=VerdictType.SCORE,
                passed=False,
                score=invalid_score,
            )

    @pytest.mark.parametrize("boundary_confidence", [0.0, 1.0])
    def test_confidence_exact_boundaries(self, boundary_confidence: float) -> None:
        tv = TypedVerdict(
            criterion=JudgeCriterion.NER_PRESERVATION,
            verdict_type=VerdictType.SCORE,
            passed=True,
            score=0.5,
            confidence=boundary_confidence,
        )
        assert tv.confidence == boundary_confidence

    @pytest.mark.parametrize("invalid_confidence", [-0.01, 1.01, -0.5, 1.5])
    def test_invalid_confidence_raises_value_error(self, invalid_confidence: float) -> None:
        with pytest.raises(
            ValueError,
            match=rf"^Confidence must be between 0\.0 and 1\.0 if provided, got: {invalid_confidence}$",
        ):
            TypedVerdict(
                criterion=JudgeCriterion.NER_PRESERVATION,
                verdict_type=VerdictType.SCORE,
                passed=False,
                score=0.5,
                confidence=invalid_confidence,
            )


class TestCriterionScore:
    """Invariants and behaviors of CriterionScore."""

    def test_valid_criterion_score(self) -> None:
        cs = CriterionScore(
            criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
            score=0.88,
            passed=True,
            confidence=0.9,
            reasoning="Faithful semantics",
            verdict_type=VerdictType.SCORE,
            improvement_suggestion="Keep it up",
        )
        assert cs.criterion == JudgeCriterion.SEMANTIC_FAITHFULNESS
        assert cs.score == 0.88
        assert cs.passed is True
        assert cs.confidence == 0.9
        assert cs.reasoning == "Faithful semantics"
        assert cs.verdict_type == VerdictType.SCORE
        assert cs.improvement_suggestion == "Keep it up"

    def test_criterion_score_defaults(self) -> None:
        cs = CriterionScore(
            criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
            score=0.5,
            passed=True,
        )
        assert cs.confidence is None
        assert cs.reasoning == ""
        assert cs.verdict_type == VerdictType.SCORE
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

    @pytest.mark.parametrize("boundary_conf", [0.0, 1.0])
    def test_criterion_confidence_boundaries(self, boundary_conf: float) -> None:
        cs = CriterionScore(
            criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
            score=0.5,
            passed=True,
            confidence=boundary_conf,
        )
        assert cs.confidence == boundary_conf

    @pytest.mark.parametrize("invalid_conf", [-0.01, 1.01])
    def test_criterion_confidence_out_of_bounds_raises_value_error(self, invalid_conf: float) -> None:
        with pytest.raises(
            ValueError,
            match=rf"^Confidence must be between 0\.0 and 1\.0 if provided, got: {invalid_conf}$",
        ):
            CriterionScore(
                criterion=JudgeCriterion.SEMANTIC_FAITHFULNESS,
                score=0.5,
                passed=True,
                confidence=invalid_conf,
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
    """Invariants and source text extraction of StageEvaluationSpec."""

    def test_spec_defaults(self) -> None:
        spec = StageEvaluationSpec()
        assert spec.required_criteria == ()
        assert spec.raw_text == ""
        assert spec.metadata == {}
        assert spec.max_attempts == 1
        assert spec.source_extractor is None
        # Default candidate_extractor stringifies
        assert spec.candidate_extractor(123) == "123"

    @pytest.mark.parametrize("invalid_attempts", [0, -1, -5])
    def test_max_attempts_less_than_1_raises_value_error(self, invalid_attempts: int) -> None:
        with pytest.raises(
            ValueError,
            match=rf"^max_attempts must be >= 1, got {invalid_attempts}$",
        ):
            StageEvaluationSpec(max_attempts=invalid_attempts)

    def test_extract_source_text_explicit_raw_text(self) -> None:
        spec = StageEvaluationSpec(raw_text="explicit text")
        assert spec.extract_source_text("arbitrary_source") == "explicit text"

    def test_extract_source_text_with_source_extractor(self) -> None:
        spec = StageEvaluationSpec(source_extractor=lambda s: f"extracted:{s}")
        assert spec.extract_source_text("hello") == "extracted:hello"

    def test_extract_source_text_from_content_body(self) -> None:
        class FakeContent:
            body = "body from content"

        class FakeSource:
            content = FakeContent()

        spec = StageEvaluationSpec()
        assert spec.extract_source_text(FakeSource()) == "body from content"

    def test_extract_source_text_from_direct_body(self) -> None:
        class FakeSource:
            body = "direct body"

        spec = StageEvaluationSpec()
        assert spec.extract_source_text(FakeSource()) == "direct body"

    def test_extract_source_text_fallback_to_str(self) -> None:
        spec = StageEvaluationSpec()
        assert spec.extract_source_text(42) == "42"
