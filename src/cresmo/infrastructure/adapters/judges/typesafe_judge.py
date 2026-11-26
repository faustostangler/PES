"""TypeSafe AI (System One Jev) Decision-Model Evaluator Adapter.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import time
from typing import Any, Final

import httpx
import structlog

from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.value_objects.quality import (
    CriterionScore,
    EvaluationContext,
    JudgeCriterion,
    JudgeEvaluation,
)
from cresmo.infrastructure.config import DEFAULT_JUDGE_PASS_THRESHOLD

logger = structlog.get_logger(__name__)

DEFAULT_TYPESAFE_MODEL: Final[str] = "jev-latest"
DEFAULT_TYPESAFE_BASE_URL: Final[str] = "https://api.typesafe.ai/v1"
DEFAULT_TYPESAFE_TIMEOUT_SECONDS: Final[float] = 30.0
TYPESAFE_PROVIDER_NAME: Final[str] = "typesafe"
_URL_TRAILING_SLASH: Final[str] = "/"
_TYPESAFE_SYSTEM_ONE_PATH: Final[str] = "/system-one"
_HEADER_AUTHORIZATION: Final[str] = "Authorization"
_BEARER_TOKEN_PREFIX: Final[str] = "Bearer "
_HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
_CONTENT_TYPE_JSON: Final[str] = "application/json"
_MS_PER_SECOND: Final[float] = 1000.0
_SCORE_MIN_BOUND: Final[float] = 0.0
_SCORE_MAX_BOUND: Final[float] = 1.0
_DEFAULT_MISSING_SCORE: Final[float] = 0.5
_KEY_NOULS: Final[str] = "nouls"
_KEY_NOUL: Final[str] = "noul"
_KEY_SCORES: Final[str] = "scores"
_KEY_SCORE: Final[str] = "score"
_KEY_SOURCE_RAW: Final[str] = "source_raw"
_KEY_CANDIDATE_OUTPUT: Final[str] = "candidate_output"
_KEY_STAGE: Final[str] = "stage"
_KEY_MODEL: Final[str] = "model"
_KEY_STATE: Final[str] = "state"
_KEY_QUESTIONS: Final[str] = "questions"
_QUESTION_TYPE_NOUL: Final[str] = "noul"
_QUESTION_TYPE_SCORE: Final[str] = "score"

_TYPESAFE_QUESTION_SPECS: Final[dict[JudgeCriterion, dict[str, Any]]] = {
    JudgeCriterion.ORALITY_REMOVAL: {
        "type": _QUESTION_TYPE_NOUL,
        "instructions": (
            "Are all oralities, verbal crutches, and conversational filler words purged from the candidate text?"
        ),
    },
    JudgeCriterion.NER_PRESERVATION: {
        "type": _QUESTION_TYPE_NOUL,
        "instructions": (
            "Are all proper names, entities, and technical terms accurately preserved and correctly spelled?"
        ),
    },
    JudgeCriterion.STRUCTURAL_COMPLIANCE: {
        "type": _QUESTION_TYPE_NOUL,
        "instructions": (
            "Is the candidate text continuous Markdown prose without forbidden tables or stray sections?"
        ),
    },
    JudgeCriterion.SEMANTIC_FAITHFULNESS: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "How faithfully does the candidate text represent the facts and arguments of the source text?"
        ),
        "criteria": [
            "significant distortions or fabrications",
            "minor discrepancies or omissions",
            "completely faithful and grounded",
        ],
    },
    JudgeCriterion.EPISTEMIC_CRITIQUE: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the candidate text appropriately qualify factual errors or bias with in-line narrative attribution, and identify conceptual gaps?"
        ),
        "criteria": [
            "uncritically adopts blatant falsehoods or introduces model errors",
            "partially addresses inaccuracies",
            "rigorously demarcates errors and accurately maps gaps",
        ],
    },
    JudgeCriterion.AUTHORIAL_VOICE: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the candidate text embody the Detective Narrator voice with second-order causality and zero binary antitheses?"
        ),
        "criteria": [
            "superficial summary or moralistic commentary",
            "moderately analytical voice with minor lapses",
            "exemplary analytical detective voice with zero antitheses",
        ],
    },
    JudgeCriterion.INVENTORY_COHERENCE: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": "How coherent, complete, and well-structured is the atomic entity inventory?",
        "criteria": [
            "incomplete or incoherent",
            "partially coherent with gaps",
            "fully coherent and complete",
        ],
    },
    JudgeCriterion.INDEX_SYNTHESIS_QUALITY: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": "How precise, dense, and paratactic is the raw catalog index entry?",
        "criteria": [
            "insufficient density or accuracy",
            "acceptable density",
            "exemplary paratactic synthesis",
        ],
    },
    JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Are all facts, dates, and primary sources grounded with strict segregation between First-Order Facts and Interpretive Models?"
        ),
        "criteria": [
            "contains fabricated facts, anachronisms, or unattributed interpretive claims",
            "mostly grounded with minor epistemic lapses",
            "completely grounded in factual truth with strict fact/model segregation",
        ],
    },
    JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text provide non-circular definitions with boundary conditions and complete A -> B -> C intermediate mechanisms?"
        ),
        "criteria": [
            "circular definitions or unexplained causal leaps",
            "partially articulated mechanisms with minor gaps",
            "complete ontological boundaries and step-by-step intermediate gearing",
        ],
    },
    JudgeCriterion.BRAUDELIAN_STRATIFICATION: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text stratify causality across structural invariants, conjunctural buildup, and immediate triggers?"
        ),
        "criteria": [
            "flattens causation onto surface events without temporal depth",
            "partially stratified across some temporal scales",
            "exemplary 3-tier Braudelian causal stratification",
        ],
    },
    JudgeCriterion.GENEALOGY_HIDDEN_AGENCY: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text track precursors, documented relational networks, and material Cui Bono incentives without inventing conspiracies?"
        ),
        "criteria": [
            "naive lone-genius or spontaneous-agency framing",
            "partial precursor or network context",
            "rigorous genealogy, documented networks, and hypothesis-framed payoffs",
        ],
    },
    JudgeCriterion.COMPETING_HYPOTHESES: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text stress-test edge cases and evaluate mutually exclusive competing hypotheses via Popperian falsification?"
        ),
        "criteria": [
            "dogmatic single-hypothesis confirmation lacking counter-arguments",
            "mentions alternatives without diagnostic refutation",
            "rigorous ACH evaluation ranking surviving hypotheses by refutation",
        ],
    },
    JudgeCriterion.EXTRA_INFO_GRANULARITY: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Is ### Extra Info numbered, non-tautological, and populated with high-granularity specifics migrated from the main body?"
        ),
        "criteria": [
            "missing, empty, bulleted, or tautological",
            "acceptable granularity with minor omissions",
            "rich numbered high-granularity specifics protecting core narrative flow",
        ],
    },
    JudgeCriterion.LINEAR_STYLE_NATURALISM: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text maintain linear progression, formal connectives, Detective Narrator naturalism, and zero style-guide bans?"
        ),
        "criteria": [
            "meta-discourse, links, em-dashes, antitheses, or restricted vocabulary present",
            "mostly linear and naturalistic with minor stylistic lapses",
            "exemplary linear prose strictly compliant with cresmo-style-guide",
        ],
    },
    JudgeCriterion.LONGUE_DUREE_STRATIFICATION: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text ground foreground events in multi-secular material constraints, cyclical institutions, and backward historical lineages?"
        ),
        "criteria": [
            "presentist event-level explanation lacking multi-secular depth",
            "partial institutional history with weak material or cyclical invariants",
            "deep three-tier diachronic stratification and backward historical tracing",
        ],
    },
    JudgeCriterion.HISTORICAL_PALIMPSEST: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text expose inherited administrative, fiscal, legal, and cognitive strata persisting beneath newer institutional forms?"
        ),
        "criteria": [
            "treats newer regimes or concepts as clean-slate inventions",
            "notes isolated historical precursors without systemic continuity",
            "thorough excavation of institutional survivals and asynchronous durations",
        ],
    },
    JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Are historical dates (big-endian YYYY/YYYY-MM-DD), primary-source treaties, institutional names, and quantitative magnitudes accurate without fabrication?"
        ),
        "criteria": [
            "contains anachronisms, fabricated events, or contradictions of the source core",
            "broadly accurate with sparse concrete dates or magnitudes",
            "rigorous verifiable historical grounding and faithful empirical continuity",
        ],
    },
    JudgeCriterion.IMPLICIT_FRAMING_STYLE: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the prose express structural depth implicitly without naming analytical frameworks while honoring cresmo-style-guide linearity and bans?"
        ),
        "criteria": [
            "explicit methodological labels, meta-discourse, em-dashes, lists, or banned verbs present",
            "implicit framing mostly preserved with minor stylistic lapses",
            "seamless implicit analytical narrative adhering strictly to cresmo-style-guide",
        ],
    },
    JudgeCriterion.SYNCHRONIC_CONNECTIVITY: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text map simultaneous hemispheric trade flows, monetary/bullion circuits, and shared planetary shocks linked across regions?"
        ),
        "criteria": [
            "treats events purely domestically ignoring synchronous global networks",
            "mentions partial regional interactions without material transmission mechanisms",
            "rigorous contemporaneous cross-regional connectivity and planetary context",
        ],
    },
    JudgeCriterion.COMPARATIVE_PARALLELISM: {
        "type": _QUESTION_TYPE_SCORE,
        "instructions": (
            "Does the text compare independent societies undergoing convergent structural pressures without fabricating false diffusion?"
        ),
        "criteria": [
            "insular single-society narrative without comparative cross-sections",
            "superficial comparison conflating independent convergence with diffusion",
            "disciplined comparative civilizational analogies respecting independent agency",
        ],
    },
}


class TypeSafeJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing TypeSafe AI (System One Jev) Decision Models."""

    def __init__(
        self,
        http_client: Any | None = None,
        api_key: str = "",
        model: str = DEFAULT_TYPESAFE_MODEL,
        base_url: str = DEFAULT_TYPESAFE_BASE_URL,
        timeout_seconds: float = DEFAULT_TYPESAFE_TIMEOUT_SECONDS,
        pass_threshold: float = DEFAULT_JUDGE_PASS_THRESHOLD,
    ) -> None:
        """Initialize TypeSafe AI judge adapter.

        Args:
            http_client: HTTP client instance (defaults to httpx.Client).
            api_key: TypeSafe AI authentication bearer token.
            model: Model identifier (e.g. 'jev-latest').
            base_url: API endpoint URL.
            timeout_seconds: HTTP timeout duration.
            pass_threshold: Minimum score threshold for passing criteria and overall evaluation.
        """
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip(_URL_TRAILING_SLASH)
        self._pass_threshold = pass_threshold
        self._client = http_client or httpx.Client(timeout=timeout_seconds)

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text using TypeSafe System One Jev."""
        start_time = time.perf_counter()

        questions_payload: dict[str, Any] = {
            criterion.value: _TYPESAFE_QUESTION_SPECS[criterion]
            for criterion in context.required_criteria
            if criterion in _TYPESAFE_QUESTION_SPECS
        }

        state_payload = {
            _KEY_SOURCE_RAW: context.raw_text,
            _KEY_CANDIDATE_OUTPUT: context.candidate_text,
            _KEY_STAGE: context.stage_name,
        }

        headers = {
            _HEADER_AUTHORIZATION: f"{_BEARER_TOKEN_PREFIX}{self._api_key}",
            _HEADER_CONTENT_TYPE: _CONTENT_TYPE_JSON,
        }
        body = {
            _KEY_MODEL: self._model,
            _KEY_STATE: state_payload,
            _KEY_QUESTIONS: questions_payload,
        }

        try:
            resp = self._client.post(
                f"{self._base_url}{_TYPESAFE_SYSTEM_ONE_PATH}",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("TypeSafeJudgeAdapter evaluation request failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * _MS_PER_SECOND

        nouls = data.get(_KEY_NOULS, {})
        scores = data.get(_KEY_SCORES, {})

        criteria_scores_list: list[CriterionScore] = []
        for criterion in context.required_criteria:
            c_name = criterion.value
            score_val = _SCORE_MIN_BOUND
            passed_val = False

            if c_name in nouls:
                noul_item = nouls[c_name]
                score_val = float(noul_item.get(_KEY_NOUL, _SCORE_MIN_BOUND))
                passed_val = score_val >= self._pass_threshold
            elif c_name in scores:
                score_item = scores[c_name]
                score_val = float(score_item.get(_KEY_SCORE, _SCORE_MIN_BOUND))
                passed_val = score_val >= self._pass_threshold
            else:
                score_val = _DEFAULT_MISSING_SCORE
                passed_val = False

            score_val = max(_SCORE_MIN_BOUND, min(_SCORE_MAX_BOUND, score_val))

            criteria_scores_list.append(
                CriterionScore(
                    criterion=criterion,
                    score=score_val,
                    passed=passed_val,
                    reasoning=f"System One Jev evaluation for {c_name}",
                )
            )

        return JudgeEvaluation.create_with_composite_verdict(
            target_stage=context.stage_name,
            criteria_scores=criteria_scores_list,
            provider=TYPESAFE_PROVIDER_NAME,
            pass_threshold=self._pass_threshold,
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

__all__ = [
    "TypeSafeJudgeAdapter",
]
