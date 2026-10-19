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
import math
import random
import sys
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from statistics import NormalDist
from typing import Any

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
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.judge_factory import build_llm_judge_adapter

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("calibrate_judge")

DEFAULT_GOLDEN_SET_PATH = (
    REPO_ROOT / "scripts" / "fluid_prose" / "golden_sets" / "fluid_prose_golden_set.json"
)

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


@dataclass(frozen=True)
class MetricInfo:
    """Informações conceituais e quantitativas de cada métrica de avaliação do juiz."""

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
    """Confusion matrix counts and comprehensive evaluation metrics for binary quality evaluation."""

    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0
    invalid: int = 0

    # Nomenclatura canônica da planilha
    @property
    def hit(self) -> int:
        """Hit (Verdadeiro Positivo): Gabarito Correto e Juiz Aprova."""
        return self.tp

    @property
    def pedantismo_beta(self) -> int:
        """Pedantismo-beta (Falso Negativo): Gabarito Correto e Juiz Reprova."""
        return self.fn

    @property
    def permissivo_alfa(self) -> int:
        """Permissivo-alfa (Falso Positivo): Gabarito Defeituoso e Juiz Aprova."""
        return self.fp

    @property
    def rejeicao(self) -> int:
        """Rejeição (Verdadeiro Negativo): Gabarito Defeituoso e Juiz Reprova."""
        return self.tn

    @property
    def total_corretos(self) -> int:
        """Total de itens com gabarito verdadeiro (Hit + Pedantismo-beta)."""
        return self.hit + self.pedantismo_beta

    @property
    def total_defeituosos(self) -> int:
        """Total de itens com gabarito defeituoso (Permissivo-alfa + Rejeição)."""
        return self.permissivo_alfa + self.rejeicao

    @property
    def total_aprovados(self) -> int:
        """Total de aprovações emitidas pelo juiz (Hit + Permissivo-alfa)."""
        return self.hit + self.permissivo_alfa

    @property
    def total_reprovados(self) -> int:
        """Total de reprovações emitidas pelo juiz (Pedantismo-beta + Rejeição)."""
        return self.pedantismo_beta + self.rejeicao

    @property
    def total_valid(self) -> int:
        return self.tp + self.fp + self.fn + self.tn

    # a) Acurácia (Accuracy)
    @property
    def accuracy(self) -> float:
        """(Hit + Rejeição) / Total"""
        return (self.hit + self.rejeicao) / self.total_valid if self.total_valid > 0 else 0.0

    # b) Precisão / VPP (Precision / Positive Predictive Value)
    @property
    def precision(self) -> float:
        """Hit / (Hit + Permissivo-alfa)"""
        denom = self.hit + self.permissivo_alfa
        return self.hit / denom if denom > 0 else 0.0

    # c) Sensibilidade / Recall (TPR)
    @property
    def recall(self) -> float:
        """Hit / (Hit + Pedantismo-beta)"""
        denom = self.hit + self.pedantismo_beta
        return self.hit / denom if denom > 0 else 0.0

    # d) Especificidade (TNR - True Negative Rate)
    @property
    def specificity(self) -> float:
        """Rejeição / (Rejeição + Permissivo-alfa)"""
        denom = self.rejeicao + self.permissivo_alfa
        return self.rejeicao / denom if denom > 0 else 0.0

    # e) Valor Preditivo Negativo (VPN / NPV)
    @property
    def npv(self) -> float:
        """Rejeição / (Rejeição + Pedantismo-beta)"""
        denom = self.rejeicao + self.pedantismo_beta
        return self.rejeicao / denom if denom > 0 else 0.0

    # f) Taxa de Falso Alarme / Permissividade (Nível Alfa / FPR)
    @property
    def alpha_fpr(self) -> float:
        """Permissivo-alfa / (Rejeição + Permissivo-alfa) = 1 - Especificidade"""
        denom = self.rejeicao + self.permissivo_alfa
        return self.permissivo_alfa / denom if denom > 0 else 0.0

    # g) Taxa de Pedantismo (Nível Beta / FNR)
    @property
    def beta_fnr(self) -> float:
        """Pedantismo-beta / (Hit + Pedantismo-beta) = 1 - Sensibilidade"""
        denom = self.hit + self.pedantismo_beta
        return self.pedantismo_beta / denom if denom > 0 else 0.0

    # h) F0.5-Score (Peso na Precisão: beta = 0.5)
    @property
    def f05(self) -> float:
        """(1 + 0.5^2) * (P * R) / ((0.5^2 * P) + R) = 1.25*(P*R)/(0.25*P + R)"""
        p, r = self.precision, self.recall
        beta_sq = 0.25
        denom = (beta_sq * p) + r
        return (1 + beta_sq) * (p * r) / denom if denom > 0 else 0.0

    # i) F1-Score (Equilíbrio harmônico entre Precisão e Recall: beta = 1)
    @property
    def f1(self) -> float:
        """2 * (P * R) / (P + R)"""
        p, r = self.precision, self.recall
        denom = p + r
        return (2 * p * r) / denom if denom > 0 else 0.0

    # j) F2-Score (Peso na Sensibilidade: beta = 2)
    @property
    def f2(self) -> float:
        """(1 + 2^2) * (P * R) / ((2^2 * P) + R) = 5.0*(P*R)/(4.0*P + R)"""
        p, r = self.precision, self.recall
        beta_sq = 4.0
        denom = (beta_sq * p) + r
        return (1 + beta_sq) * (p * r) / denom if denom > 0 else 0.0

    # k) Razão de Verossimilhança Positiva (LR+)
    @property
    def lr_plus(self) -> float:
        """Sensibilidade / (1 - Especificidade) = Recall / Taxa Falso Alarme"""
        fpr = self.alpha_fpr
        if fpr == 0:
            return float("inf") if self.recall > 0 else 1.0
        return self.recall / fpr

    # l) Razão de Verossimilhança Negativa (LR-)
    @property
    def lr_minus(self) -> float:
        """(1 - Sensibilidade) / Especificidade = Taxa Pedantismo / Especificidade"""
        tnr = self.specificity
        if tnr == 0:
            return float("inf") if self.beta_fnr > 0 else 1.0
        return self.beta_fnr / tnr

    # m) Coeficiente de Correlação de Matthews (MCC)
    @property
    def mcc(self) -> float:
        """((Hit * Rejeição) - (Permissivo * Pedantismo)) / sqrt(...)"""
        num = (self.hit * self.rejeicao) - (self.permissivo_alfa * self.pedantismo_beta)
        denom = math.sqrt(
            (self.hit + self.permissivo_alfa)
            * (self.hit + self.pedantismo_beta)
            * (self.rejeicao + self.permissivo_alfa)
            * (self.rejeicao + self.pedantismo_beta)
        )
        return num / denom if denom > 0 else 0.0

    # n) D-prime (d') da Teoria de Detecção de Sinal (SDT)
    @property
    def d_prime(self) -> float:
        """NORM.S.INV(Taxa Hit) - NORM.S.INV(Taxa Falso Alarme)"""
        n_signal = self.total_corretos
        n_noise = self.total_defeituosos
        if n_signal == 0 or n_noise == 0:
            return 0.0
        # Correção padrão de Macmillan & Creelman (clamp 1/(2N)) para evitar infinitos
        eps_s = 1.0 / (2 * n_signal)
        eps_n = 1.0 / (2 * n_noise)
        hit_rate = self.hit / n_signal
        fa_rate = self.permissivo_alfa / n_noise
        h_clamp = min(max(hit_rate, eps_s), 1.0 - eps_s)
        fa_clamp = min(max(fa_rate, eps_n), 1.0 - eps_n)
        norm = NormalDist()
        return norm.inv_cdf(h_clamp) - norm.inv_cdf(fa_clamp)

    # o) Critério c (Viés de Decisão / Response Bias)
    @property
    def c_bias(self) -> float:
        """-0.5 * (NORM.S.INV(Taxa Hit) + NORM.S.INV(Taxa Falso Alarme))"""
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

        if expected == "PASS" and actual == "PASS":
            self.tp += 1
            return "HIT (True Positive - Correto Aprovado)"
        if expected == "FAIL" and actual == "FAIL":
            self.tn += 1
            return "REJEIÇÃO (True Negative - Defeituoso Reprovado)"
        if expected == "FAIL" and actual == "PASS":
            self.fp += 1
            return "PERMISSIVO-ALFA (False Positive - Defeito que Vazou)"
        self.fn += 1
        return "PEDANTISMO-BETA (False Negative - Correto Desperdiçado)"

    def get_all_metrics(self) -> list[MetricInfo]:
        """Gera a lista completa com as 15 métricas de avaliação e seus conceitos."""
        # a) Acurácia
        acc_diag = "Maioria das decisões correta." if self.accuracy >= 0.80 else "Juiz erra com frequência."
        # b) Precisão
        prec_diag = "Aprovações muito confiáveis/puras." if self.precision >= 0.80 else "Muitos textos adulterados vazam rotulados como aprovados."
        # c) Sensibilidade
        rec_diag = "Aproveita quase todas as frases fiéis." if self.recall >= 0.85 else "Juiz é pedante e joga textos bons fora."
        # d) Especificidade
        spec_diag = "Barreira eficaz contra defeitos." if self.specificity >= 0.70 else "Deixa o lixo passar batido."
        # e) VPN
        npv_diag = "Quando reprova, o texto é de fato defeituoso." if self.npv >= 0.75 else "Reprovação descarta muitos textos bons."
        # f) Nível Alfa
        fpr_diag = "Filtro quase hermético." if self.alpha_fpr <= 0.20 else "Vazamento inaceitável de erros."
        # g) Nível Beta
        fnr_diag = "Juiz não implica à toa." if self.beta_fnr <= 0.15 else "Desperdício e retrabalho massivo."
        # h) F0.5
        f05_diag = "Excelente fidelidade e baixa permissividade." if self.f05 >= 0.80 else "Vazamento de adulterações prejudicou a saída."
        # i) F1
        f1_diag = "Ótimo equilíbrio entre filtrar erros e não implicar." if self.f1 >= 0.80 else "Desequilíbrio acentuado ou desempenho ruim."
        # j) F2
        f2_diag = "Altíssimo aproveitamento dos textos bons." if self.f2 >= 0.85 else "Excesso de pedantismo descartou material bom."
        # k) LR+
        lr_plus_val = self.lr_plus
        if lr_plus_val >= 10.0:
            lr_plus_diag = "Aprovação comprova fortemente fidelidade (>10)."
        elif lr_plus_val >= 2.0:
            lr_plus_diag = "Aprovação tem valor probatório moderado (2 a 10)."
        else:
            lr_plus_diag = "Aprovação tem pouco valor probatório (<2)."
        # l) LR-
        lr_minus_val = self.lr_minus
        if lr_minus_val <= 0.10:
            lr_minus_diag = "Reprovação descarta e confirma defeito de forma quase definitiva (<0.1)."
        elif lr_minus_val <= 0.50:
            lr_minus_diag = "Reprovação tem valor probatório moderado (0.1 a 0.5)."
        else:
            lr_minus_diag = "Reprovação é inconclusiva (>0.5)."
        # m) MCC
        mcc_val = self.mcc
        if mcc_val >= 0.60:
            mcc_diag = "Forte correlação geral com o gabarito."
        elif mcc_val > 0.20:
            mcc_diag = "Correlação moderada com o gabarito."
        else:
            mcc_diag = "Performance nula ou inversa (<=0)."
        # n) d-prime
        dp_val = self.d_prime
        if dp_val >= 2.0:
            dp_diag = "Acuidade mental / capacidade de distinção excelente (>2.0)."
        elif dp_val >= 1.0:
            dp_diag = "Capacidade de distinção moderada/boa (1.0 a 2.0)."
        else:
            dp_diag = "Juiz incapaz de diferenciar texto bom de ruim (~0)."
        # o) Critério c
        c_val = self.c_bias
        if c_val > 0.15:
            c_diag = f"Juiz pedante/conservador (+{c_val:.2f}): tende a reprovar mais."
        elif c_val < -0.15:
            c_diag = f"Juiz permissivo/liberal ({c_val:.2f}): tende a aprovar mais."
        else:
            c_diag = f"Juiz neutro/balanceado ({c_val:.2f}): sem viés sistemático."

        lr_plus_str = f"{lr_plus_val:.2f}" if lr_plus_val != float("inf") else "Inf"
        lr_minus_str = f"{lr_minus_val:.2f}" if lr_minus_val != float("inf") else "Inf"

        return [
            MetricInfo(
                code="a)",
                name="Acurácia (Accuracy)",
                math_formula="(Hit + Rejeição) / Total",
                sheets_formula="=(B4+C5)/D6",
                value=self.accuracy,
                formatted_value=f"{self.accuracy * 100:.1f}%",
                practical_implication="Mede a proporção geral de acertos do juiz.",
                high_meaning="Maioria das decisões correta.",
                low_meaning="Juiz erra com frequência.",
                diagnosis=acc_diag,
            ),
            MetricInfo(
                code="b)",
                name="Precisão / VPP (Precision)",
                math_formula="Hit / (Hit + Permissivo-alfa)",
                sheets_formula="=B4/B6",
                value=self.precision,
                formatted_value=f"{self.precision * 100:.1f}%",
                practical_implication="Mede a pureza das aprovações (textos aprovados que são realmente bons).",
                high_meaning="Aprovações muito confiáveis/puras.",
                low_meaning="Muitos textos adulterados vazam rotulados como aprovados.",
                diagnosis=prec_diag,
            ),
            MetricInfo(
                code="c)",
                name="Sensibilidade / Recall",
                math_formula="Hit / (Hit + Pedantismo-beta)",
                sheets_formula="=B4/D4",
                value=self.recall,
                formatted_value=f"{self.recall * 100:.1f}%",
                practical_implication="Mede a capacidade de não descartar textos bons.",
                high_meaning="Aproveita quase todas as frases fiéis.",
                low_meaning="Juiz é pedante e joga textos bons fora.",
                diagnosis=rec_diag,
            ),
            MetricInfo(
                code="d)",
                name="Especificidade (TNR)",
                math_formula="Rejeição / (Rejeição + Permissivo-alfa)",
                sheets_formula="=C5/D5",
                value=self.specificity,
                formatted_value=f"{self.specificity * 100:.1f}%",
                practical_implication="Mede a capacidade de barrar textos defeituosos.",
                high_meaning="Barreira eficaz contra defeitos.",
                low_meaning="Deixa o lixo passar batido.",
                diagnosis=spec_diag,
            ),
            MetricInfo(
                code="e)",
                name="Valor Preditivo Negativo (VPN)",
                math_formula="Rejeição / (Rejeição + Pedantismo-beta)",
                sheets_formula="=C5/C6",
                value=self.npv,
                formatted_value=f"{self.npv * 100:.1f}%",
                practical_implication="Mede a confiabilidade das reprovações.",
                high_meaning="Quando reprova, o texto é de fato defeituoso.",
                low_meaning="Reprovação descarta muitos textos bons.",
                diagnosis=npv_diag,
            ),
            MetricInfo(
                code="f)",
                name="Taxa de Falso Alarme / Permissividade (Nível Alfa)",
                math_formula="Permissivo-alfa / (Rejeição + Permissivo-alfa)",
                sheets_formula="=B5/D5",
                value=self.alpha_fpr,
                formatted_value=f"{self.alpha_fpr * 100:.1f}%",
                practical_implication="Mede a taxa de vazamento de erros.",
                high_meaning="Vazamento inaceitável de erros.",
                low_meaning="Filtro quase hermético.",
                diagnosis=fpr_diag,
            ),
            MetricInfo(
                code="g)",
                name="Taxa de Pedantismo (Nível Beta)",
                math_formula="Pedantismo-beta / (Hit + Pedantismo-beta)",
                sheets_formula="=C4/D4",
                value=self.beta_fnr,
                formatted_value=f"{self.beta_fnr * 100:.1f}%",
                practical_implication="Mede a taxa de desperdício de textos bons.",
                high_meaning="Desperdício e retrabalho massivo.",
                low_meaning="Juiz não implica à toa.",
                diagnosis=fnr_diag,
            ),
            MetricInfo(
                code="h)",
                name="F0.5-Score (Peso na Precisão)",
                math_formula="1.25 * (P * R) / (0.25 * P + R)",
                sheets_formula="=(1+H17^2)*(D$11*D$12)/((H17^2*D$11)+D$12)",
                value=self.f05,
                formatted_value=f"{self.f05 * 100:.1f}%",
                practical_implication="Avalia performance dando mais peso à Precisão (2x mais peso que Recall).",
                high_meaning="Excelente fidelidade e baixa permissividade.",
                low_meaning="Vazamento de adulterações prejudicou a saída.",
                diagnosis=f05_diag,
            ),
            MetricInfo(
                code="i)",
                name="F1-Score (Equilíbrio P e R)",
                math_formula="2 * (P * R) / (P + R)",
                sheets_formula="=(1+H18^2)*(D$11*D$12)/((H18^2*D$11)+D$12)",
                value=self.f1,
                formatted_value=f"{self.f1 * 100:.1f}%",
                practical_implication="Avalia o equilíbrio entre Precisão e Sensibilidade.",
                high_meaning="Ótimo equilíbrio entre filtrar erros e não implicar.",
                low_meaning="Desequilíbrio acentuado ou desempenho ruim.",
                diagnosis=f1_diag,
            ),
            MetricInfo(
                code="j)",
                name="F2-Score (Peso na Sensibilidade)",
                math_formula="5 * (P * R) / (4 * P + R)",
                sheets_formula="=(1+H19^2)*(D$11*D$12)/((H19^2*D$11)+D$12)",
                value=self.f2,
                formatted_value=f"{self.f2 * 100:.1f}%",
                practical_implication="Avalia performance dando mais peso à Sensibilidade (2x mais peso que Precisão).",
                high_meaning="Altíssimo aproveitamento dos textos bons.",
                low_meaning="Excesso de pedantismo descartou material bom.",
                diagnosis=f2_diag,
            ),
            MetricInfo(
                code="k)",
                name="Razão de Verossimilhança Positiva (LR+)",
                math_formula="Sensibilidade / (1 - Especificidade)",
                sheets_formula="=(B4/D4)/(B5/D5)",
                value=lr_plus_val,
                formatted_value=lr_plus_str,
                practical_implication="Mede o valor probatório da aprovação.",
                high_meaning="Aprovação comprova fortemente fidelidade (>10).",
                low_meaning="Aprovação tem pouco valor probatório (<2).",
                diagnosis=lr_plus_diag,
            ),
            MetricInfo(
                code="l)",
                name="Razão de Verossimilhança Negativa (LR-)",
                math_formula="(1 - Sensibilidade) / Especificidade",
                sheets_formula="=(C4/D4)/(C5/D5)",
                value=lr_minus_val,
                formatted_value=lr_minus_str,
                practical_implication="Mede o valor probatório da reprovação.",
                high_meaning="Reprovação é inconclusiva (>0.5).",
                low_meaning="Reprovação descarta e confirma defeito de forma quase definitiva (<0.1).",
                diagnosis=lr_minus_diag,
            ),
            MetricInfo(
                code="m)",
                name="Coeficiente de Correlação de Matthews (MCC)",
                math_formula="((Hit * Rejeição) - (Permissivo * Pedantismo)) / SQRT(...)",
                sheets_formula="=((B4*C5)-(B5*C4))/SQRT(B6*D4*D5*C6)",
                value=mcc_val,
                formatted_value=f"{mcc_val:+.3f}",
                practical_implication="Mede a correlação geral entre as decisões e o gabarito (-1 a +1).",
                high_meaning="Correlação perfeita (+1).",
                low_meaning="Performance nula ou inversa (<=0).",
                diagnosis=mcc_diag,
            ),
            MetricInfo(
                code="n)",
                name="D-prime (d') da Teoria de Detecção de Sinal",
                math_formula="NORM.S.INV(Taxa Hit) - NORM.S.INV(Taxa Falso Alarme)",
                sheets_formula="=NORM.S.INV(B4/D4)-NORM.S.INV(B5/D5)",
                value=dp_val,
                formatted_value=f"{dp_val:.2f}",
                practical_implication="Mede a acuidade mental / capacidade intrínseca de distinção.",
                high_meaning="Acuidade mental/capacidade de distinção excelente (>2.0).",
                low_meaning="Juiz incapaz de diferenciar texto bom de ruim (~0).",
                diagnosis=dp_diag,
            ),
            MetricInfo(
                code="o)",
                name="Critério c (Viés de Decisão)",
                math_formula="-0.5 * (NORM.S.INV(Taxa Hit) + NORM.S.INV(Taxa Falso Alarme))",
                sheets_formula="=-0.5*(NORM.S.INV(B4/D4)+NORM.S.INV(B5/D5))",
                value=c_val,
                formatted_value=f"{c_val:+.2f}",
                practical_implication="Mede o viés de decisão (conservador vs liberal).",
                high_meaning="Juiz pedante/conservador (Positivo).",
                low_meaning="Juiz permissivo/liberal (Negativo).",
                diagnosis=c_diag,
            ),
        ]


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


