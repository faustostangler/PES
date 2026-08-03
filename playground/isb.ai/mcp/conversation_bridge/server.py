#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["fastmcp>=2.0"]
# ///
"""Conversation Bridge MCP Server.

Cross-conversation job dispatch and result retrieval for ISB.AI
detranscription pipeline. Eliminates the transcript.jsonl dependency
by using artifact files as the sole communication channel.

Architecture:
    - dispatch_detranscription: CLI → agentapi new-conversation → agent writes file
    - get_job_result: Any conversation → checks artifact file on disk
    - list_jobs: Status dashboard for all tracked jobs

Why MCP and not direct file polling?
    MCP tools are shared infrastructure across ALL Antigravity conversations.
    Any conversation can dispatch work AND retrieve results from jobs dispatched
    by any other conversation — without parsing internal log files.
"""

import json
import os
import re
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastmcp import FastMCP

mcp = FastMCP("conversation-bridge")

# --- Configuration (12-Factor: externalize via env vars) ---
AGENTAPI_BINARY = os.environ.get(
    "AGENTAPI_BINARY",
    "/home/stangler/.gemini/antigravity-ide/bin/agentapi",
)
JOBS_DIR = Path(
    os.environ.get("JOBS_DIR", str(Path(__file__).parent / "jobs"))
)
DEFAULT_SKILL_PATH = Path(
    os.environ.get(
        "DEFAULT_SKILL_PATH",
        "/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES"
        "/.agents/skills/writer-detranscriptor/SKILL.md",
    )
)

JOBS_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────
# Infrastructure: gRPC Environment Discovery (Adapter)
# ──────────────────────────────────────────────────────────────────────


def _resolve_agentapi_binary() -> str:
    """Locate the agentapi executable, falling back to PATH."""
    return AGENTAPI_BINARY if Path(AGENTAPI_BINARY).exists() else "agentapi"


def _test_grpc_connection(env: dict, port: str, token: str) -> bool:
    """Validate gRPC Language Server connectivity on a specific port."""
    binary = _resolve_agentapi_binary()
    test_env = env.copy()
    test_env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
    test_env["ANTIGRAVITY_CSRF_TOKEN"] = token
    try:
        res = subprocess.run(
            [binary, "get-conversation-metadata", "00000000-0000-0000-0000-000000000000"],
            capture_output=True,
            text=True,
            timeout=2,
            env=test_env,
        )
        out = (res.stdout + "\n" + res.stderr).lower()
        invalid_signals = (
            "connection refused",
            "connection reset",
            "unavailable",
            "error reading server preface",
        )
        return res.returncode == 0 and not any(s in out for s in invalid_signals)
    except Exception:
        return False


def _get_grpc_env() -> dict[str, str]:
    """Resolve and validate active IDE gRPC environment credentials.

    Strategy:
      1. Check ANTIGRAVITY_LS_ADDRESS / ANTIGRAVITY_CSRF_TOKEN env vars
      2. Process scan fallback: find language_server PID → resolve port via ss
    """
    env = os.environ.copy()

    # Strategy 1: existing env vars
    ls_addr = env.get("ANTIGRAVITY_LS_ADDRESS", "")
    csrf = env.get("ANTIGRAVITY_CSRF_TOKEN", "")
    if ":" in ls_addr:
        port = ls_addr.split(":", 1)[1]
        if _test_grpc_connection(env, port, csrf):
            return env

    # Strategy 2: process scan
    try:
        ps_out = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True, check=False
        ).stdout
        for line in ps_out.splitlines():
            if "language_server" not in line or "--csrf_token" not in line:
                continue
            pid_m = re.search(r"^\S+\s+(\d+)", line)
            token_m = re.search(r"--csrf_token\s+([a-f0-9\-]+)", line)
            if not (pid_m and token_m):
                continue
            pid, token = pid_m.group(1), token_m.group(1)
            ss_out = subprocess.run(
                ["ss", "-tulpn"], capture_output=True, text=True, check=False
            ).stdout
            for ss_line in ss_out.splitlines():
                if f"pid={pid}," not in ss_line:
                    continue
                port_m = re.search(r"127\.0\.0\.1:(\d+)", ss_line)
                if port_m and _test_grpc_connection(env, port_m.group(1), token):
                    env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port_m.group(1)}"
                    env["ANTIGRAVITY_CSRF_TOKEN"] = token
                    return env
    except Exception:
        pass

    return env


