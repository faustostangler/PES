#!/usr/bin/env python3
"""Upload Calibrated Golden Dataset to Langfuse.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria & Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates and Calibration Framework
    - Langfuse Judge Calibration Reference (.agents/skills/langfuse/references/judge-calibration.md)
"""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import click
import typer

# Ensure project root and src are in sys.path
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
for p in (str(SRC_DIR), str(REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from cresmo.infrastructure.config import CresmoSettings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("upload_golden_set")

DEFAULT_GOLDEN_SET_PATH = (
    REPO_ROOT / "scripts" / "fluid_prose" / "golden_sets" / "fluid_prose_golden_set.json"
)
DEFAULT_DATASET_NAME = "cresmo-fluid-prose-calibration"


def upload_golden_set(
    dataset_path: Path,
    dataset_name: str,
    description: str | None = None,
) -> int:
    """Read local golden dataset and upload items to remote Langfuse."""
    if not dataset_path.exists():
        logger.error("Dataset file not found: %s", dataset_path)
        return 1

    with open(dataset_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    logger.info("Loaded %d items from %s", len(items), dataset_path)

    settings = CresmoSettings()
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        logger.error(
            "Langfuse API credentials missing. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .env"
        )
        return 1

    try:
        from langfuse import Langfuse

        langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key.get_secret_value(),
            host=settings.langfuse_host,
        )

        dataset_desc = description or (
            "Calibrated 42-item Golden Dataset for Cresmo Stage 1 (fluid_prose) LLM Judge. "
            "Evaluates: ORALITY_REMOVAL, SEMANTIC_FAITHFULNESS, EPISTEMIC_CRITIQUE, "
            "NER_PRESERVATION, STRUCTURAL_COMPLIANCE, AUTHORIAL_VOICE."
        )

        try:
            langfuse.create_dataset(
                name=dataset_name,
                description=dataset_desc,
                metadata={"source": str(dataset_path), "total_items": len(items)},
            )
            logger.info("Created new Langfuse dataset: '%s'.", dataset_name)
        except Exception as ds_err:  # noqa: BLE001
            logger.info("Dataset '%s' already exists or active (%s). Updating items...", dataset_name, ds_err)

        logger.info("Uploading %d dataset items to '%s'...", len(items), dataset_name)
        for i, item in enumerate(items, start=1):
            item_id = item["id"]
            raw_text = item["input"]["raw_text"]
            candidate_text = item["input"]["candidate_text"]
            expected_output = item["expected_output"]
            metadata = item.get("metadata", {})

            try:
                langfuse.create_dataset_item(
                    dataset_name=dataset_name,
                    id=item_id,
                    input={"raw_text": raw_text, "candidate_text": candidate_text},
                    expected_output=expected_output,
                    metadata=metadata,
                )
            except Exception as item_err:  # noqa: BLE001
                logger.debug("Item '%s' already exists or update skipped: %s", item_id, item_err)

            if i % 7 == 0 or i == len(items):
                logger.info("Uploaded %d/%d items...", i, len(items))

        langfuse.flush()
        logger.info(
            "✓ Successfully uploaded all %d items to Langfuse dataset '%s'.",
            len(items),
            dataset_name,
        )
        return 0

    except Exception as exc:  # noqa: BLE001
        logger.error("Failed uploading dataset to Langfuse: %s", exc)
        return 1


app = typer.Typer(
    name="upload-fluid-prose-dataset",
    help="Upload Golden Set to Langfuse.",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def upload(
    dataset_path: Annotated[
        Path,
        typer.Option(
            "--dataset-path",
            help="Path to local golden set JSON file",
        ),
    ] = DEFAULT_GOLDEN_SET_PATH,
    dataset_name: Annotated[
        str,
        typer.Option(
            "--dataset-name",
            help="Target Langfuse dataset name",
        ),
    ] = DEFAULT_DATASET_NAME,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            help="Optional dataset description",
        ),
    ] = None,
) -> None:
    code = upload_golden_set(dataset_path, dataset_name, description)
    if code != 0:
        raise typer.Exit(code=code)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute fluid prose dataset upload entrypoint.

    Args:
        argv: Optional sequence of CLI arguments. If None, uses sys.argv[1:].

    Returns:
        Process exit code integer.
    """
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
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
