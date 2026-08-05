#!/usr/bin/env python3
"""Shared helper utilities and path configurations for Cresmo Pipeline scripts."""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Local imports
from helper import read_playlist_urls

# --- Path Configurations ---
ISB_ROOT = Path(__file__).parent.resolve()
DEFAULT_RAW_DIR = ISB_ROOT / "raw"
DEFAULT_ENRICHED_DIR = ISB_ROOT / "enriched"
DEFAULT_CRESMO_DIR = ISB_ROOT / "cresmo"
DEFAULT_CRESMO_WIKI_DIR = DEFAULT_CRESMO_DIR / "wiki"
PROCESSED_CRESMO_LOG = DEFAULT_CRESMO_DIR / "processed_cresmo.json"
BRAIN_DIR = Path("/home/stangler/.gemini/antigravity-ide/brain")

SKILLS_ROOT = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills")
SKILL_EXPANDER_PATH = SKILLS_ROOT / "cresmo-expander" / "SKILL.md"
SKILL_ATOMIC_PATH = SKILLS_ROOT / "cresmo-atomic" / "SKILL.md"
SKILL_MOC_MANAGER_PATH = SKILLS_ROOT / "cresmo-moc-manager" / "SKILL.md"


# --- Idempotency & Log Management ---

def load_processed_cresmo_log(log_path: Path = PROCESSED_CRESMO_LOG) -> set[str]:
    """Load set of completed video_ids from processed_cresmo.json log."""
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    return set(data.keys())
        except Exception as e:
            print(f"[Log Warning] Failed to read {log_path.name}: {e}")
    return set()


