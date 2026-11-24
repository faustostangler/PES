"""Multi-stage and multi-model judge calibration suite orchestrator.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from cresmo.application.evals.calibration_metrics import (
    CalibrationResultSet,
    CalibrationSuiteOutcome,
    CalibrationVerdict,
    ModelBenchmarkSummary,
)
from cresmo.application.evals.executor import (
    CalibrationEvent,
    CalibrationEventKind,
    JudgeCalibrationFactory,
    _emit,
    extract_cooldown_seconds,
    run_stage_calibration,
)
from cresmo.application.evals.specs import (
    DEFAULT_REPORTS_DIR,
    CalibrationThresholds,
    PromptTemplateLookup,
    StageCalibrationSpec,
    classify_verdict,
    compute_config_hash,
    sanitize_report_filename,
)
from cresmo.application.ports.evals import (
    CalibrationCheckpointPort,
    CalibrationDatasetPort,
    CalibrationReportWriterPort,
)

ReportContentBuilder = Callable[[StageCalibrationSpec, CalibrationResultSet, str, str], str]


def run_calibration_suite(
    *,
    selected_stages: Sequence[str],
    selected_models: Sequence[tuple[str, str]],
    judge_factory: JudgeCalibrationFactory,
    stage_thresholds: Mapping[str, float],
    stage_specs: Mapping[str, StageCalibrationSpec],
    checkpoint_store: CalibrationCheckpointPort,
    dataset_loader: CalibrationDatasetPort,
    report_writer: CalibrationReportWriterPort,
    verdict_thresholds: CalibrationThresholds | None = None,
    dataset_path: Path | None = None,
    seed_only: bool = False,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    output_path: Path | None = None,
    delay: float = 4.2,
    jitter: float = 0.8,
    max_retry_wait: float = 60.0,
    prompt_lookup: PromptTemplateLookup | None = None,
    is_quota_exhausted: Callable[[Exception], bool] | None = None,
    report_builder: ReportContentBuilder | None = None,
    now_fn: Callable[[], float] = time.time,
    sleep_fn: Callable[[float], None] = time.sleep,
    on_event: Callable[[CalibrationEvent], None] | None = None,
) -> CalibrationSuiteOutcome:
    """Orchestrate zero-fallback calibration across selected stages and model targets.

    Args:
        selected_stages: Ordered sequence of stage names to calibrate.
        selected_models: Ordered sequence of ``(provider, model)`` pairs to calibrate.
        judge_factory: Factory instantiating isolated zero-fallback judges.
        stage_thresholds: Mapping from stage name to judge acceptance threshold.
        stage_specs: Mapping from stage name to declarative ``StageCalibrationSpec``.
        checkpoint_store: Port persisting evaluated items and cooldown timestamps.
        dataset_loader: Port loading golden sets and seed JSON datasets.
        report_writer: Port persisting rendered calibration reports.
        verdict_thresholds: Optional parameterized thresholds for ``classify_verdict``.
        dataset_path: Optional explicit dataset override (requires single stage).
        seed_only: When ``True``, bypass golden set and load canonical seed dataset.
        reports_dir: Default directory for per-target calibration reports.
        output_path: Optional explicit report file (single target) or directory override.
        delay: Base pacing delay in seconds between item evaluations.
        jitter: Upper bound for random pacing jitter in seconds.
        max_retry_wait: Maximum short cooldown wait before parking target in checkpoint.
        prompt_lookup: Optional callable supplying prompt templates for config hashing.
        is_quota_exhausted: Optional provider-specific quota classifier.
        report_builder: Optional formatter callback converting results into report text.
        now_fn: Injectable clock returning epoch seconds.
        sleep_fn: Injectable sleep function.
        on_event: Optional progress event observer callback.

    Returns:
        ``CalibrationSuiteOutcome`` containing all per-target summaries and error flag.

    Raises:
        ValueError: If ``dataset_path`` is supplied alongside multiple stages.
    """
    if dataset_path is not None and len(selected_stages) > 1:
        raise ValueError("--dataset-path can only be used with a single --stage.")

    summaries: list[ModelBenchmarkSummary] = []
    has_errors = False

    _emit(
        on_event,
        CalibrationEvent(
            kind=CalibrationEventKind.SUITE_STARTED,
            message=(
                f"Stages scheduled ({len(selected_stages)}): {', '.join(selected_stages)} | "
                f"Models scheduled ({len(selected_models)}): "
                f"{', '.join(f'{p}:{m}' for p, m in selected_models)}"
            ),
        ),
    )

    for stage_name in selected_stages:
        spec = stage_specs[stage_name]
        items = dataset_loader.load_items(
            stage_name,
            spec.default_golden_set_path,
            spec.default_seed_path,
            dataset_path=dataset_path,
            seed_only=seed_only,
        )
        active_threshold = stage_thresholds.get(stage_name, 0.75)
        config_hash = compute_config_hash(
            spec,
            items,
            active_threshold,
            prompt_lookup=prompt_lookup,
        )

        for prov, mod in selected_models:
            now_ts = now_fn()
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
                _emit(
                    on_event,
                    CalibrationEvent(
                        kind=CalibrationEventKind.COOLDOWN_SKIP,
                        message=(
                            f"[COOLDOWN SKIP] {stage_name} | {prov}:{mod} in cooldown for "
                            f"{rem:.0f}s ({completed_count}/{len(items)} checkpointed)."
                        ),
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                    ),
                )
                summaries.append(
                    ModelBenchmarkSummary(
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                        status=CalibrationVerdict.COOLDOWN,
                        evaluated_total=completed_count,
                        dataset_total=len(items),
                        cooldown_remaining_s=rem,
                    )
                )
                continue

            try:
                # Zero-fallback enforced unconditionally to guarantee pure per-model telemetry.
                judge = judge_factory(
                    provider=prov,
                    model=mod,
                    threshold=active_threshold,
                    enable_fallback=False,
                )
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
                    is_quota_exhausted=is_quota_exhausted,
                    now_fn=now_fn,
                    sleep_fn=sleep_fn,
                    on_event=on_event,
                )
                tm = results.target_isolated
                verdict = classify_verdict(tm, verdict_thresholds)

                if report_builder is not None:
                    single_target = len(selected_stages) == 1 and len(selected_models) == 1
                    if output_path is not None:
                        report_dest = (
                            output_path
                            if single_target
                            else output_path / sanitize_report_filename(stage_name, prov, mod)
                        )
                    else:
                        report_dest = reports_dir / sanitize_report_filename(stage_name, prov, mod)
                    report_text = report_builder(spec, results, prov, mod)
                    saved_path = report_writer.write_report(report_dest, report_text)
                    _emit(
                        on_event,
                        CalibrationEvent(
                            kind=CalibrationEventKind.REPORT_SAVED,
                            message=f"Saved calibration report: {saved_path}",
                            stage=stage_name,
                            provider=prov,
                            model=mod,
                        ),
                    )

                summaries.append(
                    ModelBenchmarkSummary(
                        stage=stage_name,
                        provider=prov,
                        model=mod,
                        status=verdict,
                        accuracy=tm.accuracy,
                        d_prime=tm.d_prime,
                        f1=tm.f1,
                        precision=tm.precision,
                        recall=tm.recall,
                        alpha_fpr=tm.alpha_fpr,
                        evaluated_total=tm.total_samples,
                        dataset_total=len(items),
                    )
                )
            except Exception as exc:  # noqa: BLE001
                retry_after = extract_cooldown_seconds(exc)
                saved_after = len(
                    checkpoint_store.load_completed_items(stage_name, prov, mod, config_hash)
                )
                if retry_after is not None:
                    summaries.append(
                        ModelBenchmarkSummary(
                            stage=stage_name,
                            provider=prov,
                            model=mod,
                            status=CalibrationVerdict.COOLDOWN,
                            evaluated_total=saved_after,
                            dataset_total=len(items),
                            cooldown_remaining_s=retry_after,
                        )
                    )
                else:
                    has_errors = True
                    _emit(
                        on_event,
                        CalibrationEvent(
                            kind=CalibrationEventKind.TARGET_ERROR,
                            message=f"[ERROR] {stage_name} | {prov}:{mod} failed: {exc}",
                            stage=stage_name,
                            provider=prov,
                            model=mod,
                        ),
                    )
                    summaries.append(
                        ModelBenchmarkSummary(
                            stage=stage_name,
                            provider=prov,
                            model=mod,
                            status=CalibrationVerdict.ERROR,
                            evaluated_total=saved_after,
                            dataset_total=len(items),
                            error_message=str(exc),
                        )
                    )

    return CalibrationSuiteOutcome(summaries=tuple(summaries), has_errors=has_errors)
