#!/usr/bin/env python3
"""Offline Calibration Harness for Fluid Prose LLM Judges.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria, Two-Layered Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates, Mechanical Invariants, and Calibration Framework
    - Langfuse Judge Calibration: .agents/skills/langfuse/references/judge-calibration.md
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from typing import Any

from cresmo.domain.value_objects.quality import (
    EvaluationContext,
    JudgeCriterion,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("calibrate_judge")


# Canonical seed dataset items for dry-run offline calibration
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
        "metadata": {"category": "valid_transformation"},
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
        "metadata": {"defect": "youtube_cta_leakage", "violates": "ORALITY_REMOVAL"},
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
        "metadata": {"defect": "forbidden_em_dash", "violates": "STRUCTURAL_COMPLIANCE"},
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
        "metadata": {"category": "valid_epistemic_critique", "target": "EPISTEMIC_CRITIQUE"},
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
        "metadata": {"defect": "binary_antithesis", "violates": "AUTHORIAL_VOICE"},
    },
    {
        "id": "item_06_fail_hallucination_external",
        "input": {
            "raw_text": "falamos apenas sobre a colheita do café no vale do paraíba no século 19.",
            "candidate_text": (
                "## A Cafeicultura e o Sistema Financeiro Global\n\n"
                "A produção cafeeira no Vale do Paraíba provocou o colapso dos bancos britânicos "
                "e culminou no Tratado de Bretton Woods em 1944 nos Estados Unidos."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {"defect": "anachronistic_hallucination", "violates": "SEMANTIC_FAITHFULNESS"},
    },
    {
        "id": "item_07_pass_ner_normalized",
        "input": {
            "raw_text": "o pensador friedrich nitshe escreveu sobre o eterno retorno dos acontecimentos.",
            "candidate_text": (
                "## A Ontologia do Eterno Retorno\n\n"
                "Na obra do filósofo **Friedrich Nietzsche**, a concepção do eterno retorno "
                "desafia a linearidade temporal e propõe uma radical afirmação da existência humana."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {"category": "valid_ner_normalization", "target": "NER_PRESERVATION"},
    },
    {
        "id": "item_08_fail_missing_line1_heading",
        "input": {
            "raw_text": "uma explanação detalhada da geopolítica naval do atlântico sul.",
            "candidate_text": (
                "Este parágrafo inicial não possui o cabeçalho obrigatório na linha 1.\n\n"
                "A disputa por rotas comerciais redefiniu a soberania marítima."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {"defect": "missing_line1_heading", "violates": "STRUCTURAL_COMPLIANCE"},
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


def evaluate_single_item(judge: Any, item: dict[str, Any]) -> tuple[str, str, float, str]:
    """Execute judge on item and return (actual_verdict, expected_verdict, score, reasoning)."""
    raw_text = item["input"]["raw_text"]
    candidate_text = item["input"]["candidate_text"]
    expected_verdict = item["expected_output"]["verdict"].upper().strip()

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
    actual_verdict = "PASS" if evaluation.passed else "FAIL"
    reasoning = evaluation.extract_critique()
    return actual_verdict, expected_verdict, evaluation.overall_score, reasoning


def run_local_calibration(judge: Any, items: list[dict[str, Any]]) -> ConfusionMatrix:
    """Run calibration over local dataset items and compute confusion matrix."""
    matrix = ConfusionMatrix()

    print("\n" + "=" * 70)
    print("RUNNING FLUID PROSE JUDGE CALIBRATION HARNESS")
    print("=" * 70)

    for item in items:
        item_id = item.get("id", "item")
        actual, expected, score, reasoning = evaluate_single_item(judge, item)

        if expected not in ("PASS", "FAIL"):
            matrix.invalid += 1
            print(f"[{item_id}] INVALID expected label: {expected}")
            continue

        if expected == "PASS" and actual == "PASS":
            matrix.tp += 1
            status = "TP (True Positive - Correct Pass)"
        elif expected == "FAIL" and actual == "FAIL":
            matrix.tn += 1
            status = "TN (True Negative - Correct Reject)"
        elif expected == "FAIL" and actual == "PASS":
            matrix.fp += 1
            status = "FP (False Positive - Permissive Leakage)"
        else:
            matrix.fn += 1
            status = "FN (False Negative - Pedantic Reject)"

        print(f"[{item_id}] Expected: {expected} | Actual: {actual} (Score: {score:.2f}) -> {status}")
        if expected != actual:
            print(f"    Reasoning: {reasoning}")

    return matrix


def print_calibration_report(matrix: ConfusionMatrix) -> None:
    """Print structured calibration diagnostics and recommendations."""
    print("\n" + "=" * 70)
    print("CALIBRATION METRICS & CONFUSION MATRIX REPORT")
    print("=" * 70)
    print(f"Total Evaluated: {matrix.total_valid + matrix.invalid}")
    print(f"Valid Rows:      {matrix.total_valid}")
    print(f"Invalid Rows:    {matrix.invalid}")
    print("-" * 70)
    print(f"True Positives (TP):  {matrix.tp}")
    print(f"False Positives (FP): {matrix.fp}")
    print(f"False Negatives (FN): {matrix.fn}")
    print(f"True Negatives (TN):  {matrix.tn}")
    print("-" * 70)
    print(f"Accuracy:  {matrix.accuracy * 100:.1f}%")
    print(f"Precision: {matrix.precision * 100:.1f}%")
    print(f"Recall:    {matrix.recall * 100:.1f}%")
    print(f"F1 Score:  {matrix.f1:.3f}")
    print("=" * 70)

    # Architectural diagnostics
    print("DIAGNOSIS & GATE RECOMMENDATION:")
    if matrix.fp > 0:
        print("  [!] WARNING: False Positives detected (judge approved flawed outputs).")
        print("      Risk: Knowledge lake pollution with YouTube CTAs or syntax errors.")
        print("      Action: Tighten judge pass_threshold or strengthen mechanical gates.")
    if matrix.fn > 0:
        print("  [!] WARNING: False Negatives detected (judge rejected valid outputs).")
        print("      Risk: Redundant retry loops and excessive token spend.")
        print("      Action: Refine judge prompt instructions to reduce pedantry.")

    if matrix.accuracy >= 0.85 and matrix.fp == 0:
        print("  [✓] JUDGE CALIBRATED: F1 >= 0.85 with zero permissive false positives.")
        print("      Verdict: Safe to activate in blocking mode (judge_blocking=True).")
    else:
        print("  [X] JUDGE NOT CALIBRATED: Does not meet production gates.")
        print("      Verdict: Keep in non-blocking observability mode until tuned.")
    print("=" * 70 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate Fluid Prose LLM Judge")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "ollama", "typesafe"])
    parser.add_argument("--threshold", type=float, default=0.80)
    parser.add_argument("--dataset-name", default="cresmo-fluid-prose-calibration")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run hermetically using embedded seed examples without remote Langfuse dataset",
    )
    args = parser.parse_args()

    settings = CresmoSettings(
        judge_provider=args.provider,
        judge_pass_threshold=args.threshold,
    )

    logger.info("Instantiating Judge adapter chain (Provider: %s)...", args.provider)
    judge = build_llm_judge_adapter(settings=settings)

    if args.dry_run:
        logger.info("Executing dry-run calibration against %d seed items...", len(SEED_CALIBRATION_DATA))
        matrix = run_local_calibration(judge, SEED_CALIBRATION_DATA)
        print_calibration_report(matrix)
        return 0 if matrix.accuracy >= 0.85 else 1

    # Remote Langfuse Dataset Experiment execution
    try:
        from langfuse import Langfuse

        langfuse = Langfuse()
        dataset = langfuse.get_dataset(args.dataset_name)
        logger.info("Found remote Langfuse dataset '%s' with %d items.", args.dataset_name, len(dataset.items))
        matrix = run_local_calibration(
            judge,
            [{"id": it.id, "input": it.input, "expected_output": it.expected_output} for it in dataset.items],
        )
        print_calibration_report(matrix)
        return 0 if matrix.accuracy >= 0.85 else 1
    except Exception as exc:
        logger.error("Failed connecting to remote Langfuse dataset: %s", exc)
        logger.info("Tip: Run with --dry-run to test locally using embedded seed items.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
