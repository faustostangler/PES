#!/usr/bin/env python3
"""Upload Calibrated Golden Dataset to Langfuse.

Conforms to:
    - ADR-039: Fluid Prose Canonical Judge Criteria & Mechanical Gates
    - SPEC-015: Fluid Prose Quality Gates and Calibration Framework
    - Langfuse Judge Calibration Reference (.agents/skills/langfuse/references/judge-calibration.md)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from cresmo.infrastructure.config import CresmoSettings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("upload_golden_set")

DEFAULT_GOLDEN_SET_PATH = Path("data/golden_sets/fluid_prose_golden_set_42.json")
DEFAULT_DATASET_NAME = "cresmo-fluid-prose-calibration-42"


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

        logger.info("Creating or retrieving Langfuse dataset: '%s'...", dataset_name)
        langfuse.create_dataset(
            name=dataset_name,
            description=dataset_desc,
            metadata={"source": str(dataset_path), "total_items": len(items)},
        )

        logger.info("Uploading %d dataset items to '%s'...", len(items), dataset_name)
        for i, item in enumerate(items, start=1):
            item_id = item["id"]
            raw_text = item["input"]["raw_text"]
            candidate_text = item["input"]["candidate_text"]
            expected_output = item["expected_output"]
            metadata = item.get("metadata", {})

            langfuse.create_dataset_item(
                dataset_name=dataset_name,
                id=item_id,
                input={"raw_text": raw_text, "candidate_text": candidate_text},
                expected_output=expected_output,
                metadata=metadata,
            )
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload Golden Set to Langfuse")
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=DEFAULT_GOLDEN_SET_PATH,
        help="Path to local golden set JSON file",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default=DEFAULT_DATASET_NAME,
        help="Target Langfuse dataset name",
    )
    parser.add_argument(
        "--description",
        type=str,
        default=None,
        help="Optional dataset description",
    )
    args = parser.parse_args()
    return upload_golden_set(args.dataset_path, args.dataset_name, args.description)


if __name__ == "__main__":
    sys.exit(main())
