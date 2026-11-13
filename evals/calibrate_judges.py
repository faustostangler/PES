#!/usr/bin/env python3
"""Unified Zero-Fallback LLM Judge Calibration CLI with Cooldown Checkpointing.

Thin Humble Object Typer CLI delegating calibration metrics, checkpointing, and
stage orchestration to `cresmo.application.evals`.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI with Cooldown-Aware Checkpointing
    - ADR-062: Structural Consolidation, Evals SSOT, and Bootstrap Separation
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import click
import typer
from dotenv import load_dotenv

# Ensure `cresmo` resolves cleanly when executed via `python evals/calibrate_judges.py`
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
for path_entry in (str(SRC_DIR), str(REPO_ROOT)):
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

from cresmo.application.evals import (
    PromptTemplateLookup,
    build_stage_specs,
    parse_model_specs,
    parse_stage_specs,
    run_calibration_suite,
)
from cresmo.application.ports.llm_judge_port import LlmJudgePort
from cresmo.bootstrap.factories.judge_factory import build_llm_judge_adapter
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.infrastructure.adapters.llm.gemini_pool import is_quota_exhausted_error
from cresmo.infrastructure.adapters.prompts import load_prompt_catalog
from cresmo.infrastructure.config import CresmoSettings

DEFAULT_CHECKPOINT_DIR = REPO_ROOT / "data" / "calibration_checkpoints"
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports" / "calibration"
DEFAULT_DATASETS_DIR = REPO_ROOT / "evals" / "datasets"

app = typer.Typer(
    name="calibrate-judges",
    help=(
        "Unified zero-fallback LLM Judge calibration harness across pipeline stages. "
        "Always resumes incrementally from checkpoints and skips models in cooldown."
    ),
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _build_prompt_lookup() -> PromptTemplateLookup:
    """Resolve prompt system/user templates for calibration config hashing."""
    catalog = load_prompt_catalog()

    def _lookup(prompt_key: PromptKey) -> dict[str, str]:
        if prompt_key not in catalog:
            return {"system_prompt": "", "user_prompt": ""}
        spec = catalog[prompt_key]
        return {"system_prompt": spec.system_prompt, "user_prompt": spec.user_prompt}

    return _lookup


@app.command()
def run_cli(
    stages: Annotated[
        list[str] | None,
        typer.Option(
            "--stages",
            help="Stages to calibrate (comma-separated or repeated: fluid_prose, gap_filler, all).",
        ),
    ] = None,
    stage: Annotated[
        str | None,
        typer.Option(
            "--stage",
            help="Single stage override (e.g. fluid_prose or gap_filler).",
        ),
    ] = None,
    models: Annotated[
        list[str] | None,
        typer.Option(
            "--models",
            help="Models to benchmark (comma-separated or repeated, e.g. gemini:gemini-4-hydrogen).",
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            help="Single model override (e.g. gemini:gemini-3.8-flash).",
        ),
    ] = None,
    provider: Annotated[
        str,
        typer.Option(
            "--provider",
            help="Default provider prefix when a model spec omits 'provider:'.",
        ),
    ] = "gemini",
    threshold: Annotated[
        float | None,
        typer.Option(
            "--threshold",
            help="Explicit judge pass threshold override.",
        ),
    ] = None,
    dataset_path: Annotated[
        Path | None,
        typer.Option(
            "--dataset-path",
            help="Explicit golden set JSON path (valid only when calibrating one stage).",
        ),
    ] = None,
    seed_only: Annotated[
        bool,
        typer.Option(
            "--seed-only",
            help="Run built-in seed calibration items instead of full golden set files.",
        ),
    ] = False,
    delay: Annotated[
        float,
        typer.Option(
            "--delay",
            help="Base pacing delay in seconds between fresh LLM calls.",
        ),
    ] = 4.2,
    jitter: Annotated[
        float,
        typer.Option(
            "--jitter",
            help="Random additional pacing jitter in seconds.",
        ),
    ] = 0.8,
    max_retry_wait: Annotated[
        float,
        typer.Option(
            "--max-retry-wait",
            help="Max seconds to wait in-place on short cooldowns before parking in COOLDOWN.",
        ),
    ] = 60.0,
    output_path: Annotated[
        Path | None,
        typer.Option(
            "--output-path",
            help="Explicit output directory (multi-target) or file path (single target).",
        ),
    ] = None,
) -> None:
    """Execute unified zero-fallback calibration across selected stages and models."""
    load_dotenv(REPO_ROOT / ".env", override=False)
    base_settings = CresmoSettings()
    stage_specs = build_stage_specs(datasets_dir=DEFAULT_DATASETS_DIR)

    try:
        selected_stages = parse_stage_specs(stages, stage, stage_specs=stage_specs)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    selected_models = parse_model_specs(
        models,
        model,
        default_provider=provider,
        default_models=base_settings.judge_calibration_models,
    )
    if dataset_path is not None and len(selected_stages) > 1:
        raise typer.BadParameter("--dataset-path can only be used with a single --stage.")

    stage_thresholds = {
        "fluid_prose": threshold if threshold is not None else base_settings.judge_pass_threshold,
        "gap_filler": (
            threshold if threshold is not None else base_settings.gap_filler_judge_threshold
        ),
    }

    def _build_judge(
        *,
        provider: str,
        model: str,
        threshold: float,
        enable_fallback: bool,
    ) -> LlmJudgePort:
        updates: dict[str, object] = {
            "judge_provider": provider,
            "judge_pass_threshold": threshold,
            "gap_filler_judge_threshold": threshold,
        }
        if provider == "gemini":
            updates["judge_gemini_model"] = model
        elif provider == "ollama":
            updates["ollama_model"] = model
        elif provider == "typesafe":
            updates["typesafe_model"] = model
        stage_settings = base_settings.model_copy(update=updates)
        return build_llm_judge_adapter(settings=stage_settings, enable_fallback=enable_fallback)

    outcome = run_calibration_suite(
        selected_stages=selected_stages,
        selected_models=selected_models,
        judge_factory=_build_judge,
        stage_thresholds=stage_thresholds,
        stage_specs=stage_specs,
        dataset_path=dataset_path,
        seed_only=seed_only,
        checkpoint_dir=DEFAULT_CHECKPOINT_DIR,
        reports_dir=DEFAULT_REPORTS_DIR,
        output_path=output_path,
        delay=delay,
        jitter=jitter,
        max_retry_wait=max_retry_wait,
        prompt_lookup=_build_prompt_lookup(),
        is_quota_exhausted=is_quota_exhausted_error,
    )
    if outcome.has_errors:
        raise typer.Exit(code=1)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint delegating to Typer without standalone process exit."""
    try:
        app(args=list(argv) if argv is not None else None, standalone_mode=False)
        return 0
    except click.exceptions.Exit as exc:
        return int(exc.exit_code)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