def run_local_calibration(
    judge: Any,
    items: list[dict[str, Any]],
    delay: float = 4.2,
    jitter: float = 0.8,
) -> CalibrationResultSet:
    """Run calibration over local dataset items and compute global and slice metrics."""
    results = CalibrationResultSet()

    print("\n" + "=" * 70)
    print("RUNNING FLUID PROSE JUDGE CALIBRATION HARNESS")
    if delay > 0:
        print(f"Pacing: {delay:.1f}s base delay + up to {jitter:.1f}s jitter between LLM evaluations")
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

        eval_res = evaluate_single_item(judge, item)
        actual_global = eval_res.actual
        expected = eval_res.expected
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


def format_matrix_2x2(title: str, m: ConfusionMatrix) -> str:
    """Formata a matriz de confusão 2x2 com a terminologia e layout canônico da planilha."""
    lines = [
        f"\n{title}",
        "-" * 80,
        f"{'':30} | {'Juiz Aprova':<20} | {'Juiz Reprova':<20} | {'Total':<6}",
        "-" * 80,
        (
            f"{'Gabarito Verdadeiro (Correto)':<30} | "
            f"HIT: {m.hit:<15} | "
            f"PEDANTISMO-BETA: {m.pedantismo_beta:<3} | "
            f"{m.total_corretos:<6}"
        ),
        (
            f"{'Gabarito Falso (Defeituoso)':<30} | "
            f"PERMISSIVO-ALFA: {m.permissivo_alfa:<3} | "
            f"REJEIÇÃO: {m.rejeicao:<10} | "
            f"{m.total_defeituosos:<6}"
        ),
        "-" * 80,
        (
            f"{'Total':<30} | "
            f"{m.total_aprovados:<20} | "
            f"{m.total_reprovados:<20} | "
            f"{m.total_valid:<6}"
        ),
        "-" * 80,
    ]
    return "\n".join(lines)


