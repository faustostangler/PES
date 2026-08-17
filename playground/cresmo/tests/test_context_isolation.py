"""Unit tests for Cresmo context isolation and session history purge utilities."""

import json
import sys
from pathlib import Path
import pytest

# Ensure playground/cresmo is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from cresmo_shared import (
    SENTINEL_PREFIX,
    clear_session_history,
)


def test_sentinel_prefix_content():
    """Verify SENTINEL_PREFIX contains required context reset instructions."""
    assert "CRITICAL CONTEXT RESET" in SENTINEL_PREFIX
    assert "Ignore ALL previous conversation history" in SENTINEL_PREFIX


def test_clear_session_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify clear_session_history truncates transcript.jsonl and removes message files."""
    session_id = "test-session-12345"
    mock_brain_dir = tmp_path / "brain"
    session_dir = mock_brain_dir / session_id
    logs_dir = session_dir / ".system_generated" / "logs"
    messages_dir = session_dir / ".system_generated" / "messages"

    logs_dir.mkdir(parents=True, exist_ok=True)
    messages_dir.mkdir(parents=True, exist_ok=True)

    transcript_file = logs_dir / "transcript.jsonl"
    transcript_file.write_text('{"source": "USER", "content": "hello"}\n{"source": "MODEL", "content": "world"}\n', encoding="utf-8")

    msg1 = messages_dir / "0001.json"
    msg2 = messages_dir / "0002.json"
    msg1.write_text(json.dumps({"msg": 1}), encoding="utf-8")
    msg2.write_text(json.dumps({"msg": 2}), encoding="utf-8")

    assert transcript_file.stat().st_size > 0
    assert len(list(messages_dir.glob("*.json"))) == 2

    result = clear_session_history(session_id, restart_server=False, brain_dir=mock_brain_dir)
    assert result is True

    # Check transcript is truncated to 0 bytes
    assert transcript_file.exists()
    assert transcript_file.read_text(encoding="utf-8") == ""

    # Check message json files are purged
    assert len(list(messages_dir.glob("*.json"))) == 0


def test_clear_session_history_non_existent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify clear_session_history handles non-existent directories gracefully without error."""
    import cresmo_shared
    monkeypatch.setattr(cresmo_shared, "BRAIN_DIR", tmp_path / "non_existent_brain")
    result = clear_session_history("missing-session", restart_server=False)
    assert result is False
