#!/usr/bin/env python3
"""Upload Calibrated Gap Filler Golden Dataset to Langfuse.

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - SPEC-015: Quality Gates and Calibration Framework
    - Langfuse Judge Calibration Reference (.agents/skills/langfuse/references/judge-calibration.md)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure project root and src are in sys.path
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
for p in (str(SRC_DIR), str(REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from cresmo.infrastructure.config import CresmoSettings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("upload_gap_filler_golden_set")

DEFAULT_GOLDEN_SET_PATH = (
    REPO_ROOT / "scripts" / "gap_filler" / "golden_sets" / "gap_filler_golden_set.json"
)
DEFAULT_DATASET_NAME = "cresmo-gap-filler-calibration"


def upload_golden_set(
    dataset_path: Path,
    dataset_name: str,
    description: str | None = None,
) -> int:
    """Read local golden dataset and upload items to remote Langfuse."""
    if not dataset_path.exists():
        logger.error("Dataset file not found: %s", dataset_path)
        return 1

    with open(dataset_path, encoding="utf-8") as f:
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

        dataset_desc = (
            description
            or "Cresmo Stage 2 (gap_filler) Canonical 35-item Golden Dataset for LLM Judge Calibration."
        )

        # Ensure dataset container exists
        langfuse.create_dataset(
            name=dataset_name,
            description=dataset_desc,
            metadata={
                "version": "1.0.0",
                "stage": "gap_filler",
                "total_items": len(items),
                "criteria_count": 5,
            },
        )
        logger.info(
            "Ensured Langfuse dataset '%s' exists at %s",
            dataset_name,
            settings.langfuse_host,
        )

        uploaded = 0
        for item in items:
            item_id = item["id"]
            input_payload = item["input"]
            expected_output = item["expected_output"]
            metadata = item.get("metadata", {})

            langfuse.create_dataset_item(
                dataset_name=dataset_name,
                input=input_payload,
                expected_output=expected_output,
                metadata=metadata,
                id=item_id,
            )
            uploaded += 1

        langfuse.flush()
        logger.info("Successfully uploaded %d items to dataset '%s'.", uploaded, dataset_name)
        return 0

    except Exception:
        logger.exception("Failed to upload dataset to Langfuse.")
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload Cresmo gap_filler Golden Dataset to Langfuse."
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_GOLDEN_SET_PATH,
        help=f"Path to golden dataset JSON (default: {DEFAULT_GOLDEN_SET_PATH})",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=DEFAULT_DATASET_NAME,
        help=f"Dataset name in Langfuse (default: {DEFAULT_DATASET_NAME})",
    )
    parser.add_argument(
        "--description",
        type=str,
        default=None,
        help="Optional custom dataset description.",
    )

    args = parser.parse_args()
    sys.exit(upload_golden_set(args.path, args.name, args.description))


if __name__ == "__main__":
    main()
