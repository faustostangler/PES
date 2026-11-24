"""Declarative specifications, spec parsers, thresholds, and config hashing for calibration.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cresmo.application.evals.calibration_metrics import CalibrationVerdict, ConfusionMatrix
from cresmo.domain.stage_registry import StageName, StageRegistry
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.quality import JudgeCriterion

DEFAULT_CHECKPOINT_DIR = Path("data") / "calibration_checkpoints"
DEFAULT_REPORTS_DIR = Path("reports") / "calibration"
DEFAULT_DATASETS_DIR = Path("evals") / "datasets"

PromptTemplateLookup = Callable[[PromptKey], dict[str, str]]


@dataclass(frozen=True, slots=True)
class CalibrationThresholds:
    """Configurable accuracy and false-acceptance gates for calibration verdicts."""

    approved_min_accuracy: float = 0.85
    approved_max_false_accept: int = 0
    pre_calibrated_min_accuracy: float = 0.80


@dataclass(frozen=True, slots=True)
class StageCalibrationSpec:
    """Declarative specification defining calibration behavior for a pipeline stage."""

    stage_name: str
    label: str
    prompt_key: PromptKey
    default_golden_set_path: Path
    default_seed_path: Path
    required_criteria: tuple[JudgeCriterion, ...]


def build_stage_specs(
    datasets_dir: Path = DEFAULT_DATASETS_DIR,
    seeds_dir: Path | None = None,
) -> dict[str, StageCalibrationSpec]:
    """Build stage calibration specifications rooted under the supplied datasets directories.

    Args:
        datasets_dir: Directory containing golden set JSON files.
        seeds_dir: Directory containing externalized seed JSON files. Defaults to
            ``datasets_dir / "seeds"``.

    Returns:
        Mapping from canonical stage name to its ``StageCalibrationSpec``.
    """
    resolved_seeds_dir = seeds_dir if seeds_dir is not None else datasets_dir / "seeds"
    stage_configs = (
        (StageName.FLUID_PROSE, "Stage 1: Fluid Prose", PromptKey.JUDGE_FLUID_PROSE),
        (StageName.GAP_FILLER, "Stage 2: Gap Filler", PromptKey.JUDGE_GAP_FILLER),
        (StageName.LONG_EXPANDER, "Stage 3: Long Expander", PromptKey.JUDGE_LONG_EXPANDER),
        (StageName.WIDE_EXPANDER, "Stage 4: Wide Expander", PromptKey.JUDGE_WIDE_EXPANDER),
    )
    specs: dict[str, StageCalibrationSpec] = {}
    for stage_enum, label, fallback_prompt_key in stage_configs:
        stage_key = stage_enum.value
        stage_def = StageRegistry.get(stage_key)
        specs[stage_key] = StageCalibrationSpec(
            stage_name=stage_key,
            label=label,
            prompt_key=stage_def.judge_prompt_key or fallback_prompt_key,
            default_golden_set_path=datasets_dir / f"{stage_key}_golden_set.json",
            default_seed_path=resolved_seeds_dir / f"{stage_key}_seed.json",
            required_criteria=stage_def.required_criteria,
        )
    return specs


def classify_verdict(
    matrix: ConfusionMatrix,
    thresholds: CalibrationThresholds | None = None,
) -> CalibrationVerdict:
    """Classify a confusion matrix into CalibrationVerdict per parameterized thresholds.

    Args:
        matrix: Evaluated target-isolated confusion matrix.
        thresholds: Optional threshold policy overriding defaults.

    Returns:
        Canonical ``CalibrationVerdict`` (APPROVED, PRE_CALIBRATED, or REJECTED).
    """
    policy = thresholds if thresholds is not None else CalibrationThresholds()
    if (
        matrix.accuracy >= policy.approved_min_accuracy
        and matrix.false_accept_alpha <= policy.approved_max_false_accept
    ):
        return CalibrationVerdict.APPROVED
    if matrix.accuracy >= policy.pre_calibrated_min_accuracy:
        return CalibrationVerdict.PRE_CALIBRATED
    return CalibrationVerdict.REJECTED


def resolve_model_spec(spec: str, default_provider: str = "gemini") -> tuple[str, str]:
    """Parse model specification string into canonical `(provider, model_name)` tuple.

    Args:
        spec: Raw CLI model identifier (optionally prefixed with ``provider:``).
        default_provider: Fallback provider when prefix/inference does not match.

    Returns:
        Canonical ``(provider, model_name)`` tuple.
    """
    cleaned = spec.strip()
    if ":" in cleaned:
        provider, model_name = cleaned.split(":", 1)
        return provider.strip().lower(), model_name.strip()
    lower = cleaned.lower()
    if lower.startswith(("gemini", "gemma")):
        return "gemini", cleaned
    if lower.startswith("ollama"):
        return "ollama", cleaned
    if lower.startswith("typesafe"):
        return "typesafe", cleaned
    return default_provider.strip().lower(), cleaned


def parse_stage_specs(
    stages: Sequence[str] | None,
    single_stage: str | None,
    *,
    stage_specs: Mapping[str, StageCalibrationSpec] | None = None,
) -> list[str]:
    """Expand stage flags supporting comma-separated values or repeated `--stages` flags.

    Args:
        stages: Optional sequence of stage flags or comma-separated tokens.
        single_stage: Optional single-stage override flag.
        stage_specs: Available stage registry (defaults to ``build_stage_specs()``).

    Returns:
        Deduplicated ordered list of canonical stage names.

    Raises:
        ValueError: If any requested stage token is not present in ``stage_specs``.
    """
    registry = build_stage_specs() if stage_specs is None else stage_specs
    raw_tokens: list[str] = []
    if stages:
        for entry in stages:
            raw_tokens.extend(part.strip() for part in entry.split(",") if part.strip())
    if single_stage is not None:
        raw_tokens.extend(part.strip() for part in single_stage.split(",") if part.strip())

    if not raw_tokens or "all" in [t.lower() for t in raw_tokens]:
        return list(registry.keys())

    resolved: list[str] = []
    for token in raw_tokens:
        norm = "_".join(token.lower().split("-"))
        if norm not in registry:
            valid = ", ".join(registry.keys())
            raise ValueError(f"Unknown stage '{token}'. Valid stages: {valid}, all.")
        if norm not in resolved:
            resolved.append(norm)
    return resolved


def parse_model_specs(
    models: Sequence[str] | None,
    single_model: str | None,
    default_provider: str = "gemini",
    *,
    default_models: Sequence[str] = (),
) -> list[tuple[str, str]]:
    """Expand explicit model flags or supplied defaults into `(provider, model)` pairs.

    Args:
        models: Optional sequence of model specs (comma-separated allowed).
        single_model: Optional single model flag.
        default_provider: Default provider used when unspecified.
        default_models: Fallback model specs when neither ``models`` nor ``single_model`` is set.

    Returns:
        Deduplicated ordered list of ``(provider, model_name)`` pairs.
    """
    raw_tokens: list[str] = []
    if models:
        for entry in models:
            raw_tokens.extend(part.strip() for part in entry.split(",") if part.strip())
    elif single_model is not None and single_model.strip():
        raw_tokens.append(single_model.strip())
    else:
        raw_tokens.extend(default_models)

    resolved: list[tuple[str, str]] = []
    for token in raw_tokens:
        pair = resolve_model_spec(token, default_provider=default_provider)
        if pair not in resolved:
            resolved.append(pair)
    return resolved


def sanitize_report_filename(stage: str, provider: str, model_name: str) -> str:
    """Generate clean filename slug for per-stage, per-model calibration report.

    Args:
        stage: Canonical stage name.
        provider: Judge provider name.
        model_name: Judge model identifier.

    Returns:
        Safe ASCII report filename ending in ``.txt``.
    """
    clean_model = model_name
    if clean_model.startswith(f"{provider}:"):
        clean_model = clean_model[len(provider) + 1 :]
    clean_model = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean_model)
    return f"llm_judge_{stage}_{provider}_{clean_model}.txt"


def compute_config_hash(
    spec: StageCalibrationSpec,
    items: list[dict[str, Any]],
    threshold: float,
    *,
    prompt_lookup: PromptTemplateLookup | None = None,
) -> str:
    """Compute SHA-256 hash over prompt template, criteria, threshold, and golden set items.

    Args:
        spec: Stage calibration specification.
        items: Evaluation dataset items.
        threshold: Judge acceptance threshold.
        prompt_lookup: Optional callable returning system/user prompts for ``spec.prompt_key``.

    Returns:
        Hex-encoded SHA-256 digest uniquely identifying the calibration configuration.
    """
    prompt_payload: dict[str, str] = {"system_prompt": "", "user_prompt": ""}
    if prompt_lookup is not None:
        try:
            prompt_payload = prompt_lookup(spec.prompt_key)
        except Exception as exc:  # noqa: BLE001
            logging.getLogger(__name__).debug(
                "Prompt lookup unavailable for config hash: %s",
                exc,
            )

    canonical = {
        "stage": spec.stage_name,
        "threshold": round(threshold, 6),
        "required_criteria": [c.value for c in spec.required_criteria],
        "prompt": prompt_payload,
        "items": items,
    }
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
