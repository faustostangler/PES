#!/usr/bin/env python3
"""Offline Calibration Harness for Gap Filler LLM Judges.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - ADR-028: Decoupling Fluid Prose and Socratic Gap Filling
    - SPEC-015: Quality Gates and Calibration Framework
    - Langfuse Judge Calibration: .agents/skills/langfuse/references/judge-calibration.md
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
import time
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from statistics import NormalDist
from typing import Annotated, Any

import click
import structlog
import typer

# Ensure project root and src are in sys.path when invoked directly as a script / debugger
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
for p in (str(SRC_DIR), str(REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from cresmo.domain.value_objects.quality import (
    EvaluationContext,
    JudgeCriterion,
)
from cresmo.infrastructure.adapters.gemini_pool import CredentialPoolExhaustedError
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

logger = structlog.get_logger("calibrate_gap_filler_judge")

DEFAULT_GOLDEN_SET_PATH = (
    REPO_ROOT / "scripts" / "gap_filler" / "golden_sets" / "gap_filler_golden_set.json"
)

# Canonical benchmark judge models evaluated sequentially by default (configured via CresmoSettings)
ALL_CALIBRATION_MODELS: list[str] = CresmoSettings().judge_calibration_models


def resolve_model_spec(spec: str, default_provider: str = "gemini") -> tuple[str, str]:
    """Parse model specification string into (provider, model_name)."""
    if ":" in spec:
        provider, model_name = spec.split(":", 1)
        return provider.strip().lower(), model_name.strip()
    if spec.lower().startswith("gemini"):
        return "gemini", spec
    if spec.lower().startswith("ollama"):
        return "ollama", spec
    if spec.lower().startswith("typesafe"):
        return "typesafe", spec
    return default_provider, spec


def sanitize_report_filename(provider: str, model_name: str) -> str:
    """Generate clean slug for model calibration report file."""
    clean_model = model_name
    if clean_model.startswith(f"{provider}:"):
        clean_model = clean_model[len(provider) + 1 :]
    clean_model = clean_model.replace(":", "_").replace("/", "_")
    clean_model = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean_model)
    return f"llm_judge_{provider}_{clean_model}.txt"


# Canonical seed dataset items for quick dry-run
SEED_CALIBRATION_DATA: list[dict[str, Any]] = [
    {
        "id": "seed_01_pass_factual_grounding",
        "input": {
            "raw_text": (
                "## A Posse de Afonso Henriques e a Bula Manifestis Probatum\n\n"
                "Afonso Henriques declarou a autonomia do Condado Portucalense no século XII. "
                "Após anos de conflitos contra o Reino de Leão e campanhas da Reconquista, "
                "a corte papal reconheceu formalmente a soberania portuguesa através de documento solene."
            ),
            "candidate_text": (
                "## A Autonomia Feudal e a Legitimação Apostólica do Reino de Portugal\n\n"
                "A consolidação política da independência portucalense exigiu não apenas vitórias campais "
                "contra os exércitos de Afonso VII de Leão, mas a inserção direta na rede de suserania da Santa Sé. "
                "Em 23 de maio de 1179, o papa **Alexandre III** promulgou a célebre bula **Manifestis Probatum**, "
                "declarando **Afonso Henriques** rei soberano de Portugal e outorgando proteção apostólica contra "
                "quaisquer pretensões anexionistas de monarcas cristãos vizinhos.\n\n"
                "Esse ato diplomático coroou um esforço de décadas iniciado no Tratado de Zamora em 1143, subordinando "
                "a legitimidade jurídica do novo reino ao pagamento anual de um censo de dois marcos de ouro à corte romana.\n\n"
                "## Informações Complementares\n\n"
                "1. O Tratado de Zamora de outubro de 1143 contou com a mediação do cardeal Guido de Vico, legado papal na Península Ibérica.\n\n"
                "2. O censo pago por Afonso Henriques à Santa Sé foi elevado de quatro onças de ouro anuais em 1144 para dois marcos de ouro em 1179."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "factual_grounding",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "seed_02_fail_socratic_epistemic_depth",
        "input": {
            "raw_text": (
                "## Concorrência e Gargalos em Bancos Relacionais sob Alta Carga\n\n"
                "Em testes de estresse com milhares de requisições simultâneas por segundo, o banco de dados PostgreSQL "
                "frequentemente apresenta degradação severa de latência quando as conexões não são limitadas. "
                "O esgotamento de recursos decorre da contenção de bloqueios em linhas concorrentes e do custo de "
                "context switching entre múltiplos processos no sistema operacional."
            ),
            "candidate_text": (
                "## O Esgotamento de Recursos em Bancos Relacionais sob Concorrência Extrema\n\n"
                "Em cenários de estresse computacional caracterizados por taxas elevadas de transações simultâneas, "
                "a arquitetura do **PostgreSQL** manifesta variações desproporcionais na latência percebida pelos clientes. "
                "A saturação de conexões sem pooling adequado impõe um ônus operacional que degrada o rendimento global "
                "da aplicação sob teste de estresse na infraestrutura em contêineres **Docker**.\n\n"
                "A degradação manifesta-se através de disputas intensas por recursos compartilhados, onde diferentes "
                "processos disputam o acesso aos mesmos registros de tabelas financeiras. A sobrecarga de gerenciar "
                "dezenas de processos paralelos força o núcleo do sistema operacional a despender ciclos valiosos de "
                "processamento em trocas de contexto em vez de executar consultas analíticas úteis.\n\n"
                "Essas perturbações confirmam a necessidade de dimensionar corretamente o agrupamento de conexões "
                "e revisar a modelagem de consultas para preservar a estabilidade da camada de persistência.\n\n"
                "## Informações Complementares\n\n"
                "1. O gerenciador de conexões PgBouncer opera em três modos distintos de agrupamento: sessão, transação e instrução.\n\n"
                "2. O comando EXPLAIN ANALYZE do PostgreSQL executa a consulta e retorna o plano de execução real juntamente com os custos."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "socratic_epistemic_depth",
            "difficulty": "borderline",
            "expected_anomaly": "explanatory_vacuum_missing_mvcc_intermediate_mechanisms",
            "defect_location": "paragraph_2",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
]


@dataclass(frozen=True)
class MetricInfo:
    """Informações conceituais e quantitativas de cada métrica de avaliação do juiz."""

    code: str
    name: str
    math_formula: str
    meaning: str


METRIC_DICTIONARY: list[MetricInfo] = [
    MetricInfo(
        code="hit_rate",
        name="Taxa de Hit (Sensibilidade)",
        math_formula="Hit / (Hit + Pedantismo-Beta)",
        meaning="Proporção de textos conformes que o juiz aprova.",
    ),
    MetricInfo(
        code="specificity",
        name="Especificidade (Taxa de Rejeição)",
        math_formula="Rejeição / (Rejeição + Permissivo-Alfa)",
        meaning="Proporção de textos defeituosos que o juiz reprova.",
    ),
    MetricInfo(
        code="accuracy",
        name="Acurácia Global",
        math_formula="(Hit + Rejeição) / Total",
        meaning="Proporção de decisões corretas do juiz.",
    ),
    MetricInfo(
        code="precision",
        name="Precisão (Valor Preditivo Positivo)",
        math_formula="Hit / (Hit + Permissivo-Alfa)",
        meaning="Confiabilidade de uma aprovação emitida pelo juiz.",
    ),
    MetricInfo(
        code="f1",
        name="F1-Score Balanceado",
        math_formula="2 * (Precisão * Recall) / (Precisão + Recall)",
        meaning="Média harmônica entre precisão e sensibilidade.",
    ),
    MetricInfo(
        code="mcc",
        name="Coeficiente de Correlação de Matthews (MCC)",
        math_formula="((Hit * Rej) - (Alfa * Beta)) / sqrt((H+A)(H+B)(R+A)(R+B))",
        meaning="Correlação entre previsões e gabarito (-1 a +1).",
    ),
    MetricInfo(
        code="d_prime",
        name="Sensibilidade de Discriminação (d')",
        math_formula="NormInv(Taxa Hit) - NormInv(Taxa Permissivo)",
        meaning="Capacidade intrínseca de separar sinal e ruído.",
    ),
    MetricInfo(
        code="c_bias",
        name="Critério de Resposta (c)",
        math_formula="-0.5 * (NormInv(Taxa Hit) + NormInv(Taxa Permissivo))",
        meaning="Tendência sistemática a aprovar (liberal) ou reprovar (conservador).",
    ),
]


@dataclass
class ConfusionMatrix:
    """Matriz de Confusão 2x2 segundo a Teoria de Detecção de Sinal (SDT)."""

    hit: int = 0
    pedantismo_beta: int = 0
    permissivo_alfa: int = 0
    rejeicao: int = 0
    invalid: int = 0

    @property
    def tp(self) -> int:
        return self.hit

    @property
    def fn(self) -> int:
        return self.pedantismo_beta

    @property
    def fp(self) -> int:
        return self.permissivo_alfa

    @property
    def tn(self) -> int:
        return self.rejeicao

    @property
    def total_corretos(self) -> int:
        return self.hit + self.pedantismo_beta

    @property
    def total_defeituosos(self) -> int:
        return self.permissivo_alfa + self.rejeicao

    @property
    def total_valid(self) -> int:
        return self.total_corretos + self.total_defeituosos

    @property
    def total_avaliacoes(self) -> int:
        return self.total_valid + self.invalid

    @property
    def hit_rate(self) -> float:
        tot = self.total_corretos
        return self.hit / tot if tot > 0 else 0.0

    @property
    def recall(self) -> float:
        return self.hit_rate

    @property
    def beta_fnr(self) -> float:
        tot = self.total_corretos
        return self.pedantismo_beta / tot if tot > 0 else 0.0

    @property
    def alpha_fpr(self) -> float:
        tot = self.total_defeituosos
        return self.permissivo_alfa / tot if tot > 0 else 0.0

    @property
    def specificity(self) -> float:
        tot = self.total_defeituosos
        return self.rejeicao / tot if tot > 0 else 0.0

    @property
    def accuracy(self) -> float:
        tot = self.total_valid
        return (self.hit + self.rejeicao) / tot if tot > 0 else 0.0

    @property
    def precision(self) -> float:
        denom = self.hit + self.permissivo_alfa
        return self.hit / denom if denom > 0 else 0.0

    @property
    def f1(self) -> float:
        p = self.precision
        r = self.recall
        return (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

    @property
    def mcc(self) -> float:
        num = (self.hit * self.rejeicao) - (self.permissivo_alfa * self.pedantismo_beta)
        denom = math.sqrt(
            (self.hit + self.permissivo_alfa)
            * (self.hit + self.pedantismo_beta)
            * (self.rejeicao + self.permissivo_alfa)
            * (self.rejeicao + self.pedantismo_beta)
        )
        return num / denom if denom > 0 else 0.0

    @property
    def d_prime(self) -> float:
        n_signal = self.total_corretos
        n_noise = self.total_defeituosos
        if n_signal == 0 or n_noise == 0:
            return 0.0
        eps_s = 1.0 / (2 * n_signal)
        eps_n = 1.0 / (2 * n_noise)
        hit_rate = self.hit / n_signal
        fa_rate = self.permissivo_alfa / n_noise
        h_clamp = min(max(hit_rate, eps_s), 1.0 - eps_s)
        fa_clamp = min(max(fa_rate, eps_n), 1.0 - eps_n)
        norm = NormalDist()
        return norm.inv_cdf(h_clamp) - norm.inv_cdf(fa_clamp)

    @property
    def c_bias(self) -> float:
        n_signal = self.total_corretos
        n_noise = self.total_defeituosos
        if n_signal == 0 or n_noise == 0:
            return 0.0
        eps_s = 1.0 / (2 * n_signal)
        eps_n = 1.0 / (2 * n_noise)
        hit_rate = self.hit / n_signal
        fa_rate = self.permissivo_alfa / n_noise
        h_clamp = min(max(hit_rate, eps_s), 1.0 - eps_s)
        fa_clamp = min(max(fa_rate, eps_n), 1.0 - eps_n)
        norm = NormalDist()
        return -0.5 * (norm.inv_cdf(h_clamp) + norm.inv_cdf(fa_clamp))

    def record(self, expected: str, actual: str) -> str:
        """Update counts from expected and actual verdicts and return status string."""
        if expected not in ("PASS", "FAIL"):
            self.invalid += 1
            return "INVALID"

        if expected == "PASS":
            if actual == "PASS":
                self.hit += 1
                return "HIT"
            if actual == "FAIL":
                self.pedantismo_beta += 1
                return "PEDANTISMO_BETA"
            self.invalid += 1
            return "INVALID"

        # expected == "FAIL"
        if actual == "PASS":
            self.permissivo_alfa += 1
            return "PERMISSIVO_ALFA"
        if actual == "FAIL":
            self.rejeicao += 1
            return "REJEICAO"
        self.invalid += 1
        return "INVALID"


@dataclass
class CalibrationResultSet:
    """Agregador de resultados globais e fatias da calibração."""

    overall: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    target_isolated: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    by_criterion: dict[str, ConfusionMatrix] = field(default_factory=dict)
    by_difficulty: dict[str, ConfusionMatrix] = field(default_factory=dict)
    disagreements: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ItemEvaluationResult:
    """Evaluation result supporting unpacking and target-specific metrics."""

    actual: str
    expected: str
    score: float
    reasoning: str
    target_actual: str = ""
    target_score: float = 0.0

    def __iter__(self) -> Iterator[Any]:
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
        stage_name="gap_filler",
        raw_text=raw_text,
        candidate_text=candidate_text,
        required_criteria=(
            JudgeCriterion.FACTUAL_GROUNDING,
            JudgeCriterion.SOCRATIC_EPISTEMIC_DEPTH,
            JudgeCriterion.CAUSAL_STRATIFICATION_AGENCY,
            JudgeCriterion.COMPLEMENTARY_SUBSTANCE,
            JudgeCriterion.AUTHORIAL_NATURALISM,
        ),
    )

    evaluation = judge.evaluate(context)
    global_actual = "PASS" if evaluation.passed else "FAIL"
    global_score = evaluation.overall_score
    reasoning = evaluation.extract_critique()

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


def run_local_calibration(
    judge: Any,
    items: list[dict[str, Any]],
    delay: float = 4.2,
    jitter: float = 0.8,
    max_retry_wait: float = 60.0,
) -> CalibrationResultSet:
    """Run calibration over local dataset items and compute global and slice metrics."""
    results = CalibrationResultSet()

    print("\n" + "=" * 70)
    print("RUNNING GAP FILLER JUDGE CALIBRATION HARNESS")
    if delay > 0:
        print(
            f"Pacing: {delay:.1f}s base delay + up to {jitter:.1f}s jitter between LLM evaluations"
        )
    print("=" * 70)

    for i, item in enumerate(items, start=1):
        item_id = item.get("id", "item")
        metadata = item.get("metadata", {})
        criterion = metadata.get("criterion", "general")
        difficulty = metadata.get("difficulty", "typical")

        if criterion not in results.by_criterion:
            results.by_criterion[criterion] = ConfusionMatrix()
        if difficulty not in results.by_difficulty:
            results.by_difficulty[difficulty] = ConfusionMatrix()

        max_attempts = 3
        eval_res = None
        for attempt in range(1, max_attempts + 1):
            try:
                eval_res = evaluate_single_item(judge, item)
                break
            except CredentialPoolExhaustedError as exc:
                if exc.retry_after_seconds <= max_retry_wait and attempt < max_attempts:
                    logger.warning(
                        "[RETRY %d/%d] Credential pool in cooldown (%.1fs <= %.1fs limit). Waiting before retry for '%s'...",
                        attempt,
                        max_attempts,
                        exc.retry_after_seconds,
                        max_retry_wait,
                        item_id,
                    )
                    time.sleep(exc.retry_after_seconds)
                else:
                    logger.error(
                        "\n🚨 [COOLDOWN ABORT] Model credentials in cooldown for %.1fs (> %.1fs limit). "
                        "Aborting calibration to preserve benchmark isolation (zero fallback).",
                        exc.retry_after_seconds,
                        max_retry_wait,
                    )
                    raise
            except Exception as exc:
                if attempt < max_attempts:
                    retry_wait = min(15.0, 3.0 * attempt)
                    logger.warning(
                        "[RETRY %d/%d] Transient error during evaluation of '%s': %s. Waiting %.1fs before retrying...",
                        attempt,
                        max_attempts,
                        item_id,
                        exc,
                        retry_wait,
                    )
                    time.sleep(retry_wait)
                else:
                    logger.error(
                        "\n🚨 [EVALUATION ABORT] Failed to evaluate item '%s' after %d attempts: %s",
                        item_id,
                        max_attempts,
                        exc,
                    )
                    raise

        if eval_res is None:
            continue

        actual_global = eval_res.actual
        expected = eval_res.expected
        reasoning = eval_res.reasoning
        actual_target = eval_res.target_actual
        target_score = eval_res.target_score

        # 1. Global Pipeline Gate
        results.overall.record(expected, actual_global)
        # 2. Isolated Target Criterion Gate
        status_target = results.target_isolated.record(expected, actual_target)
        results.by_criterion[criterion].record(expected, actual_target)
        results.by_difficulty[difficulty].record(expected, actual_target)

        print(
            f"[{i:02d}/{len(items):02d}] [{item_id:<26}] Expected: {expected} | "
            f"Target: {actual_target} ({target_score:.2f}) -> {status_target}"
        )
        if expected != actual_target:
            print(f"    [DIVERGÊNCIA] Anomaly: {metadata.get('expected_anomaly', 'n/a')}")
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

        # Rate-limiting pacing with jitter before next item
        if i < len(items) and delay > 0:
            sleep_time = delay + random.uniform(0.0, jitter)
            time.sleep(sleep_time)

    return results


def save_calibration_report(
    results: CalibrationResultSet,
    output_path: Path,
    provider: str,
    model: str,
) -> None:
    """Save formatted calibration report to output text file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    m = results.target_isolated

    lines = [
        "=" * 80,
        f"CRESMO STAGE 2 (GAP_FILLER) JUDGE CALIBRATION REPORT - {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "=" * 80,
        f"Provider: {provider} | Model: {model}",
        f"Total Items: {m.total_valid} | Valid: {m.total_valid} | Invalid: {m.invalid}",
        f"Overall Target Accuracy: {m.accuracy * 100:.2f}%",
        f"Precision: {m.precision * 100:.2f}% | Recall: {m.recall * 100:.2f}% | F1: {m.f1:.4f}",
        f"Specificity: {m.specificity * 100:.2f}% | Alpha (FPR): {m.alpha_fpr * 100:.2f}% | Beta (FNR): {m.beta_fnr * 100:.2f}%",
        f"MCC: {m.mcc:.4f} | d-prime (d'): {m.d_prime:.4f} | c bias: {m.c_bias:.4f}",
        "",
        "CRITERIA BREAKDOWN:",
        "-" * 80,
    ]

    for crit, c_mat in sorted(results.by_criterion.items()):
        lines.append(
            f"{crit:<35} | Items: {c_mat.total_valid:2d} | "
            f"Acc: {c_mat.accuracy * 100:5.1f}% | Hit: {c_mat.hit} | Rej: {c_mat.rejeicao} | "
            f"Alfa: {c_mat.permissivo_alfa} | Beta: {c_mat.pedantismo_beta}"
        )

    lines.extend(
        [
            "",
            "DIFFICULTY BREAKDOWN:",
            "-" * 80,
        ]
    )
    for diff, d_mat in sorted(results.by_difficulty.items()):
        lines.append(
            f"{diff:<35} | Items: {d_mat.total_valid:2d} | "
            f"Acc: {d_mat.accuracy * 100:5.1f}% | Hit: {d_mat.hit} | Rej: {d_mat.rejeicao} | "
            f"Alfa: {d_mat.permissivo_alfa} | Beta: {d_mat.pedantismo_beta}"
        )

    if results.disagreements:
        lines.extend(
            [
                "",
                f"DISAGREEMENTS / CLASSIFICATION ERRORS ({len(results.disagreements)}):",
                "-" * 80,
            ]
        )
        for d in results.disagreements:
            lines.append(
                f"- ID: {d['id']} | Expected: {d['expected']} | Actual: {d['actual_target']} | "
                f"Crit: {d['criterion']} | Diff: {d['difficulty']}\n  Critique: {d['reasoning']}"
            )

    report_content = "\n".join(lines) + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"\nCalibration report successfully saved to: {output_path}")


