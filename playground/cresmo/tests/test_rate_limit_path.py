#!/usr/bin/env python3
"""Unit tests verifying YouTube rate-limit log path routing to playground/cresmo directory."""

import json
from pathlib import Path
import sys

CRESMO_DIR = Path(__file__).resolve().parent.parent
ISB_DIR = CRESMO_DIR.parent / "isb.ai"

if str(CRESMO_DIR) not in sys.path:
    sys.path.insert(0, str(CRESMO_DIR))
if str(ISB_DIR) not in sys.path:
    sys.path.insert(0, str(ISB_DIR))

import cresmo_shared
import downloader


def test_default_rate_limit_log_file_location():
    """DEFAULT_RATE_LIMIT_LOG_FILE in cresmo_shared must point directly to playground/cresmo/rate_limit_log.json."""
    assert cresmo_shared.DEFAULT_RATE_LIMIT_LOG_FILE == CRESMO_DIR / "rate_limit_log.json"
    assert cresmo_shared.DEFAULT_RATE_LIMIT_LOG_FILE.exists()


def test_downloader_default_log_file_resolves_to_cresmo():
    """downloader.RATE_LIMIT_LOG_FILE should automatically resolve to cresmo/rate_limit_log.json when cresmo exists."""
    assert downloader.RATE_LIMIT_LOG_FILE == (CRESMO_DIR / "rate_limit_log.json").resolve()


def test_rate_limit_telemetry_writes_to_cresmo(tmp_path):
    """Writing a rate limit event to a target file should correctly record JSON telemetry."""
    custom_cresmo_log = tmp_path / "rate_limit_log.json"
    test_video_id = "test_vid_cresmo_99"

    downloader.log_rate_limit_telemetry(
        video_id=test_video_id,
        streak=1,
        delay_sec=1.5,
        status="SUCCESS",
        total_blocked_sec=0.0,
        log_file=custom_cresmo_log,
    )

    assert custom_cresmo_log.exists()
    with open(custom_cresmo_log, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["video_id"] == test_video_id
    assert data[0]["status"] == "SUCCESS"
