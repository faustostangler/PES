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


def test_stage2_sentinel_omitted_on_subsequent_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verify Stage 2 prepends SENTINEL_PREFIX on Pass 1 only and omits it on pass > 1."""
    import cresmo_pipeline

    dummy_raw = tmp_path / "test_raw.txt"
    dummy_raw.write_text("Test transcript content Ground Truth", encoding="utf-8")
    output_dir = tmp_path / "enriched"

    prompts_sent: list[str] = []
    clear_calls: list[str] = []

    def mock_clear_session(session_id, restart_server=False):
        clear_calls.append(session_id)
        return True

    def mock_send_agent_message(prompt, session_id):
        prompts_sent.append(prompt)
        # Simulate agent immediately producing valid output markdown
        channel_dir = output_dir / "ANCAPSU"
        channel_dir.mkdir(parents=True, exist_ok=True)
        enriched_target = channel_dir / "test_raw.md"
        enriched_target.write_text("## Resumo Abrangente\n" + "x" * 600 + "\n## Informações Complementares\nComp info", encoding="utf-8")

    monkeypatch.setattr(cresmo_pipeline, "clear_session_history", mock_clear_session)
    monkeypatch.setattr(cresmo_pipeline, "send_agent_message", mock_send_agent_message)

    cresmo_pipeline.execute_stage2_expander(
        txt_file=dummy_raw,
        meta={"channel_name": "ANCAPSU", "video_id": "test_raw"},
        session_id="test-session-multi-pass",
        output_dir=output_dir,
        total_passes=2,
        force=True,
        isolate_context=True,
    )

    assert len(prompts_sent) == 2, f"Expected 2 passes, got {len(prompts_sent)}"
    # Pass 1 must include SENTINEL_PREFIX and clear history
    assert prompts_sent[0].startswith(SENTINEL_PREFIX)
    assert len(clear_calls) == 1

    # Pass 2 must NOT include SENTINEL_PREFIX and NOT trigger clear_session_history
    assert SENTINEL_PREFIX not in prompts_sent[1]