def save_processed_cresmo_log(video_id: str, metadata: dict | None = None, log_path: Path = PROCESSED_CRESMO_LOG) -> None:
    """Save processed video_id entry to processed_cresmo.json."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    records = {}
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                if isinstance(raw_data, dict):
                    records = raw_data
                elif isinstance(raw_data, list):
                    records = {vid: {"processed_at": time.strftime("%Y-%m-%d %H:%M:%S")} for vid in raw_data}
        except Exception:
            records = {}

    records[video_id] = {
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "channel_name": metadata.get("channel_name", "") if metadata else "",
        "video_title": metadata.get("video_title", "") if metadata else "",
    }

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


# --- Channel Classification ---

def classify_channel(channel_name: str) -> tuple[str, str]:
    """Classifies source channel deterministically into (domain, category_type)."""
    name_clean = channel_name.lower().strip()

    perennial_tech = {
        "fabio akita", "lucas montano", "mano deyvin",
        "matheus battisti - hora de codar", "chrome for developers",
        "augusto galego", "onde eu clico"
    }
    perennial_ai = {
        "sandeco channel - decomplicated ia", "inteligência mil grau",
        "inteligencia mil grau"
    }
    volatile_politics = {
        "ancapsu", "andré marsiglia", "andre marsiglia", "deltan dallagnol",
        "nando moura", "felipe moura brasil", "renato augusto",
        "jeffrey chiquini", "leandro ruschel", "full texts", "heni ozi cukier"
    }
    volatile_geo = {
        "hoje no mundo militar", "ronnald hawk"
    }
    volatile_finance = {
        "investidor sardinha l raul sena", "investidor sardinha",
        "rafael quintanilha – quantbrasil", "rafael quintanilha - quantbrasil",
        "world revolving"
    }

    if name_clean in perennial_tech:
        return "technology", "perennial"
    elif name_clean in perennial_ai:
        return "ai_data_science", "perennial"
    elif name_clean in volatile_politics:
        return "politics_law", "volatile"
    elif name_clean in volatile_geo:
        return "geopolitics_military", "volatile"
    elif name_clean in volatile_finance:
        return "finance_economics", "volatile"

    return "uncategorized", "volatile"


# --- Agent RPC & Session Management ---

def get_agentapi_binary() -> str:
    """Locate agentapi executable binary."""
    binary_path = "/home/stangler/.gemini/antigravity-ide/bin/agentapi"
    return binary_path if Path(binary_path).exists() else "agentapi"


def get_antigravity_env() -> dict[str, str]:
    """Resolve and validate active IDE gRPC environment credentials."""
    env = os.environ.copy()
    binary_path = get_agentapi_binary()

    ls_addr = env.get("ANTIGRAVITY_LS_ADDRESS")
    csrf_token = env.get("ANTIGRAVITY_CSRF_TOKEN")

    def is_valid_grpc(port: str, token: str) -> bool:
        test_env = env.copy()
        test_env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
        test_env["ANTIGRAVITY_CSRF_TOKEN"] = token
        try:
            res = subprocess.run(
                [binary_path, "get-conversation-metadata", "0e69775c-ba22-4a48-ad18-ba6a318c9a04"],
                capture_output=True,
                text=True,
                timeout=1.5,
                env=test_env,
            )
            out = (res.stdout + "\n" + res.stderr).lower()
            return (
                res.returncode == 0
                and "error reading server preface" not in out
                and "connection reset" not in out
                and "connection refused" not in out
                and "unavailable" not in out
            )
        except Exception:
            return False

    if ls_addr and ":" in ls_addr:
        port = ls_addr.split(":", 1)[1]
        if is_valid_grpc(port, csrf_token or ""):
            return env

    try:
        ps_res = subprocess.run(["ps", "aux"], capture_output=True, text=True, check=False)
        for line in ps_res.stdout.splitlines():
            if "language_server" in line and "--csrf_token" in line:
                pid_m = re.search(r"^\S+\s+(\d+)", line)
                token_m = re.search(r"--csrf_token\s+([a-f0-9\-]+)", line)
                if pid_m and token_m:
                    pid = pid_m.group(1)
                    token = token_m.group(1)
                    ss_res = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True, check=False)
                    for ss_line in ss_res.stdout.splitlines():
                        if f"pid={pid}," in ss_line:
                            port_m = re.search(r"127\.0\.0\.1:(\d+)", ss_line)
                            if port_m:
                                port = port_m.group(1)
                                if is_valid_grpc(port, token):
                                    env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
                                    env["ANTIGRAVITY_CSRF_TOKEN"] = token
                                    return env
    except Exception as e:
        print(f"[Env Warning] LS scan: {e}")

    env["ANTIGRAVITY_LS_ADDRESS"] = "127.0.0.1:41667"
    env["ANTIGRAVITY_CSRF_TOKEN"] = "ff53390d-3617-40f6-836e-6c5375ff5817"
    return env


def resolve_active_session() -> str:
    """Resolve active session ID, auto-detect from brain logs, or allocate a NEW session."""
    env_id = os.getenv("ANTIGRAVITY_CONVERSATION_ID") or os.getenv("ANTIGRAVITY_TRAJECTORY_ID")
    if env_id:
        return env_id

    if BRAIN_DIR.exists():
        recent_logs = sorted(
            BRAIN_DIR.glob("*/.system_generated/logs/transcript.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if recent_logs:
            return recent_logs[0].parent.parent.parent.name

    binary_path = get_agentapi_binary()
    env = get_antigravity_env()
    res = subprocess.run([binary_path, "new-conversation"], capture_output=True, text=True, env=env)
    try:
        data = json.loads(res.stdout)
        new_id = data.get("response", {}).get("conversationId") or data.get("conversationId")
        if new_id:
            return new_id
    except Exception:
        pass

    raise RuntimeError("Failed to resolve or allocate active Antigravity session ID.")


def send_agent_message(prompt: str, session_id: str) -> str:
    """Dispatch RPC payload to target agent session."""
    binary_path = get_agentapi_binary()
    env = get_antigravity_env()
    cmd = [binary_path, "send-message", session_id, prompt]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return res.stdout.strip()
