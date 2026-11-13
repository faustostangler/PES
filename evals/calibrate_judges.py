#!/usr/bin/env python3
"""Unified Zero-Fallback LLM Judge Calibration Harness with Cooldown Checkpointing.

Executes offline calibration for one or more pipeline stages (`fluid_prose`, `gap_filler`)
against one or more LLM judge models with `enable_fallback=False` unconditionally enforced.
Progress is incrementally persisted per `(stage, provider, model)` under
`data/calibration_checkpoints/`, automatically resuming from previous progress and respecting
active quota cooldown windows across restarts with zero extra CLI toggles.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI with Cooldown-Aware Checkpointing
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle
    - ADR-060: Gap Filler Judge Criteria v2
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import random
import re
import sys
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from statistics import NormalDist
from typing import Any

import click
import typer
from dotenv import load_dotenv

# Ensure `cresmo` resolves cleanly when executed directly via `python scripts/calibrate_judges.py`
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.quality import (
    EvaluationContext,
    JudgeCriterion,
)
from cresmo.infrastructure.adapters.gemini_pool import (
    CredentialPoolExhaustedError,
    is_quota_exhausted_error,
)
from cresmo.infrastructure.adapters.prompts import load_prompt_catalog
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.judge_factory import (
    build_llm_judge_adapter,
)

load_dotenv(REPO_ROOT / ".env", override=False)

DEFAULT_CHECKPOINT_DIR = REPO_ROOT / "data" / "calibration_checkpoints"
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports" / "calibration"
ALL_CALIBRATION_MODELS: list[str] = CresmoSettings().judge_calibration_models


FLUID_PROSE_SEED_DATA: tuple[dict[str, Any], ...] = (
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
)

GAP_FILLER_SEED_DATA: tuple[dict[str, Any], ...] = (
    {
        "id": "eg_seed_01_pass",
        "input": {
            "raw_text": (
                "## A Posse de Afonso Henriques e a Bula Manifestis Probatum\n\n"
                "Afonso Henriques declarou a autonomia do Condado Portucalense no século XII. "
                "Após anos de conflitos contra o Reino de Leão e campanhas da Reconquista, "
                "a corte papal reconheceu formalmente a soberania portuguesa através de documento solene."
            ),
            "candidate_text": (
                "## A Autonomia Feudal e a Legitimação Apostólica do Reino de Portugal\n\n"
                "A consolidação política da independência portucalense articulou vitórias campais "
                "contra os exércitos de Afonso VII de Leão e a inserção direta na rede de suserania da Santa Sé. "
                "Em 1179-05-23, o papa Alexandre III promulgou a bula Manifestis Probatum, "
                "declarando Afonso Henriques rei soberano de Portugal e outorgando proteção apostólica contra "
                "reivindicações anexionistas de monarcas cristãos vizinhos.\n\n"
                "Esse ato diplomático coroou um esforço de décadas iniciado no Tratado de Zamora em 1143-10-05, "
                "subordinando a legitimidade jurídica do novo reino ao pagamento anual de um censo de dois marcos "
                "de ouro à corte romana.\n\n"
                "### Extra Info\n\n"
                "1. O Tratado de Zamora de 1143-10-05 contou com a mediação do cardeal Guido de Vico, legado papal na Península Ibérica.\n"
                "2. O censo pago por Afonso Henriques à Santa Sé foi elevado de quatro onças de ouro anuais em 1144 para dois marcos de ouro em 1179."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "cm_seed_02_fail",
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
                "a arquitetura do PostgreSQL manifesta variações desproporcionais na latência percebida pelos clientes. "
                "A saturação de conexões sem pooling adequado impõe um ônus que degrada o rendimento global "
                "da aplicação sob teste de estresse na infraestrutura em contêineres Docker.\n\n"
                "A degradação manifesta-se através de disputas intensas por recursos compartilhados, onde diferentes "
                "processos disputam o acesso aos mesmos registros de tabelas financeiras. A sobrecarga de gerenciar "
                "dezenas de processos paralelos força o núcleo do sistema operacional a despender ciclos de "
                "processamento em trocas de contexto.\n\n"
                "### Extra Info\n\n"
                "1. O gerenciador de conexões PgBouncer gerencia três modos distintos de agrupamento: sessão, transação e instrução.\n"
                "2. O comando EXPLAIN ANALYZE do PostgreSQL executa a consulta e retorna o plano de execução real juntamente com os custos."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "borderline",
            "expected_anomaly": "explanatory_vacuum_missing_mvcc_intermediate_mechanisms",
            "defect_location": "paragraph_2",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
)


@dataclass(frozen=True, slots=True)
class StageCalibrationSpec:
    """Declarative specification defining calibration behavior for a pipeline stage."""

    stage_name: str
    label: str
    prompt_key: PromptKey
    default_golden_set_path: Path
    required_criteria: tuple[JudgeCriterion, ...]
    seed_items: tuple[dict[str, Any], ...]


STAGE_SPECS: dict[str, StageCalibrationSpec] = {
    "fluid_prose": StageCalibrationSpec(
        stage_name="fluid_prose",
        label="Stage 1: Fluid Prose",
        prompt_key=PromptKey.JUDGE_FLUID_PROSE,
        default_golden_set_path=(
            REPO_ROOT / "scripts" / "fluid_prose" / "golden_sets" / "fluid_prose_golden_set.json"
        ),
        required_criteria=(
            JudgeCriterion.ORALITY_REMOVAL,
            JudgeCriterion.SEMANTIC_FAITHFULNESS,
            JudgeCriterion.EPISTEMIC_CRITIQUE,
            JudgeCriterion.NER_PRESERVATION,
            JudgeCriterion.STRUCTURAL_COMPLIANCE,
            JudgeCriterion.AUTHORIAL_VOICE,
        ),
        seed_items=FLUID_PROSE_SEED_DATA,
    ),
    "gap_filler": StageCalibrationSpec(
        stage_name="gap_filler",
        label="Stage 2: Gap Filler",
        prompt_key=PromptKey.JUDGE_GAP_FILLER,
        default_golden_set_path=(
            REPO_ROOT / "scripts" / "gap_filler" / "golden_sets" / "gap_filler_golden_set.json"
        ),
        required_criteria=(
            JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION,
            JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION,
            JudgeCriterion.BRAUDELIAN_STRATIFICATION,
            JudgeCriterion.GENEALOGY_HIDDEN_AGENCY,
            JudgeCriterion.COMPETING_HYPOTHESES,
            JudgeCriterion.EXTRA_INFO_GRANULARITY,
            JudgeCriterion.LINEAR_STYLE_NATURALISM,
        ),
        seed_items=GAP_FILLER_SEED_DATA,
    ),
}


@dataclass(frozen=True)
class MetricInfo:
    """Conceptual and quantitative metadata for one Signal Detection Theory metric."""

    code: str
    name: str
    math_formula: str
    sheets_formula: str
    value: float
    formatted_value: str
    practical_implication: str
    high_meaning: str
    low_meaning: str
    diagnosis: str


@dataclass
class ConfusionMatrix:
    """Confusion matrix counts and 15 Signal Detection Theory metrics."""

    hit: int = 0
    pedantismo_beta: int = 0
    permissivo_alfa: int = 0
    rejeicao: int = 0
    invalid: int = 0

    @property
    def tp(self) -> int:
        """True Positive (Hit): Ground truth PASS and judge approved."""
        return self.hit

    @property
    def fn(self) -> int:
        """False Negative (Pedantismo-beta): Ground truth PASS and judge rejected."""
        return self.pedantismo_beta

    @property
    def fp(self) -> int:
        """False Positive (Permissivo-alfa): Ground truth FAIL and judge approved."""
        return self.permissivo_alfa

    @property
    def tn(self) -> int:
        """True Negative (Rejeição): Ground truth FAIL and judge rejected."""
        return self.rejeicao

    @property
    def total_corretos(self) -> int:
        """Total ground-truth PASS items."""
        return self.hit + self.pedantismo_beta

    @property
    def total_defeituosos(self) -> int:
        """Total ground-truth FAIL items."""
        return self.permissivo_alfa + self.rejeicao

    @property
    def total_aprovados(self) -> int:
        """Total approvals emitted by judge."""
        return self.hit + self.permissivo_alfa

    @property
    def total_reprovados(self) -> int:
        """Total rejections emitted by judge."""
        return self.pedantismo_beta + self.rejeicao

    @property
    def total_valid(self) -> int:
        """Total evaluated valid items."""
        return self.hit + self.pedantismo_beta + self.permissivo_alfa + self.rejeicao

    @property
    def accuracy(self) -> float:
        """Overall accuracy: (Hit + Rejeição) / Total."""
        return (self.hit + self.rejeicao) / self.total_valid if self.total_valid > 0 else 0.0

    @property
    def precision(self) -> float:
        """Positive Predictive Value: Hit / (Hit + Permissivo-alfa)."""
        denom = self.hit + self.permissivo_alfa
        return self.hit / denom if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        """Sensitivity (TPR): Hit / (Hit + Pedantismo-beta)."""
        denom = self.hit + self.pedantismo_beta
        return self.hit / denom if denom > 0 else 0.0

    @property
    def specificity(self) -> float:
        """True Negative Rate (TNR): Rejeição / (Rejeição + Permissivo-alfa)."""
        denom = self.rejeicao + self.permissivo_alfa
        return self.rejeicao / denom if denom > 0 else 0.0

    @property
    def npv(self) -> float:
        """Negative Predictive Value: Rejeição / (Rejeição + Pedantismo-beta)."""
        denom = self.rejeicao + self.pedantismo_beta
        return self.rejeicao / denom if denom > 0 else 0.0

    @property
    def alpha_fpr(self) -> float:
        """False Positive Rate (Alpha): Permissivo-alfa / (Rejeição + Permissivo-alfa)."""
        denom = self.rejeicao + self.permissivo_alfa
        return self.permissivo_alfa / denom if denom > 0 else 0.0

    @property
    def beta_fnr(self) -> float:
        """False Negative Rate (Beta): Pedantismo-beta / (Hit + Pedantismo-beta)."""
        denom = self.hit + self.pedantismo_beta
        return self.pedantismo_beta / denom if denom > 0 else 0.0

    def _f_beta(self, beta: float) -> float:
        p, r = self.precision, self.recall
        beta_sq = beta * beta
        denom = (beta_sq * p) + r
        return (1.0 + beta_sq) * (p * r) / denom if denom > 0 else 0.0

    @property
    def f05(self) -> float:
        """F0.5 score weighting precision twice as strongly as recall."""
        return self._f_beta(0.5)

    @property
    def f1(self) -> float:
        """F1 score balancing precision and recall equally."""
        return self._f_beta(1.0)

    @property
    def f2(self) -> float:
        """F2 score weighting recall twice as strongly as precision."""
        return self._f_beta(2.0)

    @property
    def lr_plus(self) -> float:
        """Positive Likelihood Ratio: Recall / Alpha FPR."""
        fpr = self.alpha_fpr
        if fpr == 0:
            return float("inf") if self.recall > 0 else 1.0
        return self.recall / fpr

    @property
    def lr_minus(self) -> float:
        """Negative Likelihood Ratio: Beta FNR / Specificity."""
        tnr = self.specificity
        if tnr == 0:
            return float("inf") if self.beta_fnr > 0 else 1.0
        return self.beta_fnr / tnr

    @property
    def mcc(self) -> float:
        """Matthews Correlation Coefficient in [-1.0, +1.0]."""
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
        """Signal Detection Theory sensitivity d' using Macmillan & Creelman clamp."""
        n_signal = self.total_corretos
        n_noise = self.total_defeituosos
        if n_signal == 0 or n_noise == 0:
            return 0.0
        eps_s = 1.0 / (2 * n_signal)
        eps_n = 1.0 / (2 * n_noise)
        h_clamp = min(max(self.hit / n_signal, eps_s), 1.0 - eps_s)
        fa_clamp = min(max(self.permissivo_alfa / n_noise, eps_n), 1.0 - eps_n)
        norm = NormalDist()
        return norm.inv_cdf(h_clamp) - norm.inv_cdf(fa_clamp)

    @property
    def c_bias(self) -> float:
        """Signal Detection Theory response bias c (>0 pedantic, <0 permissive)."""
        n_signal = self.total_corretos
        n_noise = self.total_defeituosos
        if n_signal == 0 or n_noise == 0:
            return 0.0
        eps_s = 1.0 / (2 * n_signal)
        eps_n = 1.0 / (2 * n_noise)
        h_clamp = min(max(self.hit / n_signal, eps_s), 1.0 - eps_s)
        fa_clamp = min(max(self.permissivo_alfa / n_noise, eps_n), 1.0 - eps_n)
        norm = NormalDist()
        return -0.5 * (norm.inv_cdf(h_clamp) + norm.inv_cdf(fa_clamp))

    def record(self, expected: str, actual: str) -> str:
        """Record expected vs actual verdict pair and return canonical status code."""
        if expected not in ("PASS", "FAIL"):
            self.invalid += 1
            return "INVALID"
        if expected == "PASS" and actual == "PASS":
            self.hit += 1
            return "HIT"
        if expected == "FAIL" and actual == "FAIL":
            self.rejeicao += 1
            return "REJEICAO"
        if expected == "FAIL" and actual == "PASS":
            self.permissivo_alfa += 1
            return "PERMISSIVO_ALFA"
        self.pedantismo_beta += 1
        return "PEDANTISMO_BETA"

    def get_all_metrics(self) -> list[MetricInfo]:
        """Return full diagnostic breakdown across all 15 SDT metrics."""
        lr_plus_val = self.lr_plus
        lr_minus_val = self.lr_minus
        mcc_val = self.mcc
        dp_val = self.d_prime
        c_val = self.c_bias

        lr_plus_str = f"{lr_plus_val:.2f}" if lr_plus_val != float("inf") else "Inf"
        lr_minus_str = f"{lr_minus_val:.2f}" if lr_minus_val != float("inf") else "Inf"
        c_diag = (
            f"Pedantic/conservative (+{c_val:.2f})"
            if c_val > 0.15
            else f"Permissive/liberal ({c_val:.2f})"
            if c_val < -0.15
            else f"Balanced/neutral ({c_val:.2f})"
        )

        return [
            MetricInfo(
                code="a)",
                name="Accuracy",
                math_formula="(Hit + Rejeicao) / Total",
                sheets_formula="=(B4+C5)/D6",
                value=self.accuracy,
                formatted_value=f"{self.accuracy * 100:.1f}%",
                practical_implication="Overall proportion of correct verdicts.",
                high_meaning="Most decisions align with ground truth.",
                low_meaning="Judge frequently misclassifies items.",
                diagnosis="Acceptable (>=80%)"
                if self.accuracy >= 0.80
                else "Below baseline (<80%)",
            ),
            MetricInfo(
                code="b)",
                name="Precision / PPV",
                math_formula="Hit / (Hit + Permissivo-alfa)",
                sheets_formula="=B4/B6",
                value=self.precision,
                formatted_value=f"{self.precision * 100:.1f}%",
                practical_implication="Purity of PASS verdicts.",
                high_meaning="Approvals rarely pass defective candidates.",
                low_meaning="Defective candidates leak through PASS gate.",
                diagnosis="Pure (>=80%)" if self.precision >= 0.80 else "Leaky (<80%)",
            ),
            MetricInfo(
                code="c)",
                name="Recall / Sensitivity",
                math_formula="Hit / (Hit + Pedantismo-beta)",
                sheets_formula="=B4/D4",
                value=self.recall,
                formatted_value=f"{self.recall * 100:.1f}%",
                practical_implication="Share of valid candidates approved.",
                high_meaning="Minimal false rejections of valid work.",
                low_meaning="Judge is overly pedantic and discards valid work.",
                diagnosis="Healthy (>=85%)" if self.recall >= 0.85 else "Pedantic (<85%)",
            ),
            MetricInfo(
                code="d)",
                name="Specificity (TNR)",
                math_formula="Rejeicao / (Rejeicao + Permissivo-alfa)",
                sheets_formula="=C5/D5",
                value=self.specificity,
                formatted_value=f"{self.specificity * 100:.1f}%",
                practical_implication="Share of defective candidates caught.",
                high_meaning="Strong gate against defects.",
                low_meaning="Defects bypass rejection.",
                diagnosis="Effective (>=70%)" if self.specificity >= 0.70 else "Weak (<70%)",
            ),
            MetricInfo(
                code="e)",
                name="NPV",
                math_formula="Rejeicao / (Rejeicao + Pedantismo-beta)",
                sheets_formula="=C5/C6",
                value=self.npv,
                formatted_value=f"{self.npv * 100:.1f}%",
                practical_implication="Reliability of FAIL verdicts.",
                high_meaning="Rejections correspond to real defects.",
                low_meaning="Many valid candidates are rejected.",
                diagnosis="Reliable (>=75%)" if self.npv >= 0.75 else "Noisy (<75%)",
            ),
            MetricInfo(
                code="f)",
                name="Alpha Rate (FPR)",
                math_formula="Permissivo-alfa / (Rejeicao + Permissivo-alfa)",
                sheets_formula="=B5/D5",
                value=self.alpha_fpr,
                formatted_value=f"{self.alpha_fpr * 100:.1f}%",
                practical_implication="Rate of defective texts leaking through.",
                high_meaning="Unacceptable defect leakage.",
                low_meaning="Hermetic quality filter.",
                diagnosis="Low leak (<=20%)" if self.alpha_fpr <= 0.20 else "High leak (>20%)",
            ),
            MetricInfo(
                code="g)",
                name="Beta Rate (FNR)",
                math_formula="Pedantismo-beta / (Hit + Pedantismo-beta)",
                sheets_formula="=C4/D4",
                value=self.beta_fnr,
                formatted_value=f"{self.beta_fnr * 100:.1f}%",
                practical_implication="Rate of valid texts wasted in retries.",
                high_meaning="Excessive self-healing churn.",
                low_meaning="Low pedantry.",
                diagnosis="Low churn (<=15%)" if self.beta_fnr <= 0.15 else "High churn (>15%)",
            ),
            MetricInfo(
                code="h)",
                name="F0.5-Score",
                math_formula="1.25 * (P * R) / (0.25 * P + R)",
                sheets_formula="=(1+H17^2)*(D$11*D$12)/((H17^2*D$11)+D$12)",
                value=self.f05,
                formatted_value=f"{self.f05 * 100:.1f}%",
                practical_implication="Precision-weighted harmonic mean (2x Precision).",
                high_meaning="Strong fidelity and low permissiveness.",
                low_meaning="Leaked defects degraded gate purity.",
                diagnosis="Strong (>=80%)" if self.f05 >= 0.80 else "Weak (<80%)",
            ),
            MetricInfo(
                code="i)",
                name="F1-Score",
                math_formula="2 * (P * R) / (P + R)",
                sheets_formula="=(1+H18^2)*(D$11*D$12)/((H18^2*D$11)+D$12)",
                value=self.f1,
                formatted_value=f"{self.f1 * 100:.1f}%",
                practical_implication="Balanced harmonic mean of Precision and Recall.",
                high_meaning="Well-balanced discrimination.",
                low_meaning="Precision/Recall imbalance or weak discrimination.",
                diagnosis="Balanced (>=80%)" if self.f1 >= 0.80 else "Unbalanced (<80%)",
            ),
            MetricInfo(
                code="j)",
                name="F2-Score",
                math_formula="5 * (P * R) / (4 * P + R)",
                sheets_formula="=(1+H19^2)*(D$11*D$12)/((H19^2*D$11)+D$12)",
                value=self.f2,
                formatted_value=f"{self.f2 * 100:.1f}%",
                practical_implication="Recall-weighted harmonic mean (2x Recall).",
                high_meaning="Preserves nearly all valid texts.",
                low_meaning="Pedantry discards too much valid output.",
                diagnosis="Preserving (>=85%)" if self.f2 >= 0.85 else "Restrictive (<85%)",
            ),
            MetricInfo(
                code="k)",
                name="LR+",
                math_formula="Sensitivity / (1 - Specificity)",
                sheets_formula="=(B4/D4)/(B5/D5)",
                value=lr_plus_val,
                formatted_value=lr_plus_str,
                practical_implication="Evidentiary weight of a PASS decision.",
                high_meaning="Strong confirmation of quality (>10).",
                low_meaning="Weak confirmation (<2).",
                diagnosis=(
                    "Strong (>=10)"
                    if lr_plus_val >= 10.0
                    else "Moderate (2-10)"
                    if lr_plus_val >= 2.0
                    else "Weak (<2)"
                ),
            ),
            MetricInfo(
                code="l)",
                name="LR-",
                math_formula="(1 - Sensitivity) / Specificity",
                sheets_formula="=(C4/D4)/(C5/D5)",
                value=lr_minus_val,
                formatted_value=lr_minus_str,
                practical_implication="Evidentiary weight of a FAIL decision.",
                high_meaning="Inconclusive rejection (>0.5).",
                low_meaning="Definitive defect confirmation (<0.1).",
                diagnosis=(
                    "Definitive (<=0.1)"
                    if lr_minus_val <= 0.10
                    else "Moderate (0.1-0.5)"
                    if lr_minus_val <= 0.50
                    else "Inconclusive (>0.5)"
                ),
            ),
            MetricInfo(
                code="m)",
                name="Matthews Correlation (MCC)",
                math_formula="((Hit * Rej) - (Alfa * Beta)) / SQRT(...)",
                sheets_formula="=((B4*C5)-(B5*C4))/SQRT(B6*D4*D5*C6)",
                value=mcc_val,
                formatted_value=f"{mcc_val:+.3f}",
                practical_implication="Full confusion matrix correlation in [-1, +1].",
                high_meaning="Strong alignment with ground truth.",
                low_meaning="Random or inverted alignment (<=0).",
                diagnosis=(
                    "Strong (>=0.60)"
                    if mcc_val >= 0.60
                    else "Moderate (>0.20)"
                    if mcc_val > 0.20
                    else "Poor (<=0.20)"
                ),
            ),
            MetricInfo(
                code="n)",
                name="D-prime (d')",
                math_formula="NORM.S.INV(HitRate) - NORM.S.INV(FARate)",
                sheets_formula="=NORM.S.INV(B4/D4)-NORM.S.INV(B5/D5)",
                value=dp_val,
                formatted_value=f"{dp_val:.2f}",
                practical_implication="Intrinsic signal-vs-noise discrimination acuity.",
                high_meaning="Excellent discrimination (>=2.0).",
                low_meaning="Inability to separate valid vs defective (~0).",
                diagnosis=(
                    "Excellent (>=2.0)"
                    if dp_val >= 2.0
                    else "Moderate (>=1.0)"
                    if dp_val >= 1.0
                    else "Poor (<1.0)"
                ),
            ),
            MetricInfo(
                code="o)",
                name="Criterion c (Bias)",
                math_formula="-0.5 * (NORM.S.INV(HitRate) + NORM.S.INV(FARate))",
                sheets_formula="=-0.5*(NORM.S.INV(B4/D4)+NORM.S.INV(B5/D5))",
                value=c_val,
                formatted_value=f"{c_val:+.2f}",
                practical_implication="Systematic decision threshold bias.",
                high_meaning="Pedantic/conservative (+).",
                low_meaning="Permissive/liberal (-).",
                diagnosis=c_diag,
            ),
        ]


