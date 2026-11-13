"""Unit tests for criterion parser Anti-Corruption Layer (ACL).

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

from cresmo.domain.value_objects import JudgeCriterion
from cresmo.infrastructure.adapters.judges.criterion_parser import (
    JudgeCriterionOutputSchema,
    JudgeResponseOutputSchema,
    parse_criteria_scores,
)


class TestCriterionParser:
    """Test suite verifying resilient parsing of LLM criteria responses."""

    def test_parse_standard_criteria_list(self) -> None:
        raw = [
            {
                "criterion": "epistemic_grounding_segregation",
                "score": 0.95,
                "passed": True,
                "reasoning": "Strictly grounded.",
            },
            {
                "criterion": "conceptual_mechanical_decomposition",
                "score": 0.88,
                "passed": True,
                "reasoning": "Deep analysis.",
            },
        ]
        results = parse_criteria_scores(raw, pass_threshold=0.80)
        assert len(results) == 2
        assert results[0].criterion == JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION
        assert results[0].score == 0.95
        assert results[0].passed is True
        assert results[0].reasoning == "Strictly grounded."
        assert results[1].criterion == JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION
        assert results[1].score == 0.88

    def test_parse_criteria_with_key_aliases(self) -> None:
        raw = [
            {"name": "epistemic_grounding_segregation", "score": 0.92, "reasoning": "ok via name"},
            {"criterion_name": "linear_style_naturalism", "score": 0.85},
            {"id": "extra_info_granularity", "score": 0.90},
            {"criterion_id": "braudelian_stratification", "score": 0.87},
        ]
        results = parse_criteria_scores(raw, pass_threshold=0.80)
        assert len(results) == 4
        assert results[0].criterion == JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION
        assert results[1].criterion == JudgeCriterion.LINEAR_STYLE_NATURALISM
        assert results[2].criterion == JudgeCriterion.EXTRA_INFO_GRANULARITY
        assert results[3].criterion == JudgeCriterion.BRAUDELIAN_STRATIFICATION

    def test_parse_criteria_single_key_dict(self) -> None:
        raw = [
            {
                "epistemic_grounding_segregation": {
                    "score": 0.93,
                    "passed": True,
                    "reasoning": "Single key dictionary entry",
                }
            },
            {"linear_style_naturalism": 0.89},
        ]
        results = parse_criteria_scores(raw, pass_threshold=0.80)
        assert len(results) == 2
        assert results[0].criterion == JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION
        assert results[0].score == 0.93
        assert results[0].reasoning == "Single key dictionary entry"
        assert results[1].criterion == JudgeCriterion.LINEAR_STYLE_NATURALISM
        assert results[1].score == 0.89

    def test_parse_criteria_when_root_is_dict(self) -> None:
        raw = {
            "epistemic_grounding_segregation": {
                "score": 0.94,
                "passed": True,
                "reasoning": "Root dict format",
            },
            "conceptual_mechanical_decomposition": 0.91,
        }
        results = parse_criteria_scores(raw, pass_threshold=0.80)
        assert len(results) == 2
        assert results[0].criterion == JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION
        assert results[0].score == 0.94
        assert results[1].criterion == JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION
        assert results[1].score == 0.91

    def test_skips_unparseable_summary_item_gracefully(self) -> None:
        mock_logger = MagicMock(spec=logging.Logger)
        raw = [
            {
                "criterion": "epistemic_grounding_segregation",
                "score": 0.95,
                "passed": True,
            },
            {
                "summary": "Overall execution was high quality",
                "overall_score": 0.95,
            },
            "completely_invalid_string",
            None,
        ]
        results = parse_criteria_scores(raw, pass_threshold=0.80, logger_instance=mock_logger)
        assert len(results) == 1
        assert results[0].criterion == JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION
        assert results[0].score == 0.95
        mock_logger.debug.assert_called()

    def test_clamps_score_and_handles_case_insensitivity(self) -> None:
        raw = [
            {"criterion": "EPISTEMIC_GROUNDING_SEGREGATION", "score": 1.5},
            {"criterion": "linear_style_naturalism", "score": -0.5},
        ]
        results = parse_criteria_scores(raw, pass_threshold=0.80)
        assert len(results) == 2
        assert results[0].criterion == JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION
        assert results[0].score == 1.0
        assert results[1].criterion == JudgeCriterion.LINEAR_STYLE_NATURALISM
        assert results[1].score == 0.0

    def test_schema_validates_canonical_output(self) -> None:
        output = JudgeResponseOutputSchema(
            criteria=[
                JudgeCriterionOutputSchema(
                    criterion="epistemic_grounding_segregation",
                    score=0.95,
                    passed=True,
                    reasoning="Anchored",
                )
            ],
            overall_score=0.95,
            passed=True,
        )
        assert output.passed is True
        assert len(output.criteria) == 1
        assert output.criteria[0].criterion == "epistemic_grounding_segregation"