# ──────────────────────────────────────────────────────────────────────
# Job State Management (Repository pattern — filesystem adapter)
# ──────────────────────────────────────────────────────────────────────


def _load_job(job_id: str) -> dict | None:
    """Load a job record from the filesystem."""
    job_file = JOBS_DIR / f"{job_id}.json"
    if job_file.exists():
        return json.loads(job_file.read_text(encoding="utf-8"))
    return None


def _save_job(job: dict) -> None:
    """Persist a job record to the filesystem."""
    job_file = JOBS_DIR / f"{job['job_id']}.json"
    job_file.write_text(
        json.dumps(job, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _check_artifact_completion(job: dict) -> bool:
    """Check if the agent has written the output artifact file.

    This is the ONLY mechanism for result detection — no transcript.jsonl.
    Validates that the file was written AFTER dispatch and has substantial content.
    """
    output_file = Path(job["output_path"])
    if not output_file.exists():
        return False

    dispatch_time = datetime.fromisoformat(job["dispatched_at"]).timestamp()
    file_mtime = output_file.stat().st_mtime
    file_size = output_file.stat().st_size

    # File must be newer than dispatch time and contain meaningful content
    return file_mtime >= (dispatch_time - 2.0) and file_size > 200


# ──────────────────────────────────────────────────────────────────────
# MCP Tools (Application Service Layer)
# ──────────────────────────────────────────────────────────────────────


@mcp.tool()
def dispatch_detranscription(
    transcript_path: str,
    output_path: str,
    skill_path: str = "",
    model: str = "",
) -> dict:
    """Dispatch a detranscription job to a NEW Antigravity agent conversation.

    Sends the transcript content with the Writer Detranscriptor skill to a
    freshly allocated agent conversation via agentapi. The agent processes
    the transcript and writes the result directly to output_path on disk.

    After dispatching, use get_job_result() to check completion status and
    retrieve the content — from ANY conversation.

    Args:
        transcript_path: Absolute path to the raw .txt transcript file.
        output_path: Absolute path where the agent should write the .md result.
        skill_path: Path to the skill SKILL.md file. Uses default if empty.
        model: Model selection (flash_lite, flash, pro). Uses IDE default if empty.

    Returns:
        Dict with job_id, status, conversation_id, output_path.
    """
    transcript_file = Path(transcript_path)
    output_file = Path(output_path)
    skill_file = Path(skill_path) if skill_path else DEFAULT_SKILL_PATH

    if not transcript_file.exists():
        return {"error": f"Transcript file not found: {transcript_path}"}

    # Read inputs
    transcript_text = transcript_file.read_text(encoding="utf-8").strip()
    if not transcript_text:
        return {"error": f"Transcript file is empty: {transcript_path}"}

    skill_context = ""
    if skill_file.exists():
        skill_context = skill_file.read_text(encoding="utf-8").strip()

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Remove stale output to prevent false-positive timestamp matches
    if output_file.exists():
        output_file.unlink()

    # Build prompt — instructs agent to write file (Option A is the ONLY option now)
    prompt = (
        "You are Writer Detranscriptor. Transform raw audio transcript into "
        "clean, structured Markdown inside <config_file> tags.\n"
        f"CRITICAL: Save output directly to file: {output_file}\n\n"
        f"--- SKILL SPECIFICATION ---\n{skill_context}\n\n"
        f"--- TRANSCRIPT ---\nFile: {transcript_file.name}\n{transcript_text}"
    )

    # Create job record before dispatch
    job_id = str(uuid4())[:8]
    job = {
        "job_id": job_id,
        "status": "dispatching",
        "transcript_path": str(transcript_file),
        "output_path": str(output_file),
        "conversation_id": None,
        "dispatched_at": datetime.now(UTC).isoformat(),
        "completed_at": None,
        "error": None,
    }
    _save_job(job)

    # Dispatch via agentapi
    env = _get_grpc_env()
    binary = _resolve_agentapi_binary()

    cmd = [binary, "new-conversation"]
    if model:
        cmd.append(f"--model={model}")
    cmd.append(prompt)

    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15, env=env
        )
        response_data = json.loads(res.stdout)

        conv_id = response_data.get("response", {}).get(
            "conversationId"
        ) or response_data.get("conversationId")

        job["status"] = "running"
        job["conversation_id"] = conv_id
        _save_job(job)

        return {
            "job_id": job_id,
            "status": "running",
            "conversation_id": conv_id,
            "output_path": str(output_file),
            "message": (
                f"Job dispatched to conversation {conv_id}. "
                f"Check result with get_job_result('{job_id}')"
            ),
        }
    except subprocess.TimeoutExpired:
        job["status"] = "error"
        job["error"] = "agentapi command timed out after 15s"
        _save_job(job)
        return {"job_id": job_id, "status": "error", "error": job["error"]}
    except json.JSONDecodeError as e:
        job["status"] = "error"
        job["error"] = f"Invalid agentapi response: {e}"
        _save_job(job)
        return {"job_id": job_id, "status": "error", "error": job["error"]}
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        _save_job(job)
        return {"job_id": job_id, "status": "error", "error": job["error"]}


@mcp.tool()
def get_job_result(job_id: str, wait_seconds: int = 0) -> dict:
    """Check the status and retrieve the result of a dispatched detranscription job.

    Checks whether the agent has written the output artifact file to disk.
    Does NOT read transcript.jsonl — relies entirely on the file produced by
    the agent's file-writing capability.

    Can be called from ANY conversation — this is the cross-conversation bridge.

    Args:
        job_id: The job ID returned by dispatch_detranscription.
        wait_seconds: Seconds to poll before returning (0 = instant check, max 120).

    Returns:
        Dict with status, content (if done), output_path, and timing metadata.
    """
    job = _load_job(job_id)
    if not job:
        return {"error": f"Job not found: {job_id}"}

    output_file = Path(job["output_path"])
    dispatch_ts = datetime.fromisoformat(job["dispatched_at"]).timestamp()
    max_wait = min(max(wait_seconds, 0), 120)
    start = time.time()

    while True:
        if _check_artifact_completion(job):
            content = output_file.read_text(encoding="utf-8").strip()
            job["status"] = "done"
            job["completed_at"] = datetime.now(UTC).isoformat()
            _save_job(job)

            return {
                "job_id": job_id,
                "status": "done",
                "output_path": str(output_file),
                "content_length": len(content),
                "content_preview": content[:500] + ("..." if len(content) > 500 else ""),
                "content": content,
                "elapsed_seconds": round(time.time() - dispatch_ts, 1),
            }

        if time.time() - start >= max_wait:
            break
        time.sleep(2)

    elapsed = time.time() - dispatch_ts
    return {
        "job_id": job_id,
        "status": job["status"],
        "output_path": str(output_file),
        "output_exists": output_file.exists(),
        "output_size": output_file.stat().st_size if output_file.exists() else 0,
        "elapsed_seconds": round(elapsed, 1),
        "conversation_id": job.get("conversation_id"),
        "message": (
            f"Result not ready yet ({elapsed:.0f}s elapsed). "
            f"Try again or use wait_seconds parameter."
        ),
    }


@mcp.tool()
def list_jobs(status_filter: str = "", limit: int = 20) -> dict:
    """List all tracked detranscription jobs and their current statuses.

    Performs live status reconciliation: if a job is marked 'running' but
    the output file has appeared, it transitions to 'done'.

    Args:
        status_filter: Filter by status (dispatching, running, done, error).
                       Empty string returns all jobs.
        limit: Maximum number of jobs to return (newest first). Default 20.

    Returns:
        Dict with total count and list of job summaries.
    """
    jobs = []
    job_files = sorted(
        JOBS_DIR.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for job_file in job_files[:limit * 2]:  # Read extra to account for filtering
        try:
            job = json.loads(job_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        # Live status reconciliation
        if job.get("status") == "running" and _check_artifact_completion(job):
            job["status"] = "done"
            job["completed_at"] = datetime.now(UTC).isoformat()
            _save_job(job)

        if status_filter and job.get("status") != status_filter:
            continue

        jobs.append(
            {
                "job_id": job["job_id"],
                "status": job["status"],
                "transcript": Path(job["transcript_path"]).name,
                "output": Path(job["output_path"]).name,
                "dispatched_at": job.get("dispatched_at"),
                "completed_at": job.get("completed_at"),
                "conversation_id": job.get("conversation_id"),
                "error": job.get("error"),
            }
        )

        if len(jobs) >= limit:
            break

    return {"total": len(jobs), "jobs": jobs}


if __name__ == "__main__":
    mcp.run()
