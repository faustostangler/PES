"""Single-stage judge calibration executor with cooldown and transient retry policies.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    ConfusionMatrix,
    ItemEvaluationResult,
)
from cresmo.application.evals.specs import StageCalibrationSpec
from cresmo.application.ports.evals import CalibrationCheckpointPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.exceptions import QuotaPoolExhaustedError, RateLimitExceededError
from cresmo.domain.value_objects.quality import EvaluationContext, JudgeCriterion


class CooldownActiveError(QuotaPoolExhaustedError):
    """Raised when a calibration target already sits inside an active quota cooldown window."""

    def __init__(self, retry_after_seconds: float, message: str) -> None:
        super().__init__(message, retry_after_seconds=retry_after_seconds)


class JudgeCalibrationFactory(Protocol):
    """Port callback building an isolated judge adapter for one calibration target."""

    def __call__(
        self,
        *,
        provider: str,
        model: str,
        threshold: float,
        enable_fallback: bool,
    ) -> LlmJudgePort:
        """Return a configured LlmJudgePort with explicit fallback mode."""
        ...


class CalibrationEventKind(StrEnum):
    """Event discriminators emitted during calibration execution."""

    SUITE_STARTED = "suite_started"
    STAGE_STARTED = "stage_started"
    CHECKPOINT_RESUMED = "checkpoint_resumed"
    PACING_INFO = "pacing_info"
    COOLDOWN_WAIT = "cooldown_wait"
    COOLDOWN_ABORT = "cooldown_abort"
    COOLDOWN_SKIP = "cooldown_skip"
    RETRY_WAIT = "retry_wait"
    ITEM_EVALUATED = "item_evaluated"
    TARGET_ERROR = "target_error"
    REPORT_SAVED = "report_saved"


@dataclass(frozen=True, slots=True)
class CalibrationEvent:
    """Immutable progress event emitted by calibration executor/suite."""

    kind: CalibrationEventKind
    message: str
    stage: str = ""
    provider: str = ""
    model: str = ""
    item_id: str = ""


def _emit(
    on_event: Callable[[CalibrationEvent], None] | None,
    event: CalibrationEvent,
) -> None:
    if on_event is not None:
        on_event(event)


def extract_cooldown_seconds(exc: BaseException) -> float | None:
    """Extract cooldown duration from domain/pool rate-limit errors.

    Args:
        exc: Raised exception instance.

    Returns:
        Non-negative cooldown duration in seconds, or ``None`` if not applicable.
    """
    if isinstance(exc, RateLimitExceededError):
        retry_val = getattr(exc, "retry_after_seconds", None)
        if isinstance(retry_val, int | float):
            return max(0.0, float(retry_val))
    return None


def is_transient_retryable_error(
    exc: Exception,
    *,
    is_quota_exhausted: Callable[[Exception], bool] | None = None,
) -> bool:
    """Identify transient server/network failures worth bounded retry backoff.

    Args:
        exc: Raised exception instance.
        is_quota_exhausted: Optional provider-specific quota classifier.

    Returns:
        ``True`` if the failure is transient and safe to retry, ``False`` otherwise.
    """
    if isinstance(exc, RateLimitExceededError):
        return False
    if is_quota_exhausted is not None and is_quota_exhausted(exc):
        return False
    msg = str(exc).lower()
    if any(q in msg for q in ("resource_exhausted", "429", "quota exceeded", "too many requests")):
        return False
    transient_markers = ("503", "504", "unavailable", "timeout", "connection reset", "timed out")
    return any(marker in msg for marker in transient_markers)


def evaluate_single_item(
    judge: LlmJudgePort,
    spec: StageCalibrationSpec,
    item: dict[str, Any],
) -> ItemEvaluationResult:
    """Invoke `judge.evaluate` for one golden set item uniformly across stages.

    Args:
        judge: Configured zero-fallback judge adapter.
        spec: Stage calibration specification.
        item: Golden set or seed evaluation item payload.

    Returns:
        ``ItemEvaluationResult`` containing global and target-isolated outcomes.
    """
    raw_text = item["input"]["raw_text"]
    candidate_text = item["input"]["candidate_text"]
    expected_verdict = str(item["expected_output"]["verdict"]).upper().strip()
    target_criterion_name = str(item.get("metadata", {}).get("criterion", "")).strip()

    context = EvaluationContext(
        stage_name=spec.stage_name,
        raw_text=raw_text,
        candidate_text=candidate_text,
        required_criteria=spec.required_criteria,
        judge_prompt_key=spec.prompt_key,
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


def run_stage_calibration(
    judge: LlmJudgePort,
    spec: StageCalibrationSpec,
    items: list[dict[str, Any]],
    *,
    provider: str,
    model: str,
    config_hash: str,
    checkpoint_store: CalibrationCheckpointPort,
    delay: float = 4.2,
    jitter: float = 0.8,
    max_retry_wait: float = 60.0,
    is_quota_exhausted: Callable[[Exception], bool] | None = None,
    now_fn: Callable[[], float] = time.time,
    sleep_fn: Callable[[float], None] = time.sleep,
    uniform_fn: Callable[[float, float], float] = random.uniform,
    on_event: Callable[[CalibrationEvent], None] | None = None,
) -> CalibrationResultSet:
    """Run incremental checkpointed calibration for one `(stage, provider, model)` target.

    Args:
        judge: Configured zero-fallback judge port.
        spec: Declarative stage specification.
        items: Evaluation items to process.
        provider: Provider identifier.
        model: Model identifier.
        config_hash: Deterministic configuration digest for checkpoint validation.
        checkpoint_store: Port persisting evaluated items and cooldown timestamps.
        delay: Base pacing delay in seconds between item evaluations.
        jitter: Upper bound for random pacing jitter in seconds.
        max_retry_wait: Maximum short cooldown wait before parking target in checkpoint.
        is_quota_exhausted: Optional provider-specific quota classifier.
        now_fn: Injectable clock returning epoch seconds.
        sleep_fn: Injectable sleep function.
        uniform_fn: Injectable uniform random generator for jitter.
        on_event: Optional progress event observer callback.

    Returns:
        Aggregated ``CalibrationResultSet`` across resumed and newly evaluated items.

    Raises:
        CooldownActiveError: If the target is currently inside an active cooldown window.
    """
    active_until = checkpoint_store.active_cooldown_until(
        stage=spec.stage_name,
        provider=provider,
        model=model,
        now=now_fn(),
    )
    if active_until is not None:
        remaining = max(0.0, active_until - now_fn())
        raise CooldownActiveError(
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
    _emit(
        on_event,
        CalibrationEvent(
            kind=CalibrationEventKind.STAGE_STARTED,
            message=f"CALIBRATING [{spec.stage_name.upper()}] -> {provider}:{model}",
            stage=spec.stage_name,
            provider=provider,
            model=model,
        ),
    )
    if results.skipped_from_checkpoint > 0:
        _emit(
            on_event,
            CalibrationEvent(
                kind=CalibrationEventKind.CHECKPOINT_RESUMED,
                message=(
                    f"Checkpoint resume: {results.skipped_from_checkpoint}/{total_items} restored, "
                    f"{len(pending_items)} pending."
                ),
                stage=spec.stage_name,
                provider=provider,
                model=model,
            ),
        )
    if delay > 0 and pending_items:
        _emit(
            on_event,
            CalibrationEvent(
                kind=CalibrationEventKind.PACING_INFO,
                message=(
                    f"Pacing: {delay:.1f}s base delay + up to {jitter:.1f}s jitter between calls"
                ),
                stage=spec.stage_name,
                provider=provider,
                model=model,
            ),
        )

    for idx, item in enumerate(pending_items, start=1):
        item_id = str(item.get("id", f"item_{idx}"))
        eval_res: ItemEvaluationResult | None = None
        short_cooldown_attempts = 0
        transient_attempts = 0

        while True:
            try:
                eval_res = evaluate_single_item(judge, spec, item)
                break
            except Exception as exc:
                retry_after = extract_cooldown_seconds(exc)
                if retry_after is not None:
                    if retry_after <= max_retry_wait and short_cooldown_attempts < 5:
                        short_cooldown_attempts += 1
                        wait_s = max(retry_after, 0.5) + 0.5
                        _emit(
                            on_event,
                            CalibrationEvent(
                                kind=CalibrationEventKind.COOLDOWN_WAIT,
                                message=(
                                    f"  [COOLDOWN WAIT {short_cooldown_attempts}/5] {item_id}: "
                                    f"waiting {wait_s:.1f}s ({exc})"
                                ),
                                stage=spec.stage_name,
                                provider=provider,
                                model=model,
                                item_id=item_id,
                            ),
                        )
                        sleep_fn(wait_s)
                        continue
                    until_ts = now_fn() + max(retry_after, max_retry_wait)
                    checkpoint_store.record_cooldown(spec.stage_name, provider, model, until_ts)
                    _emit(
                        on_event,
                        CalibrationEvent(
                            kind=CalibrationEventKind.COOLDOWN_ABORT,
                            message=(
                                f"  [COOLDOWN ABORT] {spec.stage_name} | {provider}:{model} "
                                f"parked for {retry_after:.0f}s (checkpoint saved)."
                            ),
                            stage=spec.stage_name,
                            provider=provider,
                            model=model,
                            item_id=item_id,
                        ),
                    )
                    raise
                if (
                    is_transient_retryable_error(exc, is_quota_exhausted=is_quota_exhausted)
                    and transient_attempts < 3
                ):
                    transient_attempts += 1
                    backoff = (2.0**transient_attempts) * 1.5
                    _emit(
                        on_event,
                        CalibrationEvent(
                            kind=CalibrationEventKind.RETRY_WAIT,
                            message=(
                                f"  [RETRY {transient_attempts}/3] Transient error on '{item_id}': "
                                f"{exc}. Waiting {backoff:.1f}s..."
                            ),
                            stage=spec.stage_name,
                            provider=provider,
                            model=model,
                            item_id=item_id,
                        ),
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

        _emit(
            on_event,
            CalibrationEvent(
                kind=CalibrationEventKind.ITEM_EVALUATED,
                message=(
                    f"[{results.skipped_from_checkpoint + idx:02d}/{total_items:02d}] "
                    f"[{item_id:<28}] Exp: {eval_res.expected:<4} | "
                    f"Target: {eval_res.target_actual:<4} ({eval_res.target_score:.2f}) -> "
                    f"{status_target}"
                ),
                stage=spec.stage_name,
                provider=provider,
                model=model,
                item_id=item_id,
            ),
        )

        if idx < len(pending_items) and (delay + jitter) > 0:
            sleep_fn(delay + uniform_fn(0.0, jitter))

    checkpoint_store.clear_cooldown(spec.stage_name, provider, model)
    return results
