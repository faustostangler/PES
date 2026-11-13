"""Signal Detection Theory (SDT) confusion matrices and calibration result models.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass, field
from statistics import NormalDist
from typing import Any


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
        """True Negative (Rejeicao): Ground truth FAIL and judge rejected."""
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
        """Overall accuracy: (Hit + Rejeicao) / Total."""
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
        """True Negative Rate (TNR): Rejeicao / (Rejeicao + Permissivo-alfa)."""
        denom = self.rejeicao + self.permissivo_alfa
        return self.rejeicao / denom if denom > 0 else 0.0

    @property
    def npv(self) -> float:
        """Negative Predictive Value: Rejeicao / (Rejeicao + Pedantismo-beta)."""
        denom = self.rejeicao + self.pedantismo_beta
        return self.rejeicao / denom if denom > 0 else 0.0

    @property
    def alpha_fpr(self) -> float:
        """False Positive Rate (Alpha): Permissivo-alfa / (Rejeicao + Permissivo-alfa)."""
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

        lr_plus_str = f"{lr_plus_val:.2f}" if not math.isinf(lr_plus_val) else "Inf"
        lr_minus_str = f"{lr_minus_val:.2f}" if not math.isinf(lr_minus_val) else "Inf"
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


@dataclass(frozen=True)
class CalibrationSuiteOutcome:
    """Aggregated outcome across all scheduled calibration stages and models."""

    summaries: tuple[ModelBenchmarkSummary, ...]
    has_errors: bool
