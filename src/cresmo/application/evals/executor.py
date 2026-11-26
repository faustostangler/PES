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
from typing import Any, Final, Protocol

from cresmo.application.evals.calibration_metrics import (
    VERDICT_FAIL,
    VERDICT_PASS,
    CalibrationResultSet,
    ConfusionMatrix,
    ItemEvaluationResult,
)
from cresmo.application.evals.specs import StageCalibrationSpec
from cresmo.application.ports.evals import CalibrationCheckpointPort
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.domain.exceptions import QuotaPoolExhaustedError, RateLimitExceededError
from cresmo.domain.value_objects.quality import EvaluationContext, JudgeCriterion

DEFAULT_CALIBRATION_DELAY_SECONDS: Final[float] = 4.2
DEFAULT_CALIBRATION_JITTER_SECONDS: Final[float] = 0.8
DEFAULT_MAX_RETRY_WAIT_SECONDS: Final[float] = 60.0
MAX_SHORT_COOLDOWN_ATTEMPTS: Final[int] = 5
MIN_COOLDOWN_WAIT_SECONDS: Final[float] = 0.5
COOLDOWN_BUFFER_SECONDS: Final[float] = 0.5
MAX_TRANSIENT_RETRY_ATTEMPTS: Final[int] = 3
TRANSIENT_BACKOFF_BASE: Final[float] = 2.0
TRANSIENT_BACKOFF_MULTIPLIER: Final[float] = 1.5

