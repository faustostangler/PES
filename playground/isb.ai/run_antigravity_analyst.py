#!/usr/bin/env python3
"""Antigravity CLI Detranscriptor - Direct KISS Runner."""

import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

# --- Config ---
ISB_ROOT = Path(__file__).parent
DEFAULT_INPUT_FILE = ISB_ROOT / "raw" / "Elementar" / "2026-04-24-nmqFA_Z5jmA.txt"
SKILL_PATH = Path(
    "/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills/writer-detranscriptor/SKILL.md"
)


def get_antigravity_env() -> dict[str, str]:
    """Resolve active gRPC environment for agentapi with port validation."""
    env = os.environ.copy()
    binary_path = "/home/stangler/.gemini/antigravity-ide/bin/agentapi"
    if not Path(binary_path).exists():
        binary_path = "agentapi"

    ls_addr = env.get("ANTIGRAVITY_LS_ADDRESS")
    csrf_token = env.get("ANTIGRAVITY_CSRF_TOKEN")

    # Target active conversation ID for handshake check
    target_conv = "0e69775c-ba22-4a48-ad18-ba6a318c9a04"

    def is_valid_grpc(port: str, token: str) -> bool:
        test_env = env.copy()
        test_env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
        test_env["ANTIGRAVITY_CSRF_TOKEN"] = token
        try:
            res = subprocess.run(
                [binary_path, "get-conversation-metadata", target_conv],
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
                                    print(f"[AntigravityCLI] Validated gRPC LS on 127.0.0.1:{port}")
                                    return env
    except Exception as e:
        print(f"[AntigravityCLI] LS port scan exception: {e}")

    env["ANTIGRAVITY_LS_ADDRESS"] = "127.0.0.1:41667"
    env["ANTIGRAVITY_CSRF_TOKEN"] = "ff53390d-3617-40f6-836e-6c5375ff5817"
    return env


def get_conversation_id() -> str:
    """Find active listening conversation ID or fallback to UUID."""
    env_id = os.getenv("ANTIGRAVITY_CONVERSATION_ID") or os.getenv("ANTIGRAVITY_TRAJECTORY_ID")
    if env_id:
        return env_id

    brain_dir = Path("/home/stangler/.gemini/antigravity-ide/brain")
    if brain_dir.exists():
        recent_logs = sorted(
            brain_dir.glob("*/.system_generated/logs/transcript.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if recent_logs:
            return recent_logs[0].parent.parent.parent.name

    return str(uuid.uuid4())


def send_agent_message(prompt: str, conv_id: str) -> str:
    """Send CLI command to agent via agentapi."""
    binary_path = "/home/stangler/.gemini/antigravity-ide/bin/agentapi"
    if not Path(binary_path).exists():
        binary_path = "agentapi"

    env = get_antigravity_env()
    cmd = [binary_path, "send-message", conv_id, prompt]
    print(f"[CLI] Sending CLI command to agent session ({conv_id})...")
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return res.stdout.strip()


def run_detranscriptor(input_file: Path) -> Path:
    """Send transcript prompt to agent and save output markdown."""
    assert input_file.exists(), f"Input file not found: {input_file}"

    with open(input_file, "r", encoding="utf-8") as f:
        transcript_text = f.read()

    output_dir = ISB_ROOT / "enriched" / input_file.parent.name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{input_file.stem}.md"

    skill_context = ""
    if SKILL_PATH.exists():
        with open(SKILL_PATH, "r", encoding="utf-8") as sf:
            skill_context = sf.read()

    prompt = (
        f"You are Writer Detranscriptor. Transform raw transcript into clean structured Markdown inside <config_file> tags.\n"
        f"Save output directly to: {output_file}\n\n"
        f"--- SKILL ---\n{skill_context}\n\n"
        f"--- TRANSCRIPT ---\n{transcript_text}"
    )

    if len(prompt) > 100_000:
        prompt = (
            f"You are Writer Detranscriptor. Transform raw transcript into clean structured Markdown inside <config_file> tags.\n"
            f"Save output directly to: {output_file.resolve()}\n\n"
            f"Input file path: {input_file.resolve()}\n"
            f"Skill specification path: {SKILL_PATH.resolve()}\n"
            f"Note: Raw transcript text omitted from prompt payload to prevent CLI argument length limits.\n"
            f"Please use view_file to read {input_file.resolve()}, apply writer-detranscriptor skill, and write the result directly to {output_file.resolve()}."
        )

    conv_id = get_conversation_id()
    cli_response = send_agent_message(prompt, conv_id)
    print(f"[CLI] Command dispatched! Response metadata: {cli_response[:80]}")

    # If response is direct text (not JSON RPC container), write to file
    if cli_response and not cli_response.startswith("{") and not cli_response.startswith("["):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cli_response)

    if output_file.exists() and output_file.stat().st_size > 0:
        print(f"✓ Output verified -> {output_file}")
    else:
        print(f"[CLI] Payload dispatched to agent -> {output_file}")

    return output_file


if __name__ == "__main__":
    cli_args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    target = Path(cli_args[0]) if cli_args else DEFAULT_INPUT_FILE
    run_detranscriptor(target)
