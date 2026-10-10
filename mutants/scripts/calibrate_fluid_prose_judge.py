#!/usr/bin/env python3
"""Offline Calibration Harness for Fluid Prose LLM Judges.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
    - Langfuse Judge Calibration: .agents/skills/langfuse/references/judge-calibration.md
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cresmo.domain.value_objects.quality import (
    EvaluationContext,
    JudgeCriterion,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("calibrate_judge")

DEFAULT_GOLDEN_SET_PATH = Path("data/golden_sets/fluid_prose_golden_set_42.json")

# Canonical seed dataset items for quick dry-run
SEED_CALIBRATION_DATA: list[dict[str, Any]] = [
    {
        "id": "item_01_pass_clean_narrative",
        "input": {
            "raw_text": (
                "então pessoal hoje a gente vai falar do G. W. F. Hegel, né? "
                "ele pensava que a história caminha por contradições e dialética, tá ligado?"
            ),
            "candidate_text": (
                "## A Dialética e o Movimento Histórico\n\n"
                "Na filosofia de **G. W. F. Hegel**, o desenvolvimento histórico opera através de "
                "contradições dialéticas imanentes. As transformações sociais expressam a superação "
                "de contradições estruturais que reorganizam as instituições políticas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "easy",
            "category": "valid_transformation",
        },
    },
    {
        "id": "item_02_fail_youtube_cta",
        "input": {
            "raw_text": "não esquece de se inscrever no canal e deixar o like se gostou do vídeo.",
            "candidate_text": (
                "## Introdução ao Tema\n\n"
                "O debate envolve teorias econômicas clássicas. "
                "Inscreva-se no canal para acompanhar os próximos episódios."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "easy",
            "expected_anomaly": "youtube_cta_leakage",
        },
    },
    {
        "id": "item_03_fail_mechanical_em_dash",
        "input": {
            "raw_text": "ele tomou uma decisão muito dura ali naquele momento histórico.",
            "candidate_text": (
                "## Contexto Decisório\n\n"
                "A deliberação governamental — tomada sem consulta aos parlamentares — "
                "precipitou a crise fiscal subsequente."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "borderline",
            "expected_anomaly": "forbidden_em_dash",
        },
    },
    {
        "id": "item_04_pass_with_epistemic_qualification",
        "input": {
            "raw_text": (
                "o tratado de versalhes foi assinado em 1945 bem depois da guerra, todo mundo sabe disso."
            ),
            "candidate_text": (
                "## Os Tratados Internacionais e a Diplomacia\n\n"
                "O interlocutor afirma que o **Tratado de Versalhes** foi firmado em 1945; no entanto, "
                "os registros históricos diplomáticos estabelecem sua celebração formal em 1919 ao término "
                "da Primeira Guerra Mundial. Esta discrepância temporal requer retificação documental."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "typical",
            "expected_anomaly": "none",
        },
    },
    {
        "id": "item_05_fail_binary_antithesis",
        "input": {
            "raw_text": "não é uma questão simples, é algo muito profundo na sociedade.",
            "candidate_text": (
                "## Análise Social\n\n"
                "Não se trata de uma crise orçamentária simples, e sim de uma ruptura "
                "estrutural nos alicerces institucionais do Estado moderno."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "borderline",
            "expected_anomaly": "binary_antithesis",
        },
    },
]


@dataclass
class ConfusionMatrix:
    """Confusion matrix counts for binary quality evaluation."""

    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0
    invalid: int = 0

    @property
    def total_valid(self) -> int:
        return self.tp + self.fp + self.fn + self.tn

    @property
    def accuracy(self) -> float:
        return (self.tp + self.tn) / self.total_valid if self.total_valid > 0 else 0.0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

    def record(self, expected: str, actual: str) -> str:
        """Update counts from expected and actual verdicts and return status string."""
        if expected not in ("PASS", "FAIL"):
            self.invalid += 1
            return "INVALID"

        if expected == "PASS" and actual == "PASS":
            self.tp += 1
            return "TP (True Positive - Correct Pass)"
        if expected == "FAIL" and actual == "FAIL":
            self.tn += 1
            return "TN (True Negative - Correct Reject)"
        if expected == "FAIL" and actual == "PASS":
            self.fp += 1
            return "FP (False Positive - Permissive Leakage)"
        self.fn += 1
        return "FN (False Negative - Pedantic Reject)"


@dataclass
class CalibrationResultSet:
    """Aggregated calibration results across all dimensions."""

    overall: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    target_isolated: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    by_criterion: dict[str, ConfusionMatrix] = field(default_factory=dict)
    by_difficulty: dict[str, ConfusionMatrix] = field(default_factory=dict)
    disagreements: list[dict[str, Any]] = field(default_factory=list)

    @property
    def tp(self) -> int:
        return self.overall.tp

    @property
    def fp(self) -> int:
        return self.overall.fp

    @property
    def fn(self) -> int:
        return self.overall.fn

    @property
    def tn(self) -> int:
        return self.overall.tn

    @property
    def invalid(self) -> int:
        return self.overall.invalid

    @property
    def total_valid(self) -> int:
        return self.overall.total_valid

    @property
    def accuracy(self) -> float:
        return self.overall.accuracy

    @property
    def precision(self) -> float:
        return self.overall.precision

    @property
    def recall(self) -> float:
        return self.overall.recall

    @property
    def f1(self) -> float:
        return self.overall.f1


@dataclass
class ItemEvaluationResult:
    """Evaluation result supporting 4-tuple unpacking and target-specific metrics."""

    actual: str
    expected: str
    score: float
    reasoning: str
    target_actual: str = ""
    target_score: float = 0.0

    def __iter__(self) -> Iterator[Any]:
        """Enable unpacking as (actual, expected, score, reasoning)."""
        yield self.actual
        yield self.expected
        yield self.score
        yield self.reasoning


def evaluate_single_item(judge: Any, item: dict[str, Any]) -> ItemEvaluationResult:
    """Execute judge on item and return unconfounded ItemEvaluationResult."""
    raw_text = item["input"]["raw_text"]
    candidate_text = item["input"]["candidate_text"]
    expected_verdict = item["expected_output"]["verdict"].upper().strip()
    target_criterion_name = item.get("metadata", {}).get("criterion", "")

    context = EvaluationContext(
        stage_name="fluid_prose",
        raw_text=raw_text,
        candidate_text=candidate_text,
        required_criteria=(
            JudgeCriterion.ORALITY_REMOVAL,
            JudgeCriterion.SEMANTIC_FAITHFULNESS,
            JudgeCriterion.EPISTEMIC_CRITIQUE,
            JudgeCriterion.NER_PRESERVATION,
            JudgeCriterion.STRUCTURAL_COMPLIANCE,
            JudgeCriterion.AUTHORIAL_VOICE,
        ),
    )

    evaluation = judge.evaluate(context)
    global_actual = "PASS" if evaluation.passed else "FAIL"
    global_score = evaluation.overall_score
    reasoning = evaluation.extract_critique()

    # Option 3: Isolated target criterion calculation
    target_actual = global_actual
    target_score = global_score
    try:
        if target_criterion_name:
            crit_vo = JudgeCriterion(target_criterion_name)
            crit_score = evaluation.get_score(crit_vo)
            if crit_score is not None:
                target_actual = "PASS" if crit_score.passed else "FAIL"
                target_score = crit_score.score
                if crit_score.reasoning:
                    reasoning = crit_score.reasoning
    except (ValueError, KeyError):
        pass

    return ItemEvaluationResult(
        actual=global_actual,
        expected=expected_verdict,
        score=global_score,
        reasoning=reasoning,
        target_actual=target_actual,
        target_score=target_score,
    )


def run_local_calibration(judge: Any, items: list[dict[str, Any]]) -> CalibrationResultSet:
    """Run calibration over local dataset items and compute global and slice metrics."""
    results = CalibrationResultSet()

    print("\n" + "=" * 70)
    print("RUNNING FLUID PROSE JUDGE CALIBRATION HARNESS")
    print("=" * 70)

    for item in items:
        item_id = item.get("id", "item")
        metadata = item.get("metadata", {})
        criterion = metadata.get("criterion", "general")
        difficulty = metadata.get("difficulty", "typical")

        if criterion not in results.by_criterion:
            results.by_criterion[criterion] = ConfusionMatrix()
        if difficulty not in results.by_difficulty:
            results.by_difficulty[difficulty] = ConfusionMatrix()

        eval_res = evaluate_single_item(judge, item)
        actual_global = eval_res.actual
        expected = eval_res.expected
        score = eval_res.score
        reasoning = eval_res.reasoning
        actual_target = eval_res.target_actual
        target_score = eval_res.target_score

        # 1. Global Pipeline Gate
        results.overall.record(expected, actual_global)
        # 2. Isolated Target Criterion Gate (Option 3)
        status_target = results.target_isolated.record(expected, actual_target)
        results.by_criterion[criterion].record(expected, actual_target)
        results.by_difficulty[difficulty].record(expected, actual_target)

        print(
            f"[{item_id:<26}] Expected: {expected} | Global: {actual_global} ({score:.2f}) | "
            f"Target: {actual_target} ({target_score:.2f}) -> {status_target}"
        )
        if expected != actual_target:
            print(
                f"    Anomaly: {metadata.get('expected_anomaly', 'n/a')} | Defect Loc: {metadata.get('defect_location', 'n/a')}"
            )
            print(f"    Reasoning: {reasoning}")
            results.disagreements.append(
                {
                    "id": item_id,
                    "expected": expected,
                    "actual_global": actual_global,
                    "actual_target": actual_target,
                    "criterion": criterion,
                    "difficulty": difficulty,
                    "reasoning": reasoning,
                }
            )

    return results


def print_calibration_report(results: CalibrationResultSet) -> None:
    """Print structured calibration diagnostics, breakdown tables and recommendations."""
    matrix = results.overall
    target_matrix = results.target_isolated

    print("\n" + "=" * 70)
    print("GLOBAL PIPELINE QUALITY GATE REPORT (Composite Hard Gate)")
    print("=" * 70)
    print(f"Total Evaluated: {matrix.total_valid + matrix.invalid}")
    print(f"Valid Rows:      {matrix.total_valid}")
    print("-" * 70)
    print(f"True Positives (TP):  {matrix.tp}")
    print(f"False Positives (FP): {matrix.fp}")
    print(f"False Negatives (FN): {matrix.fn}")
    print(f"True Negatives (TN):  {matrix.tn}")
    print("-" * 70)
    print(f"Global Accuracy:  {matrix.accuracy * 100:.1f}%")
    print(f"Global Precision: {matrix.precision * 100:.1f}%")
    print(f"Global Recall:    {matrix.recall * 100:.1f}%")
    print(f"Global F1 Score:  {matrix.f1:.3f}")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("ISOLATED TARGET CRITERION CALIBRATION (Option 3: Unconfounded)")
    print("=" * 70)
    print(f"Target Accuracy:  {target_matrix.accuracy * 100:.1f}%")
    print(f"Target Precision: {target_matrix.precision * 100:.1f}%")
    print(f"Target Recall:    {target_matrix.recall * 100:.1f}%")
    print(f"Target F1 Score:  {target_matrix.f1:.3f}")
    print("-" * 70)
    print(
        f"TP: {target_matrix.tp} | FP: {target_matrix.fp} | FN: {target_matrix.fn} | TN: {target_matrix.tn}"
    )
    print("=" * 70)

    # Criterion breakdown table
    print("\nBREAKDOWN BY CRITERION (Target-Isolated Metrics):")
    print(f"{'Criterion':<24} | {'Valid':<5} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6}")
    print("-" * 65)
    for crit, m in results.by_criterion.items():
        print(
            f"{crit:<24} | {m.total_valid:<5} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f}"
        )

    # Difficulty breakdown table
    print("\nBREAKDOWN BY DIFFICULTY (Target-Isolated Metrics):")
    print(f"{'Difficulty':<16} | {'Valid':<5} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6}")
    print("-" * 55)
    for diff, m in results.by_difficulty.items():
        print(
            f"{diff:<16} | {m.total_valid:<5} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f}"
        )

    # Architectural diagnostics
    print("\n" + "=" * 70)
    print("DIAGNOSIS & GATE RECOMMENDATION:")
    if target_matrix.fp > 0:
        print("  [!] WARNING: False Positives detected on target criterion.")
        print("      Risk: Permissive judge passes flawed outputs into knowledge lake.")
        print("      Action: Tighten rubric guidelines for failed criteria.")
    if target_matrix.fn > 0:
        print("  [!] WARNING: False Negatives detected on target criterion.")
        print("      Risk: Overly pedantic judge triggers excessive retries.")
        print("      Action: Refine judge instructions to tolerate valid domain synthesis.")

    if target_matrix.accuracy >= 0.85 and target_matrix.fp == 0:
        print("  [✓] JUDGE CALIBRATED: Target F1 >= 0.85 with zero false positives.")
        print("      Verdict: Safe to activate in blocking mode (judge_blocking=True).")
    else:
        print("  [X] JUDGE NOT CALIBRATED: Does not meet production gates.")
        print("      Verdict: Keep in non-blocking observability mode until tuned.")
    print("=" * 70 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate Fluid Prose LLM Judge")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "ollama", "typesafe"])
    parser.add_argument("--threshold", type=float, default=0.80)
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=DEFAULT_GOLDEN_SET_PATH,
        help="Path to local Golden Set JSON file",
    )
    parser.add_argument("--dataset-name", default="cresmo-fluid-prose-calibration-42")
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Pull dataset dynamically from remote Langfuse instead of local file",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Run quickly against embedded 5-item seed data",
    )
    args = parser.parse_args()

    settings = CresmoSettings(
        judge_provider=args.provider,
        judge_pass_threshold=args.threshold,
    )

    logger.info("Instantiating Judge adapter chain (Provider: %s)...", args.provider)
    judge = build_llm_judge_adapter(settings=settings)

    if args.seed_only:
        logger.info(
            "Executing calibration against embedded seed items (%d items)...",
            len(SEED_CALIBRATION_DATA),
        )
        results = run_local_calibration(judge, SEED_CALIBRATION_DATA)
        print_calibration_report(results)
        return 0 if results.overall.accuracy >= 0.85 else 1

    if args.remote:
        try:
            from langfuse import Langfuse

            langfuse = Langfuse()
            dataset = langfuse.get_dataset(args.dataset_name)
            logger.info(
                "Found remote Langfuse dataset '%s' with %d items.",
                args.dataset_name,
                len(dataset.items),
            )
            items = [
                {
                    "id": it.id,
                    "input": it.input,
                    "expected_output": it.expected_output,
                    "metadata": it.metadata or {},
                }
                for it in dataset.items
            ]
            results = run_local_calibration(judge, items)
            print_calibration_report(results)
            return 0 if results.overall.accuracy >= 0.85 else 1
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed connecting to remote Langfuse dataset: %s", exc)
            return 1

    # Default: Load local golden set file
    if not args.dataset_path.exists():
        logger.warning(
            "Golden set file '%s' not found. Falling back to embedded seed data.", args.dataset_path
        )
        results = run_local_calibration(judge, SEED_CALIBRATION_DATA)
        print_calibration_report(results)
        return 0 if results.overall.accuracy >= 0.85 else 1

    logger.info("Loading Golden Set from '%s'...", args.dataset_path)
    with open(args.dataset_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    logger.info("Loaded %d items from %s. Starting calibration...", len(items), args.dataset_path)
    results = run_local_calibration(judge, items)
    print_calibration_report(results)
    return 0 if results.overall.accuracy >= 0.85 else 1


if __name__ == "__main__":
    sys.exit(main())