def format_metrics_table(title: str, m: ConfusionMatrix) -> str:
    """Formata a tabela detalhada das 15 métricas de avaliação do juiz com diagnósticos."""
    lines = [
        f"\n{title}",
        "=" * 112,
        f"{'Cód':<4} | {'Métrica':<36} | {'Resultado':<10} | {'Diagnóstico / Implicação Prática'}",
        "-" * 112,
    ]
    for info in m.get_all_metrics():
        lines.append(f"{info.code:<4} | {info.name:<36} | {info.formatted_value:>10} | {info.diagnosis}")
    lines.append("=" * 112)
    return "\n".join(lines)


def generate_calibration_report(
    results: CalibrationResultSet,
    provider: str = "",
    model: str = "",
) -> str:
    """Generate complete string representation of the calibration report for file output."""
    matrix = results.overall
    target_matrix = results.target_isolated
    lines: list[str] = [
        "=" * 80,
        "RELATÓRIO DE CALIBRAÇÃO DO JUIZ LLM (ESTÁGIO FLUID_PROSE)",
        "=" * 80,
        f"Data/Hora:       {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Provedor:        {provider}",
        f"Modelo:          {model}",
        f"Total Avaliado:  {matrix.total_valid + matrix.invalid} itens",
        f"Itens Válidos:   {matrix.total_valid} itens",
    ]
    if matrix.invalid > 0:
        lines.append(f"Itens Inválidos: {matrix.invalid} itens")

    # 1. Matriz 2x2 Canônica (Isolated Target Criterion Gate)
    lines.append(
        format_matrix_2x2(
            "MATRIZ 2x2: DECISÃO DO JUIZ VS GABARITO (ISOLATED TARGET CRITERION - OPÇÃO 3)",
            target_matrix,
        )
    )

    # 2. Tabela Completa das 15 Métricas (Isolated Target)
    lines.append(
        format_metrics_table(
            "MÉTRICAS DE AVALIAÇÃO DO JUIZ (TARGET ISOLATED - SEM CONTAMINAÇÃO CRUZADA)",
            target_matrix,
        )
    )

    # 3. Matriz 2x2 e Métricas Resumo (Global Composite Gate)
    lines.append(
        format_matrix_2x2(
            "MATRIZ 2x2: GLOBAL PIPELINE GATE (COMPOSITE HARD GATE DE PASSAGEM DE ESTÁGIO)",
            matrix,
        )
    )

    # 4. Breakdown por Critério
    lines.extend([
        "\n" + "=" * 80,
        "BREAKDOWN POR CRITÉRIO (Target-Isolated Metrics):",
        "-" * 80,
        f"{'Criterion':<24} | {'Valid':<5} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'d-prime':<7}",
        "-" * 80,
    ])
    for crit, m in results.by_criterion.items():
        lines.append(
            f"{crit:<24} | {m.total_valid:<5} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    # 5. Breakdown por Dificuldade
    lines.extend([
        "\n" + "=" * 80,
        "BREAKDOWN POR DIFICULDADE (Target-Isolated Metrics):",
        "-" * 80,
        f"{'Difficulty':<16} | {'Valid':<5} | {'Acc':<6} | {'Prec':<6} | {'Rec':<6} | {'F1':<6} | {'d-prime':<7}",
        "-" * 80,
    ])
    for diff, m in results.by_difficulty.items():
        lines.append(
            f"{diff:<16} | {m.total_valid:<5} | {m.accuracy * 100:5.1f}% | "
            f"{m.precision * 100:5.1f}% | {m.recall * 100:5.1f}% | {m.f1:5.3f} | {m.d_prime:6.2f}"
        )

    # 6. Referência Conceitual & Fórmulas Google Sheets
    lines.extend([
        "\n" + "=" * 112,
        "REFERÊNCIA CONCEITUAL DAS FÓRMULAS & GOOGLE SHEETS:",
        "-" * 112,
    ])
    for info in target_matrix.get_all_metrics():
        lines.append(f"{info.code:<4} {info.name:<38} | Fórmula: {info.math_formula:<40} | Sheets: {info.sheets_formula}")
        lines.append(f"     Implicação Prática: {info.practical_implication}")
        lines.append(f"     Se Valor Alto:      {info.high_meaning}")
        lines.append(f"     Se Valor Baixo:     {info.low_meaning}")
        lines.append("-" * 112)

    # 7. Diagnósticos e Gates de Produção
    lines.extend([
        "\n" + "=" * 80,
        "DIAGNÓSTICO E RECOMENDAÇÃO DOS PRODUCTION QUALITY GATES:",
        "-" * 80,
    ])
    if target_matrix.permissivo_alfa > 0:
        lines.append(f"  [!] PERMISSIBILIDADE: {target_matrix.permissivo_alfa} falsos positivos no critério alvo.")
        lines.append(f"      Taxa Alfa (FPR): {target_matrix.alpha_fpr * 100:.1f}%.")
        lines.append("      Risco: Textos defeituosos avançando silenciosamente na esteira.")
        lines.append("      Ação: Aumentar rigor dos critérios de rejeição correspondentes.")
    if target_matrix.pedantismo_beta > 0:
        lines.append(f"  [!] PEDANTISMO: {target_matrix.pedantismo_beta} falsos negativos no critério alvo.")
        lines.append(f"      Taxa Beta (FNR): {target_matrix.beta_fnr * 100:.1f}%.")
        lines.append("      Risco: Textos corretos sendo descartados ou gerando retries excessivos.")
        lines.append("      Ação: Calibrar tolerância do juiz a variações estilísticas legítimas.")

    if target_matrix.accuracy >= 0.85 and target_matrix.permissivo_alfa == 0:
        lines.append("  [✓] JUIZ CALIBRADO: Acurácia >= 85% com zero vazamentos permissivos (FP = 0).")
        lines.append("      Veredito: Seguro para ativação em modo bloqueante (judge_blocking=True).")
    elif target_matrix.accuracy >= 0.80:
        lines.append("  [~] JUIZ PRÉ-CALIBRADO: Acurácia >= 80%, mas requer ajuste fino de rubricas.")
        lines.append("      Veredito: Manter ativo em modo observabilidade / não-bloqueante.")
    else:
        lines.append("  [X] JUIZ NÃO CALIBRADO: Desempenho abaixo do patamar mínimo de 80%.")
        lines.append("      Veredito: Revisar prompts, rubricas ou optar por modelo mais potente.")
    lines.append("=" * 80 + "\n")

    return "\n".join(lines)


def print_summary_progress(
    results: CalibrationResultSet,
    output_path: Path,
    provider: str = "",
    model: str = "",
) -> None:
    """Imprime exclusivamente o progresso resumido final no terminal."""
    target_m = results.target_isolated
    status_icon = "✓" if (target_m.accuracy >= 0.85 and target_m.permissivo_alfa == 0) else "!"
    veredito_label = (
        "APROVADO PARA PRODUÇÃO BLOQUEANTE"
        if status_icon == "✓"
        else "REQUER AJUSTES FINOS"
    )

    print("\n" + "=" * 70)
    print("CALIBRAÇÃO CONCLUÍDA")
    print("=" * 70)
    print(f"Provedor / Modelo: {provider} ({model})")
    print(f"Total Avaliado:    {target_m.total_valid} itens")
    print(f"Acurácia Alvo:     {target_m.accuracy * 100:.1f}%")
    print(f"Decisões:          HIT={target_m.hit} | REJEIÇÃO={target_m.rejeicao} | FP={target_m.permissivo_alfa} | FN={target_m.pedantismo_beta}")
    print(f"Taxa Alfa (FPR):   {target_m.alpha_fpr * 100:.1f}%")
    print(f"D-prime (d'):      {target_m.d_prime:.2f}")
    print(f"Veredito:          [{status_icon}] {veredito_label}")
    print(f"Relatório Salvo:   {output_path.resolve()}")
    print("=" * 70 + "\n")


def save_calibration_report(
    results: CalibrationResultSet,
    output_path: Path,
    provider: str = "",
    model: str = "",
) -> Path:
    """Salva o relatório completo em arquivo e exibe apenas o resumo no terminal."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_text = generate_calibration_report(results, provider=provider, model=model)
    output_path.write_text(report_text, encoding="utf-8")
    print_summary_progress(results, output_path=output_path, provider=provider, model=model)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate Fluid Prose LLM Judge")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "ollama", "typesafe"])
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Optional override for model name (e.g. 'qwen2.5:7b', 'gemma4:latest' for Ollama)",
    )
    parser.add_argument("--threshold", type=float, default=0.80)
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=DEFAULT_GOLDEN_SET_PATH,
        help="Path to local Golden Set JSON file",
    )
    parser.add_argument("--dataset-name", default="cresmo-fluid-prose-calibration")
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
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Base pacing delay in seconds (default: 4.2s for Gemini API, 0.0s for local Ollama)",
    )
    parser.add_argument(
        "--jitter",
        type=float,
        default=None,
        help="Random jitter in seconds (default: 0.8s for Gemini API, 0.0s for local Ollama)",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help="Custom destination path to write full calibration report (default: scripts/fluid_prose/llm_judge_{provider}.txt)",
    )
    args = parser.parse_args()

    # Automatic zero-delay pacing for local providers
    delay = args.delay if args.delay is not None else (0.0 if args.provider == "ollama" else 4.2)
    jitter = args.jitter if args.jitter is not None else (0.0 if args.provider == "ollama" else 0.8)

    model_kwargs: dict[str, Any] = {}
    if args.model:
        if args.provider == "ollama":
            model_kwargs["ollama_model"] = args.model
        elif args.provider == "gemini":
            model_kwargs["judge_gemini_model"] = args.model
        elif args.provider == "typesafe":
            model_kwargs["typesafe_model"] = args.model

    settings = CresmoSettings(
        judge_provider=args.provider,
        judge_pass_threshold=args.threshold,
        **model_kwargs,
    )

    resolved_model = args.model or (settings.ollama_model if args.provider == "ollama" else settings.judge_gemini_model)
    output_file = args.output_path or (REPO_ROOT / "scripts" / "fluid_prose" / f"llm_judge_{args.provider}.txt")

    logger.info(
        "Instantiating Judge adapter chain (Provider: %s, Model: %s)...",
        args.provider,
        resolved_model,
    )
    judge = build_llm_judge_adapter(settings=settings)

    if args.seed_only:
        logger.info(
            "Executing calibration against embedded seed items (%d items)...",
            len(SEED_CALIBRATION_DATA),
        )
        results = run_local_calibration(
            judge,
            SEED_CALIBRATION_DATA,
            delay=delay,
            jitter=jitter,
        )
        save_calibration_report(
            results,
            output_path=output_file,
            provider=args.provider,
            model=resolved_model,
        )
        return 0 if results.target_isolated.accuracy >= 0.85 else 1

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
            results = run_local_calibration(
                judge,
                items,
                delay=delay,
                jitter=jitter,
            )
            save_calibration_report(
                results,
                output_path=output_file,
                provider=args.provider,
                model=resolved_model,
            )
            return 0 if results.target_isolated.accuracy >= 0.85 else 1
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed connecting to remote Langfuse dataset: %s", exc)
            return 1

    # Default: Load local golden set file
    if not args.dataset_path.exists():
        logger.warning(
            "Golden set file '%s' not found. Falling back to embedded seed data.", args.dataset_path
        )
        results = run_local_calibration(
            judge,
            SEED_CALIBRATION_DATA,
            delay=delay,
            jitter=jitter,
        )
        save_calibration_report(
            results,
            output_path=output_file,
            provider=args.provider,
            model=resolved_model,
        )
        return 0 if results.target_isolated.accuracy >= 0.85 else 1

    logger.info("Loading Golden Set from '%s'...", args.dataset_path)
    with open(args.dataset_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    logger.info("Loaded %d items from %s. Starting calibration...", len(items), args.dataset_path)
    results = run_local_calibration(
        judge,
        items,
        delay=delay,
        jitter=jitter,
    )
    save_calibration_report(
        results,
        output_path=output_file,
        provider=args.provider,
        model=resolved_model,
    )
    return 0 if results.target_isolated.accuracy >= 0.85 else 1


if __name__ == "__main__":
    sys.exit(main())
