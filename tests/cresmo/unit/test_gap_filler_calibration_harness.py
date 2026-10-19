"""Unit tests for Gap Filler Judge Calibration Harness.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - SPEC-015: Quality Gates and Calibration Framework
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    JudgeCriterion,
    JudgeEvaluation,
)
from cresmo.infrastructure.adapters.gemini_pool import CredentialPoolExhaustedError
from scripts.gap_filler.llm_judge.calibrate import (
    evaluate_single_item,
    run_local_calibration,
)


def test_evaluate_single_item_with_mock_judge() -> None:
    mock_judge = MagicMock(spec=LlmJudgePort)
    mock_judge.evaluate.return_value = JudgeEvaluation(
        target_stage="gap_filler",
        passed=True,
        overall_score=0.95,
        criteria_scores=(
            CriterionScore(
                criterion=JudgeCriterion.FACTUAL_GROUNDING,
                score=0.95,
                passed=True,
                reasoning="Factual details confirmed",
            ),
        ),
        provider="gemini",
    )

    item = {
        "id": "fg_01_pass",
        "input": {
            "raw_text": "Transcrição fluida original",
            "candidate_text": "## Texto Expandido\n\nCorpo em prosa com detalhes.",
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {"criterion": "factual_grounding"},
    }

    result = evaluate_single_item(mock_judge, item)

    assert result.actual == "PASS"
    assert result.expected == "PASS"
    assert result.target_actual == "PASS"
    assert result.target_score == 0.95


def test_run_local_calibration_raises_on_long_credential_pool_cooldown() -> None:
    """Verify run_local_calibration halts fail-fast on long cooldown rather than masking failure."""
    mock_judge = MagicMock(spec=LlmJudgePort)
    mock_judge.evaluate.side_effect = CredentialPoolExhaustedError(
        retry_after_seconds=28070.0,
        message="All 3 Gemini credentials in pool are in cooldown.",
    )

    items = [
        {
            "id": "item1",
            "input": {"raw_text": "raw", "candidate_text": "cand"},
            "expected_output": {"verdict": "PASS"},
        },
        {
            "id": "item2",
            "input": {"raw_text": "raw", "candidate_text": "cand"},
            "expected_output": {"verdict": "PASS"},
        },
    ]

    with pytest.raises(CredentialPoolExhaustedError) as exc_info:
        run_local_calibration(mock_judge, items, delay=0.0, jitter=0.0, max_retry_wait=60.0)

    assert exc_info.value.retry_after_seconds == 28070.0
    # Must have stopped after item 1 without proceeding to item 2
    assert mock_judge.evaluate.call_count == 1