@dataclass
class CalibrationResultSet:
    """Aggregated calibration results across global, isolated-target, and slice matrices."""

    overall: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    target_isolated: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    by_criterion: dict[str, ConfusionMatrix] = field(default_factory=dict)
    by_difficulty: dict[str, ConfusionMatrix] = field(default_factory=dict)
    disagreements: list[dict[str, Any]] = field(default_factory=list)
    evaluated_items: int = 0
    skipped_from_checkpoint: int = 0

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
    """Evaluation result supporting 4-tuple unpacking and target-criterion slicing."""

    actual: str
    expected: str
    score: float
    reasoning: str
    target_actual: str = ""
    target_score: float = 0.0

    def __iter__(self) -> Iterator[Any]:
        """Enable unpacking as `(actual, expected, score, reasoning)`."""
        yield self.actual
        yield self.expected
        yield self.score
        yield self.reasoning


@dataclass(frozen=True)
class ModelBenchmarkSummary:
    """Consolidated cross-stage/model outcome for terminal summary matrix."""

    stage: str
    provider: str
    model: str
    status: str
    accuracy: float = 0.0
    d_prime: float = 0.0
    f1: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    alpha_fpr: float = 0.0
    evaluated_total: int = 0
    dataset_total: int = 0
    cooldown_remaining_s: float = 0.0
    error_message: str = ""