app = typer.Typer(
    name="calibrate-gap-filler",
    help="Offline Calibration Harness for Gap Filler LLM Judges.",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def calibrate(
    models: Annotated[
        list[str] | None,
        typer.Option(
            "--models",
            help="List of model specifications to calibrate sequentially. Default: configured in CresmoSettings.judge_calibration_models.",
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            help="Optional single model override (e.g. 'gemini-3.5-flash-lite', 'qwen2.5:14b')",
        ),
    ] = None,
    provider: Annotated[
        str,
        typer.Option(
            "--provider",
            help="Default provider fallback when not specified in model spec (default: 'gemini')",
        ),
    ] = "gemini",
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            help="Approval pass threshold (default: 0.80)",
        ),
    ] = 0.80,
    dataset_path: Annotated[
        Path,
        typer.Option(
            "--dataset-path",
            help="Path to local golden set JSON",
        ),
    ] = DEFAULT_GOLDEN_SET_PATH,
    seed_only: Annotated[
        bool,
        typer.Option(
            "--seed-only",
            help="Run calibration on minimal seed dataset for testing without loading full set",
        ),
    ] = False,
    delay: Annotated[
        float | None,
        typer.Option(
            "--delay",
            help="Delay between requests in seconds (default: 4.2s for Gemini API, 0.0s for local Ollama)",
        ),
    ] = None,
    jitter: Annotated[
        float | None,
        typer.Option(
            "--jitter",
            help="Random jitter in seconds (default: 0.8s for Gemini API, 0.0s for local Ollama)",
        ),
    ] = None,
    output_path: Annotated[
        Path | None,
        typer.Option(
            "--output-path",
            help="Custom destination path to write full calibration report (single model mode)",
        ),
    ] = None,
) -> None:
    # 1. Resolve Target Models
    if models:
        target_specs = models
    elif model:
        target_specs = [model]
    else:
        target_specs = ALL_CALIBRATION_MODELS

    # 2. Resolve Dataset Items
    if seed_only or not dataset_path.exists():
        if not seed_only:
            logger.warning(
                "Golden set file '%s' not found. Falling back to embedded seed data.",
                dataset_path,
            )
        items = SEED_CALIBRATION_DATA
        logger.info("Using embedded seed dataset (%d items).", len(items))
    else:
        logger.info("Loading Golden Set from '%s'...", dataset_path)
        with open(dataset_path, encoding="utf-8") as f:
            items = json.load(f)
        logger.info("Loaded %d items from %s.", len(items), dataset_path)

    print(f"\n🎯 Modelos agendados para calibração do Judge ({len(target_specs)}):")
    for i, m in enumerate(target_specs, 1):
        print(f"   {i}. {m}")
    print()

    # 3. Iterate sequentially over models
    reports: list[dict[str, Any]] = []
    overall_exit_code = 0

    for spec in target_specs:
        resolved_provider, model_name = resolve_model_spec(spec, default_provider=provider)
        req_delay = delay if delay is not None else (0.0 if resolved_provider == "ollama" else 4.2)
        req_jitter = (
            jitter if jitter is not None else (0.0 if resolved_provider == "ollama" else 0.8)
        )

        model_kwargs: dict[str, Any] = {}
        if resolved_provider == "ollama":
            model_kwargs["ollama_model"] = model_name
        elif resolved_provider == "gemini":
            model_kwargs["judge_gemini_model"] = model_name
        elif resolved_provider == "typesafe":
            model_kwargs["typesafe_model"] = model_name

        settings = CresmoSettings(
            judge_provider=resolved_provider,
            gap_filler_judge_threshold=threshold,
            **model_kwargs,
        )

        if output_path and len(target_specs) == 1:
            output_file = output_path
        else:
            filename = sanitize_report_filename(resolved_provider, model_name)
            output_file = REPO_ROOT / "scripts" / "gap_filler" / filename

        logger.info(
            "\n🚀 INICIANDO CALIBRAÇÃO DO JUIZ: [%s] %s",
            resolved_provider.upper(),
            model_name,
        )
        # Metrological isolation: zero fallback failover during calibration
        judge = build_llm_judge_adapter(settings=settings, enable_fallback=False)

        try:
            results = run_local_calibration(
                judge,
                items,
                delay=req_delay,
                jitter=req_jitter,
            )
            save_calibration_report(
                results,
                output_path=output_file,
                provider=resolved_provider,
                model=model_name,
            )

            acc = results.target_isolated.accuracy
            d_prime = results.target_isolated.d_prime
            f1 = results.target_isolated.f1
            prec = results.target_isolated.precision
            rec = results.target_isolated.recall

            reports.append(
                {
                    "spec": f"{resolved_provider}:{model_name}",
                    "accuracy": acc,
                    "d_prime": d_prime,
                    "f1": f1,
                    "precision": prec,
                    "recall": rec,
                    "output_file": output_file,
                    "passed": acc >= 0.80,
                }
            )

            if acc < 0.80:
                overall_exit_code = 1
        except CredentialPoolExhaustedError as exc:
            logger.error(
                "❌ [ABORTADO] Modelo '%s:%s' abortado devido a cooldown de cota (%.1fs). "
                "Calibração interrompida para este modelo para evitar contaminação do benchmark.",
                resolved_provider,
                model_name,
                exc.retry_after_seconds,
            )
            reports.append(
                {
                    "spec": f"{resolved_provider}:{model_name}",
                    "accuracy": 0.0,
                    "d_prime": 0.0,
                    "f1": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "output_file": f"ABORTADO (COOLDOWN {exc.retry_after_seconds:.0f}s)",
                    "passed": False,
                }
            )
            overall_exit_code = 1

    # 4. Print Comparative Summary Table
    print("\n" + "=" * 90)
    print("COMPARATIVO DE CALIBRAÇÃO DOS JUÍZES (STAGE 2: GAP_FILLER)")
    print("=" * 90)
    print(
        f"{'Modelo':<35} | {'Acurácia':<8} | {'d-prime':<7} | {'F1':<6} | {'Precisão':<8} | {'Recall':<6} | {'Status':<6}"
    )
    print("-" * 90)
    for r in reports:
        status_str = "APROVADO" if r["passed"] else "FALHOU"
        print(
            f"{r['spec']:<35} | {r['accuracy'] * 100:>7.1f}% | {r['d_prime']:>7.2f} | {r['f1']:>6.3f} | {r['precision'] * 100:>7.1f}% | {r['recall'] * 100:>5.1f}% | {status_str:<6}"
        )
    print("=" * 90)
    print("📁 Relatórios individuais salvos em:")
    for r in reports:
        print(f"   👉 {r['output_file']}")
    print()

    if overall_exit_code != 0:
        raise typer.Exit(code=overall_exit_code)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute gap filler judge calibration entrypoint.

    Args:
        argv: Optional sequence of CLI arguments. If None, uses sys.argv[1:].

    Returns:
        Exit code (0 for success/approval, non-zero for failure).
    """
    try:
        res = app(args=list(argv) if argv is not None else None, standalone_mode=False)
        return 0 if res is None else int(res)
    except typer.Exit as exc:
        return exc.exit_code
    except click.ClickException as exc:
        sys.stderr.write(f"Usage error: {exc}\n")
        return getattr(exc, "exit_code", 2)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
    print('done!')