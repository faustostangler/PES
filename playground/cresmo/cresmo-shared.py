#!/usr/bin/env python3
"""Shared helper utilities and path configurations for Cresmo Pipeline scripts."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

# --- Path Configurations ---
CRESMO_ROOT: Path = Path(__file__).parent.resolve()
DEFAULT_RAW_DIR: Path = CRESMO_ROOT / "raw"
DEFAULT_ENRICHED_DIR: Path = CRESMO_ROOT / "enriched"
DEFAULT_CRESMO_DIR: Path = CRESMO_ROOT
DEFAULT_CRESMO_WIKI_DIR: Path = CRESMO_ROOT / "wiki"
PROCESSED_CRESMO_LOG: Path = CRESMO_ROOT / "processed_cresmo.json"
DEFAULT_PLAYLIST_FILE: Path = CRESMO_ROOT / "playlist.txt"
DEFAULT_BRAIN_CSV: Path = CRESMO_ROOT / "brain.csv"
DEFAULT_COOKIES_FILE: Path = CRESMO_ROOT / ".yt_dlp_cookies.txt"

BRAIN_DIR: Path = Path(os.environ.get("ANTIGRAVITY_BRAIN_DIR", Path.home() / ".gemini" / "antigravity-ide" / "brain"))

_WORKSPACE_ROOT = CRESMO_ROOT.parent.parent
_CANDIDATE_SKILLS_DIRS = [
    _WORKSPACE_ROOT / ".agents" / "skills",
    Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills"),
    Path("/mnt/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills"),
]
SKILLS_ROOT: Path = next((p for p in _CANDIDATE_SKILLS_DIRS if p.exists()), _WORKSPACE_ROOT / ".agents" / "skills")

SKILL_EXPANDER_PATH: Path = SKILLS_ROOT / "cresmo-expander" / "SKILL.md"
SKILL_ATOMIC_PATH: Path = SKILLS_ROOT / "cresmo-atomic" / "SKILL.md"
SKILL_MOC_MANAGER_PATH: Path = SKILLS_ROOT / "cresmo-moc-manager" / "SKILL.md"

# --- Agent RPC & gRPC Defaults ---
DEFAULT_AGENTAPI_BINARY: Path = Path(os.environ.get(
    "ANTIGRAVITY_AGENTAPI_BINARY",
    Path.home() / ".gemini" / "antigravity-ide" / "bin" / "agentapi"
))
FALLBACK_TEST_CONVERSATION_ID: str = "0e69775c-ba22-4a48-ad18-ba6a318c9a04"
DEFAULT_LS_ADDRESS: str = "127.0.0.1:41667"
DEFAULT_CSRF_TOKEN: str = "ff53390d-3617-40f6-836e-6c5375ff5817"
GRPC_TEST_TIMEOUT_SECONDS: float = 1.5

# --- Formats & Protocols ---
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
VIDEO_DESCRIPTION_KEY: str = "video_description"
SENTINEL_PREFIX: str = (
    "CRITICAL CONTEXT RESET: Ignore ALL previous conversation history. "
    "This is a completely new, independent task. Do NOT reference any "
    "previously processed files or outputs. Treat this as your very "
    "first message in a fresh session.\n\n"
)

# --- Channel Classification Categories ---
PERENNIAL_TECH_CHANNELS: frozenset[str] = frozenset({
    "fabio akita",
    "lucas montano",
    "mano deyvin",
    "matheus battisti - hora de codar",
    "chrome for developers",
    "augusto galego",
    "onde eu clico",
})
PERENNIAL_AI_CHANNELS: frozenset[str] = frozenset({
    "sandeco channel - decomplicated ia",
    "inteligência mil grau",
    "inteligencia mil grau",
})
VOLATILE_POLITICS_CHANNELS: frozenset[str] = frozenset({
    "ancapsu",
    "andré marsiglia",
    "andre marsiglia",
    "deltan dallagnol",
    "nando moura",
    "felipe moura brasil",
    "renato augusto",
    "jeffrey chiquini",
    "leandro ruschel",
    "full texts",
    "heni ozi cukier",
})
VOLATILE_GEO_CHANNELS: frozenset[str] = frozenset({
    "hoje no mundo militar",
    "ronnald hawk",
})
VOLATILE_FINANCE_CHANNELS: frozenset[str] = frozenset({
    "investidor sardinha l raul sena",
    "investidor sardinha",
    "rafael quintanilha – quantbrasil",
    "rafael quintanilha - quantbrasil",
    "world revolving",
})
DEFAULT_CHANNEL_DOMAIN: str = "uncategorized"
DEFAULT_CHANNEL_CATEGORY: str = "volatile"

# --- Compiled Regexes ---
TRANSCRIPTION_SPLIT_REGEX: re.Pattern[str] = re.compile(r"^---$", flags=re.MULTILINE)
PID_REGEX: re.Pattern[str] = re.compile(r"^\S+\s+(\d+)")
TOKEN_REGEX: re.Pattern[str] = re.compile(r"--csrf_token\s+([a-f0-9\-]+)")
PORT_REGEX: re.Pattern[str] = re.compile(r"127\.0\.0\.1:(\d+)")


# --- File & Data Helpers ---

def read_playlist_urls(file_path: Path) -> list[str]:
    """Read seed video URLs from a text file, skipping comments and blank lines."""
    urls = []
    if file_path.exists():
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                if "#" in line:
                    continue
                line = line.strip()
                if line:
                    urls.append(line)
    return urls


def parse_merged_transcriptions(file_path: Path) -> list[dict]:
    """Parse a file containing multiple transcription blocks separated by --- blocks.

    Each block contains a dictionary of metadata and the corresponding text.
    """
    metadata_list = []
    if not file_path.exists():
        return metadata_list
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parts = TRANSCRIPTION_SPLIT_REGEX.split(content)

        i = 1
        while i < len(parts):
            yaml_text = parts[i]
            text_content = parts[i + 1].strip() if i + 1 < len(parts) else ""

            meta = {}
            lines = yaml_text.splitlines()
            in_desc = False
            desc_lines = []

            for line in lines:
                if in_desc:
                    if line.startswith("  ") or line.strip() == "":
                        desc_lines.append(line[2:] if line.startswith("  ") else line)
                    else:
                        in_desc = False

                if in_desc:
                    continue
                if ":" not in line:
                    continue
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if key == VIDEO_DESCRIPTION_KEY:
                    in_desc = True
                    continue
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                meta[key] = val

            if desc_lines:
                meta[VIDEO_DESCRIPTION_KEY] = "\n".join(desc_lines)

            metadata_list.append({
                "metadata": meta,
                "text": text_content,
            })
            i += 2
    except Exception as e:
        print(f"Error parsing merged transcriptions in {file_path.name}: {e}")
    return metadata_list


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


def save_processed_cresmo_log(
    video_id: str,
    metadata: dict | None = None,
    log_path: Path = PROCESSED_CRESMO_LOG,
) -> None:
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
                    records = {vid: {"processed_at": time.strftime(DATETIME_FORMAT)} for vid in raw_data}
        except Exception:
            records = {}

    records[video_id] = {
        "processed_at": time.strftime(DATETIME_FORMAT),
        "channel_name": metadata.get("channel_name", "") if metadata else "",
        "video_title": metadata.get("video_title", "") if metadata else "",
    }

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


# --- Channel Classification ---

def classify_channel(channel_name: str) -> tuple[str, str]:
    """Classifies source channel deterministically into (domain, category_type)."""
    name_clean = channel_name.lower().strip()

    if name_clean in PERENNIAL_TECH_CHANNELS:
        return "technology", "perennial"
    elif name_clean in PERENNIAL_AI_CHANNELS:
        return "ai_data_science", "perennial"
    elif name_clean in VOLATILE_POLITICS_CHANNELS:
        return "politics_law", "volatile"
    elif name_clean in VOLATILE_GEO_CHANNELS:
        return "geopolitics_military", "volatile"
    elif name_clean in VOLATILE_FINANCE_CHANNELS:
        return "finance_economics", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


# --- Agent RPC & Session Management ---

def get_agentapi_binary() -> str:
    """Locate agentapi executable binary."""
    return str(DEFAULT_AGENTAPI_BINARY) if DEFAULT_AGENTAPI_BINARY.exists() else "agentapi"


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
                [binary_path, "get-conversation-metadata", FALLBACK_TEST_CONVERSATION_ID],
                capture_output=True,
                text=True,
                timeout=GRPC_TEST_TIMEOUT_SECONDS,
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
                pid_m = PID_REGEX.search(line)
                token_m = TOKEN_REGEX.search(line)
                if pid_m and token_m:
                    pid = pid_m.group(1)
                    token = token_m.group(1)
                    ss_res = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True, check=False)
                    for ss_line in ss_res.stdout.splitlines():
                        if f"pid={pid}," in ss_line:
                            port_m = PORT_REGEX.search(ss_line)
                            if port_m:
                                port = port_m.group(1)
                                if is_valid_grpc(port, token):
                                    env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
                                    env["ANTIGRAVITY_CSRF_TOKEN"] = token
                                    return env
    except Exception as e:
        print(f"[Env Warning] LS scan: {e}")

    env["ANTIGRAVITY_LS_ADDRESS"] = DEFAULT_LS_ADDRESS
    env["ANTIGRAVITY_CSRF_TOKEN"] = DEFAULT_CSRF_TOKEN
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


def clear_session_history(session_id: str, restart_server: bool = False, brain_dir: Path | None = None) -> bool:
    """Purge active agent session history (transcript.jsonl and message files) to isolate context.

    Args:
        session_id: Target agent conversation identifier.
        restart_server: If True, terminates the active Language Server process to force fresh context reload.
        brain_dir: Optional custom path to brain root directory (defaults to BRAIN_DIR).

    Returns:
        bool: True if session directory was located and purged, False otherwise.
    """
    target_brain_dir = brain_dir if brain_dir is not None else BRAIN_DIR
    session_dir = target_brain_dir / session_id
    if not session_dir.exists():
        return False

    purged = False
    # 1. Truncate transcript logs
    for log_filename in ("transcript.jsonl", "transcript_full.jsonl"):
        jsonl_path = session_dir / ".system_generated" / "logs" / log_filename
        if jsonl_path.exists():
            try:
                jsonl_path.write_text("", encoding="utf-8")
                purged = True
            except Exception as e:
                print(f"[Context Purge Warning] Failed to truncate {jsonl_path.name}: {e}")

    # 2. Delete message files
    messages_dir = session_dir / ".system_generated" / "messages"
    if messages_dir.exists():
        for msg_file in messages_dir.glob("*.json"):
            try:
                msg_file.unlink(missing_ok=True)
                purged = True
            except Exception:
                pass

    return purged or session_dir.exists()