class CalibrationCheckpointStore:
    """Atomic JSON checkpoint and cooldown manager under `data/calibration_checkpoints/`.

    Persists evaluated items per `(stage, provider, model)` bound to `config_hash` and
    tracks cooldown expiration per `(stage, provider, model)` plus shared `(provider, model)`
    rate/quota limits so subsequent runs resume cleanly without wasted calls.
    """

    def __init__(self, checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR) -> None:
        self.checkpoint_dir = checkpoint_dir

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", value.strip())

    def _target_path(self, stage: str, provider: str, model: str) -> Path:
        filename = f"{self._slug(stage)}__{self._slug(provider)}__{self._slug(model)}.json"
        return self.checkpoint_dir / filename

    @property
    def _cooldowns_path(self) -> Path:
        return self.checkpoint_dir / "cooldowns.json"

    @staticmethod
    def _shared_key(provider: str, model: str) -> str:
        return f"{provider.strip().lower()}:{model.strip()}"

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
        return raw if isinstance(raw, dict) else {}

    def _write_json_atomic(self, path: Path, payload: dict[str, Any]) -> None:
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(tmp_path, path)

    def load_completed_items(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
    ) -> dict[str, dict[str, Any]]:
        """Load checkpointed item verdicts only when `config_hash` matches current config."""
        data = self._read_json(self._target_path(stage, provider, model))
        if not data or data.get("config_hash") != config_hash:
            return {}
        items = data.get("items")
        if not isinstance(items, dict):
            return {}
        return {str(k): v for k, v in items.items() if isinstance(v, dict)}

    def record_item(
        self,
        stage: str,
        provider: str,
        model: str,
        config_hash: str,
        item_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Atomically append or update one evaluated item in the target checkpoint file."""
        path = self._target_path(stage, provider, model)
        existing = self._read_json(path)
        if existing.get("config_hash") != config_hash:
            items: dict[str, Any] = {}
        else:
            raw_items = existing.get("items")
            items = dict(raw_items) if isinstance(raw_items, dict) else {}
        items[item_id] = payload
        updated: dict[str, Any] = {
            "stage": stage,
            "provider": provider,
            "model": model,
            "config_hash": config_hash,
            "updated_at": datetime.now(UTC).isoformat(),
            "items": items,
        }
        if isinstance(existing.get("cooldown_until"), int | float):
            updated["cooldown_until"] = float(existing["cooldown_until"])
        self._write_json_atomic(path, updated)

    def record_cooldown(
        self,
        stage: str,
        provider: str,
        model: str,
        until_ts: float,
    ) -> None:
        """Persist cooldown expiration timestamp for `(stage, provider, model)` and shared model."""
        path = self._target_path(stage, provider, model)
        existing = self._read_json(path)
        existing.setdefault("stage", stage)
        existing.setdefault("provider", provider)
        existing.setdefault("model", model)
        prev_target_cd = existing.get("cooldown_until")
        if isinstance(prev_target_cd, int | float):
            existing["cooldown_until"] = max(float(prev_target_cd), until_ts)
        else:
            existing["cooldown_until"] = until_ts
        self._write_json_atomic(path, existing)

        cooldowns = self._read_json(self._cooldowns_path)
        shared_key = self._shared_key(provider, model)
        prev_shared = cooldowns.get(shared_key)
        if isinstance(prev_shared, int | float):
            cooldowns[shared_key] = max(float(prev_shared), until_ts)
        else:
            cooldowns[shared_key] = until_ts
        self._write_json_atomic(self._cooldowns_path, cooldowns)

    def active_cooldown_until(
        self,
        stage: str,
        provider: str,
        model: str,
        now: float | None = None,
    ) -> float | None:
        """Return future cooldown epoch timestamp if still active, else None."""
        current_now = time.time() if now is None else now
        candidates: list[float] = []

        target_data = self._read_json(self._target_path(stage, provider, model))
        target_cd = target_data.get("cooldown_until")
        if isinstance(target_cd, int | float) and float(target_cd) > current_now:
            candidates.append(float(target_cd))

        cooldowns = self._read_json(self._cooldowns_path)
        shared_cd = cooldowns.get(self._shared_key(provider, model))
        if isinstance(shared_cd, int | float) and float(shared_cd) > current_now:
            candidates.append(float(shared_cd))

        return max(candidates) if candidates else None

    def clear_cooldown(self, stage: str, provider: str, model: str) -> None:
        """Clear cooldown metadata after target completes cleanly."""
        path = self._target_path(stage, provider, model)
        target_data = self._read_json(path)
        if "cooldown_until" in target_data:
            target_data.pop("cooldown_until", None)
            self._write_json_atomic(path, target_data)

        cooldowns = self._read_json(self._cooldowns_path)
        shared_key = self._shared_key(provider, model)
        if shared_key in cooldowns:
            cooldowns.pop(shared_key, None)
            self._write_json_atomic(self._cooldowns_path, cooldowns)


def resolve_model_spec(spec: str, default_provider: str = "gemini") -> tuple[str, str]:
    """Parse model specification string into canonical `(provider, model_name)` tuple."""
    cleaned = spec.strip()
    if ":" in cleaned:
        provider, model_name = cleaned.split(":", 1)
        return provider.strip().lower(), model_name.strip()
    lower = cleaned.lower()
    if lower.startswith("gemini"):
        return "gemini", cleaned
    if lower.startswith("ollama"):
        return "ollama", cleaned
    if lower.startswith("typesafe"):
        return "typesafe", cleaned
    return default_provider.strip().lower(), cleaned


def parse_stage_specs(
    stages: list[str] | None,
    single_stage: str | None,
) -> list[str]:
    """Expand stage flags supporting comma-separated values or repeated `--stages` flags."""
    raw_tokens: list[str] = []
    if stages:
        for entry in stages:
            raw_tokens.extend(part.strip() for part in entry.split(",") if part.strip())
    if single_stage is not None:
        raw_tokens.extend(part.strip() for part in single_stage.split(",") if part.strip())

    if not raw_tokens or "all" in [t.lower() for t in raw_tokens]:
        return list(STAGE_SPECS.keys())

    resolved: list[str] = []
    for token in raw_tokens:
        norm = token.lower().replace("-", "_")
        if norm not in STAGE_SPECS:
            valid = ", ".join(STAGE_SPECS.keys())
            raise typer.BadParameter(f"Unknown stage '{token}'. Valid stages: {valid}, all.")
        if norm not in resolved:
            resolved.append(norm)
    return resolved


def parse_model_specs(
    models: list[str] | None,
    single_model: str | None,
    default_provider: str = "gemini",
) -> list[tuple[str, str]]:
    """Expand model flags or `CresmoSettings().judge_calibration_models` into `(provider, model)` pairs."""
    raw_tokens: list[str] = []
    if models:
        for entry in models:
            raw_tokens.extend(part.strip() for part in entry.split(",") if part.strip())
    elif single_model is not None and single_model.strip():
        raw_tokens.append(single_model.strip())
    else:
        raw_tokens.extend(CresmoSettings().judge_calibration_models)

    resolved: list[tuple[str, str]] = []
    for token in raw_tokens:
        pair = resolve_model_spec(token, default_provider=default_provider)
        if pair not in resolved:
            resolved.append(pair)
    return resolved


def sanitize_report_filename(stage: str, provider: str, model_name: str) -> str:
    """Generate clean filename slug for per-stage, per-model calibration report."""
    clean_model = model_name
    if clean_model.startswith(f"{provider}:"):
        clean_model = clean_model[len(provider) + 1 :]
    clean_model = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean_model.replace(":", "_").replace("/", "_"))
    return f"llm_judge_{stage}_{provider}_{clean_model}.txt"


def compute_config_hash(
    spec: StageCalibrationSpec,
    items: list[dict[str, Any]],
    threshold: float,
) -> str:
    """Compute SHA-256 hash over prompt template, criteria, threshold, and golden set items."""
    prompt_payload: dict[str, str] = {"system_prompt": "", "user_prompt": ""}
    try:
        catalog = load_prompt_catalog()
        if spec.prompt_key in catalog:
            prompt_spec = catalog[spec.prompt_key]
            prompt_payload = {
                "system_prompt": prompt_spec.system_prompt,
                "user_prompt": prompt_spec.user_prompt,
            }
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).debug("Prompt catalog unavailable for config hash: %s", exc)

    canonical = {
        "stage": spec.stage_name,
        "threshold": round(threshold, 6),
        "required_criteria": [c.value for c in spec.required_criteria],
        "prompt": prompt_payload,
        "items": items,
    }
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_stage_dataset(
    spec: StageCalibrationSpec,
    dataset_path: Path | None,
    seed_only: bool,
) -> list[dict[str, Any]]:
    """Load golden set JSON list for a stage or fall back to canonical seed items."""
    if seed_only:
        return [dict(item) for item in spec.seed_items]

    target_path = dataset_path if dataset_path is not None else spec.default_golden_set_path
    if not target_path.exists():
        return [dict(item) for item in spec.seed_items]

    loaded = json.loads(target_path.read_text(encoding="utf-8"))
    if isinstance(loaded, list) and loaded:
        return [dict(item) for item in loaded]
    return [dict(item) for item in spec.seed_items]


def evaluate_single_item(
    judge: Any,
    spec: StageCalibrationSpec,
    item: dict[str, Any],
) -> ItemEvaluationResult:
    """Invoke `judge.evaluate` for one golden set item uniformly across stages."""
    raw_text = item["input"]["raw_text"]
    candidate_text = item["input"]["candidate_text"]
    expected_verdict = str(item["expected_output"]["verdict"]).upper().strip()
    target_criterion_name = str(item.get("metadata", {}).get("criterion", "")).strip()

    context = EvaluationContext(
        stage_name=spec.stage_name,
        raw_text=raw_text,
        candidate_text=candidate_text,
        required_criteria=spec.required_criteria,
    )

    evaluation = judge.evaluate(context)
    global_actual = "PASS" if evaluation.passed else "FAIL"
    global_score = float(evaluation.overall_score)
    reasoning = evaluation.extract_critique()

    target_actual = global_actual
    target_score = global_score
    if target_criterion_name:
        try:
            crit_vo = JudgeCriterion(target_criterion_name)
            crit_score = evaluation.get_score(crit_vo)
            if crit_score is not None:
                target_actual = "PASS" if crit_score.passed else "FAIL"
                target_score = float(crit_score.score)
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


def _record_item_into_results(
    results: CalibrationResultSet,
    item: dict[str, Any],
    eval_res: ItemEvaluationResult,
) -> str:
    """Record item verdict into global, target-isolated, and slice confusion matrices."""
    item_id = str(item.get("id", "item"))
    metadata = item.get("metadata", {})
    criterion = str(metadata.get("criterion", "general"))
    difficulty = str(metadata.get("difficulty", "typical"))

    if criterion not in results.by_criterion:
        results.by_criterion[criterion] = ConfusionMatrix()
    if difficulty not in results.by_difficulty:
        results.by_difficulty[difficulty] = ConfusionMatrix()

    results.overall.record(eval_res.expected, eval_res.actual)
    status_target = results.target_isolated.record(eval_res.expected, eval_res.target_actual)
    results.by_criterion[criterion].record(eval_res.expected, eval_res.target_actual)
    results.by_difficulty[difficulty].record(eval_res.expected, eval_res.target_actual)

    if eval_res.expected != eval_res.target_actual:
        results.disagreements.append(
            {
                "id": item_id,
                "criterion": criterion,
                "difficulty": difficulty,
                "expected": eval_res.expected,
                "actual_target": eval_res.target_actual,
                "actual_global": eval_res.actual,
                "score": eval_res.target_score,
                "anomaly": metadata.get("expected_anomaly", ""),
                "reasoning": eval_res.reasoning,
            }
        )
    return status_target


def _is_transient_retryable_error(exc: Exception) -> bool:
    """Identify transient server/network failures worth bounded retry backoff."""
    if is_quota_exhausted_error(exc):
        return False
    msg = str(exc).lower()
    transient_markers = ("503", "504", "unavailable", "timeout", "connection reset", "timed out")
    return any(marker in msg for marker in transient_markers)


def run_stage_calibration(
    judge: Any,
    spec: StageCalibrationSpec,
    items: list[dict[str, Any]],
    *,
    provider: str,
    model: str,
    config_hash: str,
    checkpoint_store: CalibrationCheckpointStore,
    delay: float = 4.2,
    jitter: float = 0.8,
    max_retry_wait: float = 60.0,
    now_fn: Callable[[], float] = time.time,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> CalibrationResultSet:
    """Run incremental checkpointed calibration for one `(stage, provider, model)` target."""
    active_until = checkpoint_store.active_cooldown_until(
        stage=spec.stage_name,
        provider=provider,
        model=model,
        now=now_fn(),
    )
    if active_until is not None:
        remaining = max(0.0, active_until - now_fn())
        raise CredentialPoolExhaustedError(
            retry_after_seconds=remaining,
            message=f"Cooldown active for {provider}:{model} ({remaining:.0f}s remaining).",
        )

    results = CalibrationResultSet()
    completed_map = checkpoint_store.load_completed_items(
        stage=spec.stage_name,
        provider=provider,
        model=model,
        config_hash=config_hash,
    )

    pending_items: list[dict[str, Any]] = []
    for item in items:
        item_id = str(item.get("id", "item"))
        saved = completed_map.get(item_id)
        if saved is not None:
            saved_eval = ItemEvaluationResult(
                actual=str(saved["actual"]),
                expected=str(saved["expected"]),
                score=float(saved["score"]),
                reasoning=str(saved.get("reasoning", "")),
                target_actual=str(saved.get("target_actual", saved["actual"])),
                target_score=float(saved.get("target_score", saved["score"])),
            )
            _record_item_into_results(results, item, saved_eval)
            results.skipped_from_checkpoint += 1
        else:
            pending_items.append(item)

    total_items = len(items)
    print("\n" + "=" * 72)
    print(f"CALIBRATING [{spec.stage_name.upper()}] -> {provider}:{model}")
    if results.skipped_from_checkpoint > 0:
        print(
            f"Checkpoint resume: {results.skipped_from_checkpoint}/{total_items} restored, "
            f"{len(pending_items)} pending."
        )
    if delay > 0 and pending_items:
        print(f"Pacing: {delay:.1f}s base delay + up to {jitter:.1f}s jitter between calls")
    print("=" * 72)

    for idx, item in enumerate(pending_items, start=1):
        item_id = str(item.get("id", f"item_{idx}"))
        eval_res: ItemEvaluationResult | None = None
        short_cooldown_attempts = 0
        transient_attempts = 0

        while True:
            try:
                eval_res = evaluate_single_item(judge, spec, item)
                break
            except CredentialPoolExhaustedError as exc:
                if exc.retry_after_seconds <= max_retry_wait and short_cooldown_attempts < 5:
                    short_cooldown_attempts += 1
                    wait_s = max(exc.retry_after_seconds, 0.5) + 0.5
                    print(
                        f"  [COOLDOWN WAIT {short_cooldown_attempts}/5] {item_id}: "
                        f"waiting {wait_s:.1f}s ({exc})"
                    )
                    sleep_fn(wait_s)
                    continue
                until_ts = now_fn() + max(exc.retry_after_seconds, max_retry_wait)
                checkpoint_store.record_cooldown(spec.stage_name, provider, model, until_ts)
                print(
                    f"  [COOLDOWN ABORT] {spec.stage_name} | {provider}:{model} parked for "
                    f"{exc.retry_after_seconds:.0f}s (checkpoint saved)."
                )
                raise
            except Exception as exc:
                if _is_transient_retryable_error(exc) and transient_attempts < 3:
                    transient_attempts += 1
                    backoff = (2.0**transient_attempts) * 1.5
                    print(
                        f"  [RETRY {transient_attempts}/3] Transient error on '{item_id}': "
                        f"{exc}. Waiting {backoff:.1f}s..."
                    )
                    sleep_fn(backoff)
                    continue
                raise

        assert eval_res is not None
        checkpoint_store.record_item(
            stage=spec.stage_name,
            provider=provider,
            model=model,
            config_hash=config_hash,
            item_id=item_id,
            payload={
                "actual": eval_res.actual,
                "expected": eval_res.expected,
                "score": eval_res.score,
                "reasoning": eval_res.reasoning,
                "target_actual": eval_res.target_actual,
                "target_score": eval_res.target_score,
            },
        )
        status_target = _record_item_into_results(results, item, eval_res)
        results.evaluated_items += 1

        print(
            f"[{results.skipped_from_checkpoint + idx:02d}/{total_items:02d}] "
            f"[{item_id:<28}] Exp: {eval_res.expected:<4} | "
            f"Target: {eval_res.target_actual:<4} ({eval_res.target_score:.2f}) -> {status_target}"
        )

        if idx < len(pending_items) and (delay + jitter) > 0:
            sleep_fn(delay + random.uniform(0.0, jitter))

    checkpoint_store.clear_cooldown(spec.stage_name, provider, model)
    return results


def _format_matrix_2x2(title: str, m: ConfusionMatrix) -> str:
    lines = [
        "\n" + "=" * 80,
        title,
        "-" * 80,
        f"{'Ground Truth \\ Judge':<28} | {'Judge: PASS':<20} | {'Judge: FAIL':<20} | {'Total':<8}",
        "-" * 80,
        (
            f"{'PASS (Valid Output)':<28} | "
            f"{f'HIT (TP): {m.hit}':<20} | "
            f"{f'PEDANT (FN): {m.pedantismo_beta}':<20} | "
            f"{m.total_corretos:<8}"
        ),
        (
            f"{'FAIL (Defective Output)':<28} | "
            f"{f'PERMISSIVE (FP): {m.permissivo_alfa}':<20} | "
            f"{f'REJECT (TN): {m.rejeicao}':<20} | "
            f"{m.total_defeituosos:<8}"
        ),
        "-" * 80,
        f"{'Total by Judge':<28} | {m.total_aprovados:<20} | {m.total_reprovados:<20} | {m.total_valid:<8}",
        "=" * 80,
    ]
    return "\n".join(lines)


def generate_calibration_report(
    spec: StageCalibrationSpec,
    results: CalibrationResultSet,
    provider: str,
    model: str,
) -> str:
    """Build full Signal Detection Theory and slice calibration report."""
    target_m = results.target_isolated
    lines: list[str] = [
        "=" * 80,
        f"LLM JUDGE CALIBRATION REPORT ({spec.label.upper()})",
        "=" * 80,
        f"Timestamp:       {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Stage:           {spec.stage_name}",
        f"Provider:        {provider}",
        f"Model:           {model}",
        "Fallback Mode:   DISABLED (enable_fallback=False)",
        (
            f"Valid Items:     {target_m.total_valid} "
            f"(fresh={results.evaluated_items}, resumed={results.skipped_from_checkpoint})"
        ),
        _format_matrix_2x2(
            "2x2 CONFUSION MATRIX (ISOLATED TARGET CRITERION)",
            target_m,
        ),
        "\n" + "=" * 80,
        "15 SIGNAL DETECTION THEORY (SDT) METRICS (TARGET ISOLATED)",
        "-" * 80,
        f"{'Code':<4} {'Metric':<28} | {'Value':<10} | {'Diagnosis'}",
        "-" * 80,
    ]
    for info in target_m.get_all_metrics():
        lines.append(
            f"{info.code:<4} {info.name:<28} | {info.formatted_value:<10} | {info.diagnosis}"
        )

    lines.append(
        _format_matrix_2x2(
            "2x2 CONFUSION MATRIX (GLOBAL COMPOSITE GATE)",
            results.overall,
        )
    )

    lines.extend(
        [
            "\n" + "=" * 80,
            "SLICE BREAKDOWN BY CRITERION",
            "-" * 80,
            f"{'Criterion':<34} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'d-prime':<7}",
            "-" * 80,
        ]
    )
    for crit, m in results.by_criterion.items():
        lines.append(
            f"{crit:<34} | {m.total_valid:<4} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    lines.extend(
        [
            "\n" + "=" * 80,
            "SLICE BREAKDOWN BY DIFFICULTY",
            "-" * 80,
            f"{'Difficulty':<18} | {'N':<4} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'d-prime':<7}",
            "-" * 80,
        ]
    )
    for diff, m in results.by_difficulty.items():
        lines.append(
            f"{diff:<18} | {m.total_valid:<4} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    if results.disagreements:
        lines.extend(["\n" + "=" * 80, "DISAGREEMENTS", "-" * 80])
        for d in results.disagreements:
            lines.append(
                f"[{d['id']}] crit={d['criterion']} diff={d['difficulty']} "
                f"exp={d['expected']} got={d['actual_target']} ({d['score']:.2f}): "
                f"{str(d['reasoning'])[:180]}"
            )

    return "\n".join(lines) + "\n"


def save_calibration_report(
    spec: StageCalibrationSpec,
    results: CalibrationResultSet,
    output_path: Path,
    provider: str,
    model: str,
) -> Path:
    """Write full calibration report to disk cleanly."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_text = generate_calibration_report(spec, results, provider=provider, model=model)
    output_path.write_text(report_text, encoding="utf-8")
    return output_path


def _print_benchmark_summary(summaries: list[ModelBenchmarkSummary]) -> None:
    """Print cross-stage, cross-model comparison table without polluting cooldown rows."""
    print("\n" + "=" * 116)
    print("UNIFIED LLM JUDGE CALIBRATION SUMMARY (ZERO-FALLBACK)")
    print("=" * 116)
    print(
        f"{'Stage':<12} | {'Model':<32} | {'Status':<11} | {'Done':<7} | "
        f"{'Acc':<6} | {'d-prime':<7} | {'F1':<6} | {'Prec':<6} | {'Rec':<6} | {'FPR':<6}"
    )
    print("-" * 116)
    for s in summaries:
        label = f"{s.provider}:{s.model}"
        done = f"{s.evaluated_total}/{s.dataset_total}"
        if s.status in ("COOLDOWN", "ERRO"):
            extra = (
                f"retry in {int(s.cooldown_remaining_s)}s"
                if s.status == "COOLDOWN"
                else s.error_message[:32]
            )
            print(f"{s.stage:<12} | {label:<32} | {s.status:<11} | {done:<7} | {extra}")
        else:
            print(
                f"{s.stage:<12} | {label:<32} | {s.status:<11} | {done:<7} | "
                f"{s.accuracy * 100:5.1f}% | {s.d_prime:7.2f} | {s.f1:6.3f} | "
                f"{s.precision * 100:5.1f}% | {s.recall * 100:5.1f}% | {s.alpha_fpr * 100:5.1f}%"
            )
    print("=" * 116 + "\n")


app = typer.Typer(
    name="calibrate-judges",
    help=(
        "Unified zero-fallback LLM Judge calibration harness across pipeline stages. "
        "Always resumes incrementally from checkpoints and skips models in cooldown."
    ),
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def run_cli(
    stages: list[str] | None = typer.Option(
        None,
        "--stages",
        help="Stages to calibrate (comma-separated or repeated: fluid_prose, gap_filler, all).",
    ),
    stage: str | None = typer.Option(
        None,
        "--stage",
        help="Single stage override (e.g. fluid_prose or gap_filler).",
    ),
    models: list[str] | None = typer.Option(
        None,
        "--models",
        help="Models to benchmark (comma-separated or repeated, e.g. gemini:gemini-4-hydrogen).",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        help="Single model override (e.g. gemini:gemini-3.8-flash).",
    ),
    provider: str = typer.Option(
        "gemini",
        "--provider",
        help="Default provider prefix when a model spec omits 'provider:'.",
    ),
    threshold: float | None = typer.Option(
        None,
        "--threshold",
        help="Explicit judge pass threshold override.",
    ),
    dataset_path: Path | None = typer.Option(
        None,
        "--dataset-path",
        help="Explicit golden set JSON path (valid only when calibrating one stage).",
    ),
    seed_only: bool = typer.Option(
        False,
        "--seed-only",
        help="Run built-in seed calibration items instead of full golden set files.",
    ),
    delay: float = typer.Option(
        4.2,
        "--delay",
        help="Base pacing delay in seconds between fresh LLM calls.",
    ),
    jitter: float = typer.Option(
        0.8,
        "--jitter",
        help="Random additional pacing jitter in seconds.",
    ),
    max_retry_wait: float = typer.Option(
        60.0,
        "--max-retry-wait",
        help="Max seconds to wait in-place on short cooldowns before parking in COOLDOWN.",
    ),
    output_path: Path | None = typer.Option(
        None,
        "--output-path",
        help="Explicit output directory (multi-target) or file path (single target).",
    ),
) -> None:
    """Execute unified zero-fallback calibration across selected stages and models."""
    selected_stages = parse_stage_specs(stages, stage)
    selected_models = parse_model_specs(models, model, default_provider=provider)
    if dataset_path is not None and len(selected_stages) > 1:
        raise typer.BadParameter("--dataset-path can only be used with a single --stage.")

    base_settings = CresmoSettings()
    checkpoint_store = CalibrationCheckpointStore(checkpoint_dir=DEFAULT_CHECKPOINT_DIR)
    summaries: list[ModelBenchmarkSummary] = []
    has_errors = False

    print(f"\nStages scheduled ({len(selected_stages)}): {', '.join(selected_stages)}")
    print(
        f"Models scheduled ({len(selected_models)}): "
        f"{', '.join(f'{p}:{m}' for p, m in selected_models)}"
    )

    for stage_name in selected_stages:
        spec = STAGE_SPECS[stage_name]
        items = load_stage_dataset(spec, dataset_path=dataset_path, seed_only=seed_only)
        active_threshold = (
            threshold
            if threshold is not None
            else (
                base_settings.gap_filler_judge_threshold
                if stage_name == "gap_filler"
                else base_settings.judge_pass_threshold
            )
        )
        config_hash = compute_config_hash(spec, items, active_threshold)

        for prov, mod in selected_models:
            now_ts = time.time()
            active_until = checkpoint_store.active_cooldown_until(
                stage=stage_name,
                provider=prov,
                model=mod,
                now=now_ts,
            )
            completed_count = len(
                checkpoint_store.load_completed_items(stage_name, prov, mod, config_hash)
            )
            if active_until is not None:
                rem = max(0.0, active_until - now_ts)
                print(
                    f"\n[COOLDOWN SKIP] {stage_name} | {prov}:{mod} in cooldown for "
                    f"{rem:.0f}s ({completed_count}/{len(items)} checkpointed)."
                )
                summaries.append(
                    ModelBenchmarkSummary(
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                        status="COOLDOWN",
                        evaluated_total=completed_count,
                        dataset_total=len(items),
                        cooldown_remaining_s=rem,
                    )
                )
                continue

            updates: dict[str, Any] = {
                "judge_provider": prov,
                "judge_pass_threshold": active_threshold,
                "gap_filler_judge_threshold": active_threshold,
            }
            if prov == "gemini":
                updates["judge_gemini_model"] = mod
            elif prov == "ollama":
                updates["ollama_model"] = mod
            elif prov == "typesafe":
                updates["typesafe_model"] = mod
            stage_settings = base_settings.model_copy(update=updates)

            try:
                # Zero-fallback enforced unconditionally to guarantee pure per-model telemetry.
                judge = build_llm_judge_adapter(settings=stage_settings, enable_fallback=False)
                results = run_stage_calibration(
                    judge=judge,
                    spec=spec,
                    items=items,
                    provider=prov,
                    model=mod,
                    config_hash=config_hash,
                    checkpoint_store=checkpoint_store,
                    delay=delay,
                    jitter=jitter,
                    max_retry_wait=max_retry_wait,
                )
                tm = results.target_isolated
                status = (
                    "APROVADO"
                    if (tm.accuracy >= 0.85 and tm.permissivo_alfa == 0)
                    else "PRE-CALIB"
                    if tm.accuracy >= 0.80
                    else "REPROVADO"
                )
                single_target = len(selected_stages) == 1 and len(selected_models) == 1
                if output_path is not None:
                    report_dest = (
                        output_path
                        if single_target
                        else output_path / sanitize_report_filename(stage_name, prov, mod)
                    )
                else:
                    report_dest = DEFAULT_REPORTS_DIR / sanitize_report_filename(
                        stage_name, prov, mod
                    )
                save_calibration_report(
                    spec=spec,
                    results=results,
                    output_path=report_dest,
                    provider=prov,
                    model=mod,
                )
                summaries.append(
                    ModelBenchmarkSummary(
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                        status=status,
                        accuracy=tm.accuracy,
                        d_prime=tm.d_prime,
                        f1=tm.f1,
                        precision=tm.precision,
                        recall=tm.recall,
                        alpha_fpr=tm.alpha_fpr,
                        evaluated_total=tm.total_valid,
                        dataset_total=len(items),
                    )
                )
            except CredentialPoolExhaustedError as exc:
                saved_after = len(
                    checkpoint_store.load_completed_items(stage_name, prov, mod, config_hash)
                )
                summaries.append(
                    ModelBenchmarkSummary(
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                        status="COOLDOWN",
                        evaluated_total=saved_after,
                        dataset_total=len(items),
                        cooldown_remaining_s=exc.retry_after_seconds,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                has_errors = True
                saved_after = len(
                    checkpoint_store.load_completed_items(stage_name, prov, mod, config_hash)
                )
                print(f"[ERROR] {stage_name} | {prov}:{mod} failed: {exc}")
                summaries.append(
                    ModelBenchmarkSummary(
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                        status="ERRO",
                        evaluated_total=saved_after,
                        dataset_total=len(items),
                        error_message=str(exc),
                    )
                )

    _print_benchmark_summary(summaries)
    if has_errors:
        raise typer.Exit(code=1)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint delegating to Typer without standalone process exit."""
    try:
        app(args=list(argv) if argv is not None else None, standalone_mode=False)
        return 0
    except click.exceptions.Exit as exc:
        return int(exc.exit_code)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 0
        return code


if __name__ == "__main__":
    raise SystemExit(main())