_QUOTA_ERROR_MARKERS: Final[tuple[str, ...]] = (
    "resource_exhausted",
    "429",
    "quota exceeded",
    "too many requests",
)
_TRANSIENT_ERROR_MARKERS: Final[tuple[str, ...]] = (
    "503",
    "504",
    "unavailable",
    "timeout",
    "connection reset",
    "timed out",
)
_ITEM_KEY_INPUT: Final[str] = "input"
_ITEM_KEY_RAW_TEXT: Final[str] = "raw_text"
_ITEM_KEY_CANDIDATE_TEXT: Final[str] = "candidate_text"
_ITEM_KEY_EXPECTED_OUTPUT: Final[str] = "expected_output"
_ITEM_KEY_VERDICT: Final[str] = "verdict"
_ITEM_KEY_METADATA: Final[str] = "metadata"
_KEY_ID: Final[str] = "id"
_KEY_CRITERION: Final[str] = "criterion"
_KEY_DIFFICULTY: Final[str] = "difficulty"
_KEY_EXPECTED: Final[str] = "expected"
_KEY_ACTUAL: Final[str] = "actual"
_KEY_ACTUAL_TARGET: Final[str] = "actual_target"
_KEY_ACTUAL_GLOBAL: Final[str] = "actual_global"
_KEY_TARGET_ACTUAL: Final[str] = "target_actual"
_KEY_TARGET_SCORE: Final[str] = "target_score"
_KEY_SCORE: Final[str] = "score"
_KEY_ANOMALY: Final[str] = "anomaly"
_KEY_EXPECTED_ANOMALY: Final[str] = "expected_anomaly"
_KEY_REASONING: Final[str] = "reasoning"
_DEFAULT_ITEM_ID: Final[str] = "item"
_DEFAULT_CRITERION_NAME: Final[str] = "general"
_DEFAULT_DIFFICULTY: Final[str] = "typical"
_FALLBACK_ITEM_ID_PREFIX: Final[str] = "item_"


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
    if isinstance(exc, QuotaPoolExhaustedError):
        return exc.retry_after_seconds
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
    if any(q in msg for q in _QUOTA_ERROR_MARKERS):
        return False
    return any(marker in msg for marker in _TRANSIENT_ERROR_MARKERS)


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
    raw_text = item[_ITEM_KEY_INPUT][_ITEM_KEY_RAW_TEXT]
    candidate_text = item[_ITEM_KEY_INPUT][_ITEM_KEY_CANDIDATE_TEXT]
    expected_verdict = str(item[_ITEM_KEY_EXPECTED_OUTPUT][_ITEM_KEY_VERDICT]).upper().strip()
    target_criterion_name = str(item.get(_ITEM_KEY_METADATA, {}).get(_KEY_CRITERION, "")).strip()

    context = EvaluationContext(
        stage_name=spec.stage_name,
        raw_text=raw_text,
        candidate_text=candidate_text,
        required_criteria=spec.required_criteria,
        judge_prompt_key=spec.prompt_key,
    )

    evaluation = judge.evaluate(context)
    global_actual = VERDICT_PASS if evaluation.passed else VERDICT_FAIL
    global_score = float(evaluation.overall_score)
    reasoning = evaluation.extract_critique()

    target_actual = global_actual
    target_score = global_score
    if target_criterion_name:
        try:
            crit_vo = JudgeCriterion(target_criterion_name)
            crit_score = evaluation.get_score(crit_vo)
            if crit_score is not None:
                target_actual = VERDICT_PASS if crit_score.passed else VERDICT_FAIL
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
    item_id = str(item.get(_KEY_ID, _DEFAULT_ITEM_ID))
    metadata = item.get(_ITEM_KEY_METADATA, {})
    criterion = str(metadata.get(_KEY_CRITERION, _DEFAULT_CRITERION_NAME))
    difficulty = str(metadata.get(_KEY_DIFFICULTY, _DEFAULT_DIFFICULTY))

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
                _KEY_ID: item_id,
                _KEY_CRITERION: criterion,
                _KEY_DIFFICULTY: difficulty,
                _KEY_EXPECTED: eval_res.expected,
                _KEY_ACTUAL_TARGET: eval_res.target_actual,
                _KEY_ACTUAL_GLOBAL: eval_res.actual,
                _KEY_SCORE: eval_res.target_score,
                _KEY_ANOMALY: metadata.get(_KEY_EXPECTED_ANOMALY, ""),
                _KEY_REASONING: eval_res.reasoning,
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
    delay: float = DEFAULT_CALIBRATION_DELAY_SECONDS,
    jitter: float = DEFAULT_CALIBRATION_JITTER_SECONDS,
    max_retry_wait: float = DEFAULT_MAX_RETRY_WAIT_SECONDS,
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
        QuotaPoolExhaustedError: If the target is currently inside an active cooldown window.
    """
    active_until = checkpoint_store.active_cooldown_until(
        stage=spec.stage_name,
        provider=provider,
        model=model,
        now=now_fn(),
    )
    if active_until is not None:
        remaining = max(0.0, active_until - now_fn())
        raise QuotaPoolExhaustedError(
            f"Cooldown active for {provider}:{model} ({remaining:.0f}s remaining).",
            retry_after_seconds=remaining,
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
        item_id = str(item.get(_KEY_ID, _DEFAULT_ITEM_ID))
        saved = completed_map.get(item_id)
        if saved is not None:
            saved_eval = ItemEvaluationResult(
                actual=str(saved[_KEY_ACTUAL]),
                expected=str(saved[_KEY_EXPECTED]),
                score=float(saved[_KEY_SCORE]),
                reasoning=str(saved.get(_KEY_REASONING, "")),
                target_actual=str(saved.get(_KEY_TARGET_ACTUAL, saved[_KEY_ACTUAL])),
                target_score=float(saved.get(_KEY_TARGET_SCORE, saved[_KEY_SCORE])),
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
        item_id = str(item.get(_KEY_ID, f"{_FALLBACK_ITEM_ID_PREFIX}{idx}"))
        short_cooldown_attempts = 0
        transient_attempts = 0

        while True:
            try:
                eval_res = evaluate_single_item(judge, spec, item)
                break
            except Exception as exc:
                retry_after = extract_cooldown_seconds(exc)
                if retry_after is not None:
                    if (
                        retry_after <= max_retry_wait
                        and short_cooldown_attempts < MAX_SHORT_COOLDOWN_ATTEMPTS
                    ):
                        short_cooldown_attempts += 1
                        wait_s = max(retry_after, MIN_COOLDOWN_WAIT_SECONDS) + COOLDOWN_BUFFER_SECONDS
                        _emit(
                            on_event,
                            CalibrationEvent(
                                kind=CalibrationEventKind.COOLDOWN_WAIT,
                                message=(
                                    f"  [COOLDOWN WAIT {short_cooldown_attempts}/{MAX_SHORT_COOLDOWN_ATTEMPTS}] "
                                    f"{item_id}: waiting {wait_s:.1f}s ({exc})"
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
                    and transient_attempts < MAX_TRANSIENT_RETRY_ATTEMPTS
                ):
                    transient_attempts += 1
                    backoff = (
                        TRANSIENT_BACKOFF_BASE**transient_attempts
                    ) * TRANSIENT_BACKOFF_MULTIPLIER
                    _emit(
                        on_event,
                        CalibrationEvent(
                            kind=CalibrationEventKind.RETRY_WAIT,
                            message=(
                                f"  [RETRY {transient_attempts}/{MAX_TRANSIENT_RETRY_ATTEMPTS}] "
                                f"Transient error on '{item_id}': {exc}. Waiting {backoff:.1f}s..."
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

        checkpoint_store.record_item(
            stage=spec.stage_name,
            provider=provider,
            model=model,
            config_hash=config_hash,
            item_id=item_id,
            payload={
                _KEY_ACTUAL: eval_res.actual,
                _KEY_EXPECTED: eval_res.expected,
                _KEY_SCORE: eval_res.score,
                _KEY_REASONING: eval_res.reasoning,
                _KEY_TARGET_ACTUAL: eval_res.target_actual,
                _KEY_TARGET_SCORE: eval_res.target_score,
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
