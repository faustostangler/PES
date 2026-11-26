"""Declarative specifications, spec parsers, thresholds, and config hashing for calibration.

Conforms to:
    - ADR-061: Unified Zero-Fallback LLM Judge Calibration CLI
    - ADR-068: Hexagonal Decomposition of Judge Calibration and JSON Seed SSOT
    - SPEC-068: Hexagonal Decomposition of Judge Calibration & Seed SSOT
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import structlog

from cresmo.application.evals.calibration_metrics import CalibrationVerdict, ConfusionMatrix
from cresmo.domain.stage_registry import StageName, StageRegistry
from cresmo.domain.value_objects.prompt import PromptKey
from cresmo.domain.value_objects.quality import JudgeCriterion

DEFAULT_REPORTS_DIR = Path("reports") / "calibration"
DEFAULT_DATASETS_DIR = Path("evals") / "datasets"

DEFAULT_APPROVED_MIN_ACCURACY: Final[float] = 0.85
DEFAULT_APPROVED_MAX_FALSE_ACCEPT: Final[int] = 0
DEFAULT_PRE_CALIBRATED_MIN_ACCURACY: Final[float] = 0.80
SEEDS_SUBDIR_NAME: Final[str] = "seeds"
STAGE_LABEL_FLUID_PROSE: Final[str] = "Stage 1: Fluid Prose"
STAGE_LABEL_GAP_FILLER: Final[str] = "Stage 2: Gap Filler"
STAGE_LABEL_LONG_EXPANDER: Final[str] = "Stage 3: Long Expander"
STAGE_LABEL_WIDE_EXPANDER: Final[str] = "Stage 4: Wide Expander"
GOLDEN_SET_FILE_SUFFIX: Final[str] = "_golden_set.json"
SEED_FILE_SUFFIX: Final[str] = "_seed.json"
PROVIDER_GEMINI: Final[str] = "gemini"
PROVIDER_OLLAMA: Final[str] = "ollama"
PROVIDER_TYPESAFE: Final[str] = "typesafe"
PROVIDER_MODEL_DELIMITER: Final[str] = ":"
MODEL_PREFIX_GEMMA: Final[str] = "gemma"
SPEC_LIST_DELIMITER: Final[str] = ","
STAGE_SELECTOR_ALL: Final[str] = "all"
STAGE_NAME_UNDERSCORE: Final[str] = "_"
STAGE_NAME_HYPHEN: Final[str] = "-"
DISPLAY_LIST_SEPARATOR: Final[str] = ", "
_FILENAME_SANITIZE_PATTERN: Final[re.Pattern[str]] = re.compile(r"[^a-zA-Z0-9_\-\.]")
_FILENAME_REPLACEMENT_CHAR: Final[str] = "_"
REPORT_FILENAME_PREFIX: Final[str] = "llm_judge_"
REPORT_FILENAME_EXTENSION: Final[str] = ".txt"
_HASH_KEY_SYSTEM_PROMPT: Final[str] = "system_prompt"
_HASH_KEY_USER_PROMPT: Final[str] = "user_prompt"
_HASH_KEY_STAGE: Final[str] = "stage"
_HASH_KEY_THRESHOLD: Final[str] = "threshold"
_HASH_KEY_REQUIRED_CRITERIA: Final[str] = "required_criteria"
_HASH_KEY_PROMPT: Final[str] = "prompt"
_HASH_KEY_ITEMS: Final[str] = "items"
CONFIG_HASH_THRESHOLD_PRECISION: Final[int] = 6
DEFAULT_ENCODING: Final[str] = "utf-8"

logger = structlog.get_logger(__name__)

PromptTemplateLookup = Callable[[PromptKey], dict[str, str]]


@dataclass(frozen=True, slots=True)
class CalibrationThresholds:
    """Configurable accuracy and false-acceptance gates for calibration verdicts."""

    approved_min_accuracy: float = DEFAULT_APPROVED_MIN_ACCURACY
    approved_max_false_accept: int = DEFAULT_APPROVED_MAX_FALSE_ACCEPT
    pre_calibrated_min_accuracy: float = DEFAULT_PRE_CALIBRATED_MIN_ACCURACY


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
    resolved_seeds_dir = seeds_dir if seeds_dir is not None else datasets_dir / SEEDS_SUBDIR_NAME
    stage_configs = (
        (StageName.FLUID_PROSE, STAGE_LABEL_FLUID_PROSE),
        (StageName.GAP_FILLER, STAGE_LABEL_GAP_FILLER),
        (StageName.LONG_EXPANDER, STAGE_LABEL_LONG_EXPANDER),
        (StageName.WIDE_EXPANDER, STAGE_LABEL_WIDE_EXPANDER),
    )
    specs: dict[str, StageCalibrationSpec] = {}
    for stage_enum, label in stage_configs:
        stage_key = stage_enum.value
        stage_def = StageRegistry.get(stage_key)
        if stage_def.judge_prompt_key is None:
            raise ValueError(f"Stage '{stage_key}' is missing judge_prompt_key in StageRegistry.")
        specs[stage_key] = StageCalibrationSpec(
            stage_name=stage_key,
            label=label,
            prompt_key=stage_def.judge_prompt_key,
            default_golden_set_path=datasets_dir / f"{stage_key}{GOLDEN_SET_FILE_SUFFIX}",
            default_seed_path=resolved_seeds_dir / f"{stage_key}{SEED_FILE_SUFFIX}",
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


def resolve_model_spec(spec: str, default_provider: str = PROVIDER_GEMINI) -> tuple[str, str]:
    """Parse model specification string into canonical `(provider, model_name)` tuple.

    Args:
        spec: Raw CLI model identifier (optionally prefixed with ``provider:``).
        default_provider: Fallback provider when prefix/inference does not match.

    Returns:
        Canonical ``(provider, model_name)`` tuple.
    """
    cleaned = spec.strip()
    if PROVIDER_MODEL_DELIMITER in cleaned:
        provider, model_name = cleaned.split(PROVIDER_MODEL_DELIMITER, 1)
        return provider.strip().lower(), model_name.strip()
    lower = cleaned.lower()
    if lower.startswith((PROVIDER_GEMINI, MODEL_PREFIX_GEMMA)):
        return PROVIDER_GEMINI, cleaned
    if lower.startswith(PROVIDER_OLLAMA):
        return PROVIDER_OLLAMA, cleaned
    if lower.startswith(PROVIDER_TYPESAFE):
        return PROVIDER_TYPESAFE, cleaned
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
            raw_tokens.extend(
                part.strip() for part in entry.split(SPEC_LIST_DELIMITER) if part.strip()
            )
    if single_stage is not None:
        raw_tokens.extend(
            part.strip() for part in single_stage.split(SPEC_LIST_DELIMITER) if part.strip()
        )

    if not raw_tokens or STAGE_SELECTOR_ALL in [t.lower() for t in raw_tokens]:
        return list(registry.keys())

    resolved: list[str] = []
    for token in raw_tokens:
        norm = STAGE_NAME_UNDERSCORE.join(token.lower().split(STAGE_NAME_HYPHEN))
        if norm not in registry:
            valid = DISPLAY_LIST_SEPARATOR.join(registry.keys())
            raise ValueError(
                f"Unknown stage '{token}'. Valid stages: {valid}, {STAGE_SELECTOR_ALL}."
            )
        if norm not in resolved:
            resolved.append(norm)
    return resolved


def parse_model_specs(
    models: Sequence[str] | None,
    single_model: str | None,
    default_provider: str = PROVIDER_GEMINI,
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
            raw_tokens.extend(
                part.strip() for part in entry.split(SPEC_LIST_DELIMITER) if part.strip()
            )
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
    if clean_model.startswith(f"{provider}{PROVIDER_MODEL_DELIMITER}"):
        clean_model = clean_model[len(provider) + 1 :]
    clean_model = _FILENAME_SANITIZE_PATTERN.sub(_FILENAME_REPLACEMENT_CHAR, clean_model)
    return f"{REPORT_FILENAME_PREFIX}{stage}_{provider}_{clean_model}{REPORT_FILENAME_EXTENSION}"


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
    prompt_payload: dict[str, str] = {_HASH_KEY_SYSTEM_PROMPT: "", _HASH_KEY_USER_PROMPT: ""}
    if prompt_lookup is not None:
        try:
            prompt_payload = prompt_lookup(spec.prompt_key)
        except (KeyError, OSError, ValueError) as exc:
            logger.debug("Prompt lookup unavailable for config hash", error=str(exc))

    canonical = {
        _HASH_KEY_STAGE: spec.stage_name,
        _HASH_KEY_THRESHOLD: round(threshold, CONFIG_HASH_THRESHOLD_PRECISION),
        _HASH_KEY_REQUIRED_CRITERIA: [c.value for c in spec.required_criteria],
        _HASH_KEY_PROMPT: prompt_payload,
        _HASH_KEY_ITEMS: items,
    }
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode(DEFAULT_ENCODING)
    return hashlib.sha256(encoded).hexdigest()
