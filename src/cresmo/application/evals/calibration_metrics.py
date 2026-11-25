"""Pure Signal Detection Theory (SDT) confusion matrices and calibration result models.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from statistics import NormalDist
from typing import Any

from cresmo.domain.exceptions import DomainValidationError


class CalibrationVerdict(StrEnum):
    """Canonical lifecycle verdict assigned to one `(stage, provider, model)` target."""

    APPROVED = "APPROVED"
    PRE_CALIBRATED = "PRE-CALIBRATED"
    REJECTED = "REJECTED"
    COOLDOWN = "COOLDOWN"
    ERROR = "ERROR"


@dataclass
class ConfusionMatrix:
    """Confusion matrix counts and pure Signal Detection Theory metrics."""

    hit: int = 0
    false_reject_beta: int = 0
    false_accept_alpha: int = 0
    correct_rejection: int = 0

    @property
    def total_valid(self) -> int:
        """Total ground-truth PASS items."""
        return self.hit + self.false_reject_beta

    @property
    def total_defective(self) -> int:
        """Total ground-truth FAIL items."""
        return self.false_accept_alpha + self.correct_rejection

    @property
    def total_approved(self) -> int:
        """Total items approved by Judge."""
        return self.hit + self.false_accept_alpha

    @property
    def total_rejected(self) -> int:
        """Total items rejected by Judge."""
        return self.false_reject_beta + self.correct_rejection

    @property
    def total_samples(self) -> int:
        """Total valid (non-invalid) items evaluated across the 2x2 matrix."""
        return self.hit + self.false_reject_beta + self.false_accept_alpha + self.correct_rejection

    @property
    def accuracy(self) -> float:
        """Overall accuracy: (Hit + Correct Rejection) / Total Samples."""
        total = self.total_samples
        return (self.hit + self.correct_rejection) / total if total > 0 else 0.0

    @property
    def precision(self) -> float:
        """Positive Predictive Value: Hit / (Hit + False Accept Alpha)."""
        denom = self.hit + self.false_accept_alpha
        return self.hit / denom if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        """Sensitivity (TPR): Hit / (Hit + False Reject Beta)."""
        denom = self.hit + self.false_reject_beta
        return self.hit / denom if denom > 0 else 0.0

    @property
    def specificity(self) -> float:
        """True Negative Rate (TNR): Correct Rejection / (Correct Rejection + False Accept Alpha)."""
        denom = self.correct_rejection + self.false_accept_alpha
        return self.correct_rejection / denom if denom > 0 else 0.0

    @property
    def npv(self) -> float:
        """Negative Predictive Value: Correct Rejection / (Correct Rejection + False Reject Beta)."""
        denom = self.correct_rejection + self.false_reject_beta
        return self.correct_rejection / denom if denom > 0 else 0.0

    @property
    def alpha_fpr(self) -> float:
        """False Positive Rate (Alpha): False Accept Alpha / Total Defective."""
        denom = self.correct_rejection + self.false_accept_alpha
        return self.false_accept_alpha / denom if denom > 0 else 0.0

    @property
    def beta_fnr(self) -> float:
        """False Negative Rate (Beta): False Reject Beta / Total Valid."""
        denom = self.hit + self.false_reject_beta
        return self.false_reject_beta / denom if denom > 0 else 0.0

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
        num = (self.hit * self.correct_rejection) - (
            self.false_accept_alpha * self.false_reject_beta
        )
        denom = math.sqrt(
            (self.hit + self.false_accept_alpha)
            * (self.hit + self.false_reject_beta)
            * (self.correct_rejection + self.false_accept_alpha)
            * (self.correct_rejection + self.false_reject_beta)
        )
        return num / denom if denom > 0 else 0.0

    @property
    def d_prime(self) -> float:
        """Signal Detection Theory sensitivity d' using Macmillan & Creelman clamp."""
        n_signal = self.total_valid
        n_noise = self.total_defective
        if n_signal == 0 or n_noise == 0:
            return 0.0
        eps_s = 1.0 / (2 * n_signal)
        eps_n = 1.0 / (2 * n_noise)
        h_clamp = min(max(self.hit / n_signal, eps_s), 1.0 - eps_s)
        fa_clamp = min(max(self.false_accept_alpha / n_noise, eps_n), 1.0 - eps_n)
        norm = NormalDist()
        return norm.inv_cdf(h_clamp) - norm.inv_cdf(fa_clamp)

    @property
    def c_bias(self) -> float:
        """Signal Detection Theory response bias c (>0 pedantic, <0 permissive)."""
        n_signal = self.total_valid
        n_noise = self.total_defective
        if n_signal == 0 or n_noise == 0:
            return 0.0
        eps_s = 1.0 / (2 * n_signal)
        eps_n = 1.0 / (2 * n_noise)
        h_clamp = min(max(self.hit / n_signal, eps_s), 1.0 - eps_s)
        fa_clamp = min(max(self.false_accept_alpha / n_noise, eps_n), 1.0 - eps_n)
        norm = NormalDist()
        return -0.5 * (norm.inv_cdf(h_clamp) + norm.inv_cdf(fa_clamp))

    def record(self, expected: str, actual: str) -> str:
        """Record expected vs actual verdict pair and return canonical status code."""
        if expected not in ("PASS", "FAIL"):
            raise DomainValidationError(
                f"Invalid expected calibration verdict {expected!r}; expected 'PASS' or 'FAIL'."
            )
        if expected == "PASS" and actual == "PASS":
            self.hit += 1
            return "HIT"
        if expected == "FAIL" and actual == "FAIL":
            self.correct_rejection += 1
            return "CORRECT_REJECTION"
        if expected == "FAIL" and actual == "PASS":
            self.false_accept_alpha += 1
            return "FALSE_ACCEPT_ALPHA"
        self.false_reject_beta += 1
        return "FALSE_REJECT_BETA"


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


@dataclass
class ItemEvaluationResult:
    """Evaluation result encapsulating global and target-criterion outcomes."""

    actual: str
    expected: str
    score: float
    reasoning: str
    target_actual: str = ""
    target_score: float = 0.0


@dataclass(frozen=True)
class ModelBenchmarkSummary:
    """Consolidated cross-stage/model outcome for terminal summary matrix."""

    stage: str
    provider: str
    model: str
    status: CalibrationVerdict
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
