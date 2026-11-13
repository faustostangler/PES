#!/usr/bin/env python3
"""Unified CLI for uploading Calibrated Golden Datasets to Langfuse.

Replaces stage-split upload scripts with one parameterized runner reading SSOT
JSON datasets from `evals/datasets/`.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle
    - ADR-060: Gap Filler Judge Criteria v2
    - ADR-062: Structural Consolidation, Evals SSOT, and Bootstrap Separation
    - SPEC-062: Structural Consolidation Specification
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import click
import structlog
import typer
from dotenv import load_dotenv

# Ensure `cresmo` resolves cleanly when executed via `python evals/upload_golden_sets.py`
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
for path_entry in (str(SRC_DIR), str(REPO_ROOT)):
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

from cresmo.bootstrap.factories.telemetry_factory import resolve_langfuse_client
from cresmo.infrastructure.config import CresmoSettings

logger = structlog.get_logger("upload_golden_sets")

DATASETS_DIR = REPO_ROOT / "evals" / "datasets"


@dataclass(frozen=True)
class GoldenDatasetSpec:
    """Static metadata describing a stage's canonical Golden Dataset."""

    stage: str
    default_path: Path
    default_name: str
    default_description: str
    metadata: dict[str, Any]


STAGE_DATASET_SPECS: dict[str, GoldenDatasetSpec] = {
    "fluid_prose": GoldenDatasetSpec(
        stage="fluid_prose",
        default_path=DATASETS_DIR / "fluid_prose_golden_set.json",
        default_name="cresmo-fluid-prose-calibration",
        default_description=(
            "Calibrated 42-item Golden Dataset for Cresmo Stage 1 (fluid_prose) LLM Judge. "
            "Evaluates: ORALITY_REMOVAL, SEMANTIC_FAITHFULNESS, EPISTEMIC_CRITIQUE, "
            "NER_PRESERVATION, STRUCTURAL_COMPLIANCE, AUTHORIAL_VOICE."
        ),
        metadata={"stage": "fluid_prose", "criteria_count": 6},
    ),
    "gap_filler": GoldenDatasetSpec(
        stage="gap_filler",
        default_path=DATASETS_DIR / "gap_filler_golden_set.json",
        default_name="cresmo-gap-filler-calibration",
        default_description=(
            "Cresmo Stage 2 (gap_filler) Canonical 49-item Golden Dataset (ADR-060) "
            "for LLM Judge Calibration."
        ),
        metadata={"version": "2.0.0", "stage": "gap_filler", "criteria_count": 7},
    ),
}


def upload_golden_set(
    dataset_path: Path,
    dataset_name: str,
    description: str,
    metadata: dict[str, Any],
    settings: CresmoSettings,
) -> int:
    """Read local golden dataset JSON SSOT and upsert items to Langfuse."""
    if not dataset_path.exists():
        logger.error("Dataset file not found: %s", dataset_path)
        return 1

    raw = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        logger.error("Dataset root must be a JSON array: %s", dataset_path)
        return 1

    items: list[dict[str, Any]] = [item for item in raw if isinstance(item, dict)]
    logger.info("Loaded %d items from %s", len(items), dataset_path)

    if not settings.langfuse_public_key or not settings.langfuse_secret_key.get_secret_value():
        logger.error(
            "Langfuse API credentials missing. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .env"
        )
        return 1

    langfuse = resolve_langfuse_client(settings)
    if langfuse is None:
        logger.error("Langfuse server unreachable at '%s'.", settings.langfuse_host)
        return 1

    try:
        full_metadata = {**metadata, "source": str(dataset_path), "total_items": len(items)}
        try:
            langfuse.create_dataset(
                name=dataset_name,
                description=description,
                metadata=full_metadata,
            )
            logger.info("Ensured Langfuse dataset '%s' exists.", dataset_name)
        except Exception as ds_err:  # noqa: BLE001
            logger.info(
                "Dataset '%s' already active (%s). Proceeding with item upsert...",
                dataset_name,
                ds_err,
            )

        for idx, item in enumerate(items, start=1):
            item_id = item["id"]
            try:
                langfuse.create_dataset_item(
                    dataset_name=dataset_name,
                    id=item_id,
                    input=item["input"],
                    expected_output=item["expected_output"],
                    metadata=item.get("metadata", {}),
                )
            except Exception as item_err:  # noqa: BLE001
                logger.debug("Item '%s' skipped/already present: %s", item_id, item_err)

            if idx % 7 == 0 or idx == len(items):
                logger.info("Uploaded %d/%d items to '%s'...", idx, len(items), dataset_name)

        langfuse.flush()
        logger.info("Successfully uploaded %d items to '%s'.", len(items), dataset_name)
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed uploading dataset '%s' to Langfuse: %s", dataset_name, exc)
        return 1


app = typer.Typer(
    name="upload-golden-sets",
    help="Upload Cresmo JSON SSOT Golden Datasets to Langfuse.",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def upload(
    stage: Annotated[
        str,
        typer.Option(
            "--stage",
            help="Stage dataset preset to upload: fluid_prose, gap_filler, or all.",
        ),
    ] = "all",
    dataset_path: Annotated[
        Path | None,
        typer.Option(
            "--dataset-path",
            help="Override JSON dataset path (only valid for single stage).",
        ),
    ] = None,
    dataset_name: Annotated[
        str | None,
        typer.Option(
            "--dataset-name",
            help="Override target Langfuse dataset name (only valid for single stage).",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            help="Override Langfuse dataset description (only valid for single stage).",
        ),
    ] = None,
) -> None:
    """Upload one or all canonical Golden Datasets from `evals/datasets/` to Langfuse."""
    load_dotenv(REPO_ROOT / ".env", override=False)
    settings = CresmoSettings()

    normalized = stage.strip().lower().replace("-", "_")
    if normalized == "all":
        if any(opt is not None for opt in (dataset_path, dataset_name, description)):
            raise typer.BadParameter(
                "--dataset-path, --dataset-name, and --description require a single --stage."
            )
        targets = list(STAGE_DATASET_SPECS.values())
    elif normalized in STAGE_DATASET_SPECS:
        targets = [STAGE_DATASET_SPECS[normalized]]
    else:
        valid = ", ".join((*STAGE_DATASET_SPECS.keys(), "all"))
        raise typer.BadParameter(f"Unknown stage '{stage}'. Valid stages: {valid}.")

    for spec in targets:
        code = upload_golden_set(
            dataset_path=dataset_path or spec.default_path,
            dataset_name=dataset_name or spec.default_name,
            description=description or spec.default_description,
            metadata=spec.metadata,
            settings=settings,
        )
        if code != 0:
            raise typer.Exit(code=code)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint returning explicit exit code without standalone process exit."""
    try:
        res = app(args=list(argv) if argv is not None else None, standalone_mode=False)
        return 0 if res is None else int(res)
    except typer.Exit as exc:
        return exc.exit_code
    except click.ClickException as exc:
        sys.stderr.write(f"Usage error: {exc}\n")
        return getattr(exc, "exit_code", 2)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2


if __name__ == "__main__":
    raise SystemExit(main())
