"""TypeSafe AI (System One Jev) Decision-Model Evaluator Adapter.

Conforms to:
    - ADR-029: Unified LlmJudgePort, Decision-Model Evaluators, and Resilient Multi-Provider Adapters
    - SPEC-012: LLM Judge Evaluators, Multi-Provider Adapters, and Langfuse Telemetry
"""

from __future__ import annotations

import time
from typing import Any

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


class TypeSafeJudgeAdapter(LlmJudgePort):
    """Quality judge adapter utilizing TypeSafe AI (System One Jev) Decision Models."""

    def __init__(
        self,
        http_client: Any | None = None,
        api_key: str = "",
        model: str = "jev-latest",
        base_url: str = "https://api.typesafe.ai/v1",
        timeout_seconds: float = 30.0,
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
        self._base_url = base_url.rstrip("/")
        self._pass_threshold = pass_threshold
        self._client = http_client or httpx.Client(timeout=timeout_seconds)

    def evaluate(self, context: EvaluationContext) -> JudgeEvaluation:
        """Evaluate candidate text against raw text using TypeSafe System One Jev."""
        start_time = time.perf_counter()

        questions_payload: dict[str, Any] = {}
        for criterion in context.required_criteria:
            if criterion == JudgeCriterion.ORALITY_REMOVAL:
                questions_payload[criterion.value] = {
                    "type": "noul",
                    "instructions": (
                        "Are all oralities, verbal crutches, and conversational filler words purged from the candidate text?"
                    ),
                }
            elif criterion == JudgeCriterion.NER_PRESERVATION:
                questions_payload[criterion.value] = {
                    "type": "noul",
                    "instructions": (
                        "Are all proper names, entities, and technical terms accurately preserved and correctly spelled?"
                    ),
                }
            elif criterion == JudgeCriterion.STRUCTURAL_COMPLIANCE:
                questions_payload[criterion.value] = {
                    "type": "noul",
                    "instructions": (
                        "Is the candidate text continuous Markdown prose without forbidden tables or stray sections?"
                    ),
                }
            elif criterion == JudgeCriterion.SEMANTIC_FAITHFULNESS:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "How faithfully does the candidate text represent the facts and arguments of the source text?"
                    ),
                    "criteria": [
                        "significant distortions or fabrications",
                        "minor discrepancies or omissions",
                        "completely faithful and grounded",
                    ],
                }
            elif criterion == JudgeCriterion.EPISTEMIC_CRITIQUE:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the candidate text appropriately qualify factual errors or bias with in-line narrative attribution, and identify conceptual gaps?"
                    ),
                    "criteria": [
                        "uncritically adopts blatant falsehoods or introduces model errors",
                        "partially addresses inaccuracies",
                        "rigorously demarcates errors and accurately maps gaps",
                    ],
                }
            elif criterion == JudgeCriterion.AUTHORIAL_VOICE:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the candidate text embody the Detective Narrator voice with second-order causality and zero binary antitheses?"
                    ),
                    "criteria": [
                        "superficial summary or moralistic commentary",
                        "moderately analytical voice with minor lapses",
                        "exemplary analytical detective voice with zero antitheses",
                    ],
                }
            elif criterion == JudgeCriterion.INVENTORY_COHERENCE:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": "How coherent, complete, and well-structured is the atomic entity inventory?",
                    "criteria": [
                        "incomplete or incoherent",
                        "partially coherent with gaps",
                        "fully coherent and complete",
                    ],
                }
            elif criterion == JudgeCriterion.INDEX_SYNTHESIS_QUALITY:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": "How precise, dense, and paratactic is the raw catalog index entry?",
                    "criteria": [
                        "insufficient density or accuracy",
                        "acceptable density",
                        "exemplary paratactic synthesis",
                    ],
                }
            elif criterion == JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Are all facts, dates, and primary sources grounded with strict segregation between First-Order Facts and Interpretive Models?"
                    ),
                    "criteria": [
                        "contains fabricated facts, anachronisms, or unattributed interpretive claims",
                        "mostly grounded with minor epistemic lapses",
                        "completely grounded in factual truth with strict fact/model segregation",
                    ],
                }
            elif criterion == JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text provide non-circular definitions with boundary conditions and complete A -> B -> C intermediate mechanisms?"
                    ),
                    "criteria": [
                        "circular definitions or unexplained causal leaps",
                        "partially articulated mechanisms with minor gaps",
                        "complete ontological boundaries and step-by-step intermediate gearing",
                    ],
                }
            elif criterion == JudgeCriterion.BRAUDELIAN_STRATIFICATION:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text stratify causality across structural invariants, conjunctural buildup, and immediate triggers?"
                    ),
                    "criteria": [
                        "flattens causation onto surface events without temporal depth",
                        "partially stratified across some temporal scales",
                        "exemplary 3-tier Braudelian causal stratification",
                    ],
                }
            elif criterion == JudgeCriterion.GENEALOGY_HIDDEN_AGENCY:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text track precursors, documented relational networks, and material Cui Bono incentives without inventing conspiracies?"
                    ),
                    "criteria": [
                        "naive lone-genius or spontaneous-agency framing",
                        "partial precursor or network context",
                        "rigorous genealogy, documented networks, and hypothesis-framed payoffs",
                    ],
                }
            elif criterion == JudgeCriterion.COMPETING_HYPOTHESES:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text stress-test edge cases and evaluate mutually exclusive competing hypotheses via Popperian falsification?"
                    ),
                    "criteria": [
                        "dogmatic single-hypothesis confirmation lacking counter-arguments",
                        "mentions alternatives without diagnostic refutation",
                        "rigorous ACH evaluation ranking surviving hypotheses by refutation",
                    ],
                }
            elif criterion == JudgeCriterion.EXTRA_INFO_GRANULARITY:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Is ### Extra Info numbered, non-tautological, and populated with high-granularity specifics migrated from the main body?"
                    ),
                    "criteria": [
                        "missing, empty, bulleted, or tautological",
                        "acceptable granularity with minor omissions",
                        "rich numbered high-granularity specifics protecting core narrative flow",
                    ],
                }
            elif criterion == JudgeCriterion.LINEAR_STYLE_NATURALISM:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text maintain linear progression, formal connectives, Detective Narrator naturalism, and zero style-guide bans?"
                    ),
                    "criteria": [
                        "meta-discourse, links, em-dashes, antitheses, or restricted vocabulary present",
                        "mostly linear and naturalistic with minor stylistic lapses",
                        "exemplary linear prose strictly compliant with cresmo-style-guide",
                    ],
                }
            elif criterion == JudgeCriterion.LONGUE_DUREE_STRATIFICATION:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text ground foreground events in multi-secular material constraints, cyclical institutions, and backward historical lineages?"
                    ),
                    "criteria": [
                        "presentist event-level explanation lacking multi-secular depth",
                        "partial institutional history with weak material or cyclical invariants",
                        "deep three-tier diachronic stratification and backward historical tracing",
                    ],
                }
            elif criterion == JudgeCriterion.HISTORICAL_PALIMPSEST:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text expose inherited administrative, fiscal, legal, and cognitive strata persisting beneath newer institutional forms?"
                    ),
                    "criteria": [
                        "treats newer regimes or concepts as clean-slate inventions",
                        "notes isolated historical precursors without systemic continuity",
                        "thorough excavation of institutional survivals and asynchronous durations",
                    ],
                }
            elif criterion == JudgeCriterion.EMPIRICAL_HISTORICAL_GROUNDING:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Are historical dates (big-endian YYYY/YYYY-MM-DD), primary-source treaties, institutional names, and quantitative magnitudes accurate without fabrication?"
                    ),
                    "criteria": [
                        "contains anachronisms, fabricated events, or contradictions of the source core",
                        "broadly accurate with sparse concrete dates or magnitudes",
                        "rigorous verifiable historical grounding and faithful empirical continuity",
                    ],
                }
            elif criterion == JudgeCriterion.IMPLICIT_FRAMING_STYLE:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the prose express structural depth implicitly without naming analytical frameworks while honoring cresmo-style-guide linearity and bans?"
                    ),
                    "criteria": [
                        "explicit methodological labels, meta-discourse, em-dashes, lists, or banned verbs present",
                        "implicit framing mostly preserved with minor stylistic lapses",
                        "seamless implicit analytical narrative adhering strictly to cresmo-style-guide",
                    ],
                }
            elif criterion == JudgeCriterion.SYNCHRONIC_CONNECTIVITY:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text map simultaneous hemispheric trade flows, monetary/bullion circuits, and shared planetary shocks linked across regions?"
                    ),
                    "criteria": [
                        "treats events purely domestically ignoring synchronous global networks",
                        "mentions partial regional interactions without material transmission mechanisms",
                        "rigorous contemporaneous cross-regional connectivity and planetary context",
                    ],
                }
            elif criterion == JudgeCriterion.COMPARATIVE_PARALLELISM:
                questions_payload[criterion.value] = {
                    "type": "score",
                    "instructions": (
                        "Does the text compare independent societies undergoing convergent structural pressures without fabricating false diffusion?"
                    ),
                    "criteria": [
                        "insular single-society narrative without comparative cross-sections",
                        "superficial comparison conflating independent convergence with diffusion",
                        "disciplined comparative civilizational analogies respecting independent agency",
                    ],
                }

        state_payload = {
            "source_raw": context.raw_text,
            "candidate_output": context.candidate_text,
            "stage": context.stage_name,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self._model,
            "state": state_payload,
            "questions": questions_payload,
        }

        try:
            resp = self._client.post(
                f"{self._base_url}/system-one",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("TypeSafeJudgeAdapter evaluation request failed: %s", exc)
            raise

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        nouls = data.get("nouls", {})
        scores = data.get("scores", {})

        criteria_scores_list: list[CriterionScore] = []
        for criterion in context.required_criteria:
            c_name = criterion.value
            score_val = 0.0
            passed_val = False

            if c_name in nouls:
                noul_item = nouls[c_name]
                score_val = float(noul_item.get("noul", 0.0))
                passed_val = score_val >= self._pass_threshold
            elif c_name in scores:
                score_item = scores[c_name]
                score_val = float(score_item.get("score", 0.0))
                passed_val = score_val >= self._pass_threshold
            else:
                score_val = 0.5
                passed_val = False

            score_val = max(0.0, min(1.0, score_val))

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
            provider="typesafe",
            pass_threshold=self._pass_threshold,
            latency_ms=latency_ms,
            trace_id=context.trace_id,
        )

__all__ = [
    "TypeSafeJudgeAdapter",
]
