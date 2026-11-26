"""Resilient criterion score parser and schema definitions for LLM Judges.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - Anti-Corruption Layer (ACL): Shields the domain Quality Value Objects from diverse LLM JSON shapes.
"""

from __future__ import annotations

import re
from typing import Any, Final

import structlog
from pydantic import BaseModel, Field

from cresmo.domain.value_objects import CriterionScore, JudgeCriterion

logger = structlog.get_logger(__name__)

_MARKDOWN_JSON_FENCE_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```")
_SCORE_MIN_BOUND: Final[float] = 0.0
_SCORE_MAX_BOUND: Final[float] = 1.0
_KEY_CRITERION: Final[str] = "criterion"
_KEY_SCORE: Final[str] = "score"
_KEY_RAW: Final[str] = "raw"
_KEY_PASSED: Final[str] = "passed"
_KEY_REASONING: Final[str] = "reasoning"
_CRITERION_ALIAS_KEYS: Final[tuple[str, ...]] = (
    _KEY_CRITERION,
    "name",
    "criterion_name",
    "id",
    "criterion_id",
)


def clean_json_markdown(text: str) -> str:
    """Strip markdown code fence wrappers from raw JSON response."""
    cleaned = text.strip()
    match = _MARKDOWN_JSON_FENCE_PATTERN.search(cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


class JudgeCriterionOutputSchema(BaseModel):
    """Schema for individual criterion evaluation output."""

    criterion: str = Field(description="Canonical identifier of the evaluated criterion.")
    score: float = Field(ge=0.0, le=1.0, description="Normalized score in [0.0, 1.0].")
    passed: bool = Field(description="Boolean verdict whether this criterion passed threshold.")
    reasoning: str = Field(default="", description="Fact-checked explanation or critique.")


class JudgeResponseOutputSchema(BaseModel):
    """Schema for root LLM judge response output."""

    criteria: list[JudgeCriterionOutputSchema] = Field(
        default_factory=list,
        description="Collection of evaluated individual criteria.",
    )
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0)
    passed: bool = Field(default=False)


def parse_criteria_scores(
    raw_criteria: Any,
    pass_threshold: float,
    logger_instance: Any = None,
) -> list[CriterionScore]:
    """Parse raw LLM criteria payload into strongly typed CriterionScore value objects.

    This function acts as an Anti-Corruption Layer (ACL), gracefully handling structural
    and key variations across different LLM families (e.g. Gemini, Ollama, Qwen):
    1. Supports list of dicts: `[{"criterion": "...", "score": 0.9}]`
    2. Supports key aliases: `criterion`, `name`, `criterion_name`, `id`, `criterion_id`.
    3. Supports dict representations: `{"epistemic_grounding_segregation": {"score": 0.9, ...}}`.
    4. Supports single-key criterion objects: `[{"epistemic_grounding_segregation": {"score": 0.9}}]`.
    5. Safely skips non-criterion/meta objects while logging raw payload context.

    Args:
        raw_criteria: Raw JSON structure extracted from the model response.
        pass_threshold: Minimum score threshold required to pass.
        logger_instance: Optional logger instance for debug telemetry.

    Returns:
        List of strongly typed CriterionScore domain objects.
    """
    log = logger_instance or logger

    items: list[Any] = []
    if isinstance(raw_criteria, dict):
        for k, v in raw_criteria.items():
            if isinstance(v, dict):
                items.append({_KEY_CRITERION: k, **v})
            elif isinstance(v, (int, float)):
                items.append({_KEY_CRITERION: k, _KEY_SCORE: float(v)})
            else:
                items.append({_KEY_CRITERION: k, _KEY_RAW: v})
    elif isinstance(raw_criteria, list):
        items = raw_criteria
    else:
        log.debug("Unexpected criteria type in judge response: %s", type(raw_criteria))
        return []

    criteria_scores_list: list[CriterionScore] = []
    for item in items:
        if not isinstance(item, dict):
            log.debug("Skipping non-dict judge criterion item: %r", item)
            continue

        try:
            # 1. Resolve criterion identifier across common LLM aliases
            crit_name = next(
                (item[alias] for alias in _CRITERION_ALIAS_KEYS if item.get(alias)),
                None,
            )

            # 2. Support single-key dicts where the key itself is the criterion name
            if crit_name is None and len(item) == 1:
                candidate_key, candidate_val = next(iter(item.items()))
                try:
                    JudgeCriterion(str(candidate_key).strip().lower())
                    crit_name = candidate_key
                    if isinstance(candidate_val, dict):
                        item = {_KEY_CRITERION: crit_name, **candidate_val}
                    elif isinstance(candidate_val, (int, float)):
                        item = {_KEY_CRITERION: crit_name, _KEY_SCORE: float(candidate_val)}
                except ValueError:
                    pass

            if crit_name is None:
                raise KeyError(_KEY_CRITERION)

            crit_enum = JudgeCriterion(str(crit_name).strip().lower())
            score_val = max(_SCORE_MIN_BOUND, min(_SCORE_MAX_BOUND, float(item[_KEY_SCORE])))
            passed_val = bool(item.get(_KEY_PASSED, score_val >= pass_threshold))
            criteria_scores_list.append(
                CriterionScore(
                    criterion=crit_enum,
                    score=score_val,
                    passed=passed_val,
                    reasoning=str(item.get(_KEY_REASONING, "")),
                )
            )
        except (ValueError, KeyError, TypeError) as parse_item_err:
            log.debug(
                "Skipping unparseable judge criterion item: %s | raw_item=%r",
                parse_item_err,
                item,
            )

    return criteria_scores_list


__all__ = [
    "JudgeCriterionOutputSchema",
    "JudgeResponseOutputSchema",
    "clean_json_markdown",
    "parse_criteria_scores",
]
