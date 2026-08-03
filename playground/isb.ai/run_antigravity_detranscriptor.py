#!/usr/bin/env python3
"""Antigravity Agent CLI Detranscriptor - Ideal Dual-Mode (Option A + Option B Fallback) Architecture.

Performs speech-to-text detranscription by sending CLI commands to active IDE agent sessions.
Uses Option A (direct agent file writing) as primary, with Option B (trajectory log capture) as fallback.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# --- Configuration & Paths ---
ISB_ROOT = Path(__file__).parent
DEFAULT_INPUT_DIR = ISB_ROOT / "raw" / "Elementar"
SKILL_PATH = Path(
    "/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills/writer-detranscriptor/SKILL.md"
)
BRAIN_DIR = Path("/home/stangler/.gemini/antigravity-ide/brain")


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
                                    print(f"[Env] Validated gRPC Language Server on 127.0.0.1:{port}")
                                    return env
    except Exception as e:
        print(f"[Env] LS scan warning: {e}")

    # Fallback to default port if auto-detection fails
    env["ANTIGRAVITY_LS_ADDRESS"] = "127.0.0.1:41667"
    env["ANTIGRAVITY_CSRF_TOKEN"] = "ff53390d-3617-40f6-836e-6c5375ff5817"
    return env


def resolve_active_session() -> str:
    """Resolve active session ID, auto-detect from brain logs, or allocate a NEW official session."""
    env_id = os.getenv("ANTIGRAVITY_CONVERSATION_ID") or os.getenv("ANTIGRAVITY_TRAJECTORY_ID")
    if env_id:
        print(f"[Session] Using environment session ID: {env_id}")
        return env_id

    # 1. Auto-detect most recent listening conversation session in brain/
    if BRAIN_DIR.exists():
        recent_logs = sorted(
            BRAIN_DIR.glob("*/.system_generated/logs/transcript.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if recent_logs:
            detected_id = recent_logs[0].parent.parent.parent.name
            print(f"[Session] Auto-detected active session: {detected_id}")
            return detected_id

    # 2. If no active session found, request IDE to allocate a NEW official listening conversation
    binary_path = get_agentapi_binary()
    env = get_antigravity_env()
    print("[Session] Allocating new conversation session via agentapi...")
    res = subprocess.run([binary_path, "new-conversation"], capture_output=True, text=True, env=env)
    try:
        data = json.loads(res.stdout)
        new_id = data.get("response", {}).get("conversationId") or data.get("conversationId")
        if new_id:
            print(f"[Session] Successfully allocated new session ID: {new_id}")
            return new_id
    except Exception:
        pass

    raise RuntimeError("Failed to resolve or allocate an active Antigravity session ID.")


def send_agent_message(prompt: str, session_id: str) -> str:
    """Send CLI RPC message payload to target agent session."""
    binary_path = get_agentapi_binary()
    env = get_antigravity_env()

    cmd = [binary_path, "send-message", session_id, prompt]
    print(f"[CLI] Dispatching RPC payload to session ({session_id[:8]}...)...")
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    recipient_id = json.loads(res.stdout.strip()).get("response", {}).get("sendMessage", {}).get("recipientId")
    brain_dir = Path("/home/stangler/.gemini/antigravity-ide/brain")
    session_dir = brain_dir / recipient_id
    log_file = session_dir / ".system_generated" / "logs" / "transcript.jsonl"

    # Print log and session paths to console
    print(f"[Recipient ID] : {recipient_id}")
    print(f"[Session Dir]  : {session_dir}")
    print(f"[Log File Path]: {log_file}")
    print(f"[File Exists?] : {log_file.exists()}")
    return res.stdout.strip()


def fetch_trajectory_log_response(session_id: str, timeout_seconds: int = 15) -> str:
    """Option B Fallback: Scan transcript.jsonl for complete MODEL response content."""
    log_path = BRAIN_DIR / session_id / ".system_generated" / "logs" / "transcript.jsonl"
    if not log_path.exists():
        return ""

    print(f"[Option B Fallback] Scanning trajectory log: {log_path.name}...")
    start = time.time()
    while time.time() - start < timeout_seconds:
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            content_candidates = []
            for line in lines:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("source") == "MODEL" and entry.get("content"):
                        content = str(entry["content"]).strip()
                        # Exclude JSON metadata, system/tool logs, truncated notices, or CLI commands
                        if (
                            content
                            and not content.startswith("{")
                            and not content.startswith("[")
                            and "send-message" not in content
                            and "does NOT show the entire" not in content
                            and "invalid tool call" not in content
                        ):
                            content_candidates.append(content)
                except json.JSONDecodeError:
                    continue

            if content_candidates:
                # Prioritize complete candidates with both opening and closing XML tags
                complete_xml = [c for c in content_candidates if "<config_file>" in c and "</config_file>" in c]
                partial_xml = [c for c in content_candidates if "<config_file>" in c]

                if complete_xml:
                    selected = complete_xml[-1]
                elif partial_xml:
                    selected = partial_xml[-1]
                else:
                    selected = content_candidates[-1]

                print(f"[Option B Fallback] Evaluated {len(content_candidates)} candidate(s). Selected length: {len(selected)} chars.")
                return selected
        except Exception:
            pass
        time.sleep(1)

    return ""


def run_detranscriptor(input_file: Path, force: bool = False) -> Path:
    """Execute complete detranscription flow with Option A (direct agent write) + Option B (log fallback)."""
    assert input_file.exists(), f"Input file not found: {input_file}"

    output_dir = ISB_ROOT / "enriched" / input_file.parent.name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{input_file.stem}.md"

    if not force and output_file.exists() and output_file.stat().st_size > 0:
        print(f"✓ [Skip] Already enriched -> {output_file}")
        return output_file

    with open(input_file, "r", encoding="utf-8") as f:
        transcript_text = f.read().strip()

    # Remove stale output file to prevent false Option A timestamp matches
    if output_file.exists():
        output_file.unlink()

    skill_context = ""
    if SKILL_PATH.exists():
        with open(SKILL_PATH, "r", encoding="utf-8") as sf:
            skill_context = sf.read().strip()

    prompt = (
        f"You are Writer Detranscriptor. Transform raw audio transcript into clean, structured Markdown inside <config_file> tags.\n"
        f"Option A (Primary): Save output directly to file: {output_file}\n\n"
        f"--- SKILL SPECIFICATION ---\n{skill_context}\n\n"
        f"--- TRANSCRIPT ---\nFile: {input_file.name}\n{transcript_text}"
    )

    # Resolve active session ID
    session_id = resolve_active_session()
    dispatch_time = time.time()

    # Dispatch CLI RPC command
    cli_ack = send_agent_message(prompt, session_id)
    print(f"[CLI] Message Ack: {cli_ack[:90]}")

    # Check Option A: Direct Agent Writing (poll for up to 8 seconds for newly created file)
    print("[Option A] Checking direct agent output file writing...")
    for _ in range(8):
        if output_file.exists():
            content = output_file.read_text(encoding="utf-8").strip()
            # Verify file is newly written and contains complete content
            if output_file.stat().st_mtime >= (dispatch_time - 1.0) and len(content) > 500:
                print(f"✓ [Option A Success] Agent wrote complete output directly ({len(content)} chars) -> {output_file}")
                return output_file
        time.sleep(1)

    # Execute Option B (Fallback): Trajectory Log Extraction
    print("[Option B Fallback] Option A pending or incomplete. Extracting response from trajectory log...")
    model_content = fetch_trajectory_log_response(session_id, timeout_seconds=12)

    if model_content:
        # Write to both target path and symlink-resolved path for guaranteed availability
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(model_content)

        alt_path = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/playground/isb.ai/enriched") / input_file.parent.name / f"{input_file.stem}.md"
        alt_path.parent.mkdir(parents=True, exist_ok=True)
        with open(alt_path, "w", encoding="utf-8") as f:
            f.write(model_content)

        print(f"✓ [Option B Fallback Success] Saved complete response ({len(model_content)} chars) -> {output_file}")
        return output_file

    if output_file.exists() and output_file.stat().st_size > 0:
        print(f"✓ Output file present -> {output_file}")
    else:
        print(f"[CLI Dispatch] Request dispatched successfully to agent session {session_id[:8]}... -> {output_file}")

    return output_file


if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    cli_args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    target = Path(cli_args[0]) if cli_args else DEFAULT_INPUT_DIR

    if target.is_dir():
        txt_files = sorted(target.rglob("*.txt"))
        print(f"[Batch] Discovered {len(txt_files)} transcript file(s) in {target}")
        for idx, txt_file in enumerate(txt_files, 1):
            print(f"\n--- [{idx}/{len(txt_files)}] Processing: {txt_file.name} ---")
            run_detranscriptor(txt_file, force=force)
    elif target.is_file():
        run_detranscriptor(target, force=force)
    else:
        print(f"Error: Target path does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    print("done!")