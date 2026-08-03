#!/usr/bin/env python3
"""Ultra-Linear Single-Function CLI Detranscriptor.

Executes the entire detranscription pipeline (gRPC environment discovery, session
allocation, RPC dispatch, Option A file polling, and Option B log fallback) in a
single, continuous, top-to-bottom function flow.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


def main() -> None:
    # --- Configuration ---
    isb_root = Path(__file__).parent
    raw_root = isb_root / "raw"
    default_input_dir = raw_root
    skill_path = Path(
        "/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills/writer-detranscriptor/SKILL.md"
    )
    brain_dir = Path("/home/stangler/.gemini/antigravity-ide/brain")
    default_agentapi = "/home/stangler/.gemini/antigravity-ide/bin/agentapi"
    binary_path = default_agentapi if Path(default_agentapi).exists() else "agentapi"

    # --- 1. Parse Arguments ---
    force = "--force" in sys.argv or "-f" in sys.argv
    cli_args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    target = Path(cli_args[0]) if cli_args else default_input_dir

    if not target.exists():
        print(f"Error: Target path does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    # --- 2. Resolve & Validate gRPC Environment ---
    env = os.environ.copy()
    ls_addr = env.get("ANTIGRAVITY_LS_ADDRESS")
    csrf_token = env.get("ANTIGRAVITY_CSRF_TOKEN")
    env_validated = False

    # Check environment variables
    if ls_addr and ":" in ls_addr:
        port = ls_addr.split(":", 1)[1]
        test_env = env.copy()
        test_env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
        test_env["ANTIGRAVITY_CSRF_TOKEN"] = csrf_token or ""
        try:
            res = subprocess.run(
                [binary_path, "get-conversation-metadata", "0e69775c-ba22-4a48-ad18-ba6a318c9a04"],
                capture_output=True,
                text=True,
                timeout=1.5,
                env=test_env,
            )
            out = (res.stdout + "\n" + res.stderr).lower()
            if (
                res.returncode == 0
                and "error reading server preface" not in out
                and "connection reset" not in out
                and "connection refused" not in out
                and "unavailable" not in out
            ):
                env_validated = True
        except Exception:
            pass

    # Process scan if env vars are invalid
    if not env_validated:
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
                                        if (
                                            res.returncode == 0
                                            and "error reading server preface" not in out
                                            and "connection reset" not in out
                                            and "connection refused" not in out
                                            and "unavailable" not in out
                                        ):
                                            env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{port}"
                                            env["ANTIGRAVITY_CSRF_TOKEN"] = token
                                            env_validated = True
                                            print(f"[Env] Validated gRPC Language Server on 127.0.0.1:{port}")
                                            break
                                    except Exception:
                                        pass
                        if env_validated:
                            break
        except Exception as e:
            print(f"[Env] LS scan warning: {e}")

    if not env_validated:
        env["ANTIGRAVITY_LS_ADDRESS"] = "127.0.0.1:41667"
        env["ANTIGRAVITY_CSRF_TOKEN"] = "ff53390d-3617-40f6-836e-6c5375ff5817"

    # --- 3. Resolve Active Session ---
    session_id = os.getenv("ANTIGRAVITY_CONVERSATION_ID") or os.getenv("ANTIGRAVITY_TRAJECTORY_ID")
    if session_id:
        print(f"[Session] Using environment session ID: {session_id}")
    else:
        # Primary Strategy: Attempt to allocate a NEW conversation session via agentapi
        print("[Session] Allocating new conversation session via agentapi...")
        try:
            res = subprocess.run(
                [binary_path, "new-conversation", "Initializing detranscription session"],
                capture_output=True,
                text=True,
                timeout=3,
                env=env,
            )
            data = json.loads(res.stdout)
            session_id = data.get("response", {}).get("conversationId") or data.get("conversationId")
            if session_id:
                print(f"[Session] Allocated NEW session ID: {session_id}")
        except Exception as e:
            print(f"[Session] new-conversation notice: {e}")

        # Fallback Strategy: Auto-detect most recent active conversation session in brain/
        if not session_id and brain_dir.exists():
            recent_logs = sorted(
                brain_dir.glob("*/.system_generated/logs/transcript.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if recent_logs:
                session_folder = recent_logs[0].parent.parent.parent
                session_id = session_folder.name
                print(f"[Session] Fallback auto-detected active session: {session_id}")

    if not session_id:
        raise RuntimeError("Failed to resolve or allocate an active Antigravity session ID.")

    session_folder_path = brain_dir / session_id
    print(f"[Session] Full directory path: {session_folder_path.resolve()}")

    # --- 4. Load Skill Context ---
    skill_context = ""
    if skill_path.exists():
        skill_context = skill_path.read_text(encoding="utf-8").strip()

    # --- 5. Build Target Files List ---
    if target.is_dir():
        txt_files = sorted(target.rglob("*.txt"))
        print(f"[Batch] Discovered {len(txt_files)} transcript file(s) in {target}")
    else:
        txt_files = [target]

    # --- 6. Continuous Linear Loop ---
    for idx, input_file in enumerate(txt_files, 1):
        # print(f"\n--- [{idx}/{len(txt_files)}] Processing: {input_file.name} ---")

        try:
            rel_path = input_file.relative_to(raw_root)
            output_file = (isb_root / "enriched" / rel_path).with_suffix(".md")
        except ValueError:
            output_file = (isb_root / "enriched" / input_file.parent.name / f"{input_file.stem}.md")

        output_dir = output_file.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        if not force and output_file.exists() and output_file.stat().st_size > 0:
            # print(f"✓ [Skip] Already enriched -> {output_file}")
            continue

        transcript_text = input_file.read_text(encoding="utf-8").strip()

        if output_file.exists():
            output_file.unlink()

        prompt = (
            f"You are Writer Detranscriptor. Transform raw audio transcript into clean, structured Markdown inside <config_file> tags.\n"
            f"Option A (Primary): Save output directly to file: {output_file}\n\n"
            f"--- SKILL SPECIFICATION ---\n{skill_context}\n\n"
            f"--- TRANSCRIPT ---\nFile: {input_file.name}\n{transcript_text}"
        )

        if len(prompt.encode("utf-8")) > 40_000:
            prompt = (
                f"You are Writer Detranscriptor. Transform raw audio transcript into clean, structured Markdown inside <config_file> tags.\n"
                f"Option A (Primary): Save output directly to file: {output_file.resolve()}\n\n"
                f"Input file path: {input_file.resolve()}\n"
                f"Skill specification path: {skill_path.resolve()}\n"
                f"Note: Raw transcript text omitted from prompt payload to prevent CLI argument length limits.\n"
                f"Please use view_file to read {input_file.resolve()}, apply writer-detranscriptor skill, and write the result directly to {output_file.resolve()}."
            )

        dispatch_time = time.time()
        # print(f"[CLI] Dispatching RPC payload to session ({session_id[:8]}...)...")
        res = subprocess.run([binary_path, "send-message", session_id, prompt], capture_output=True, text=True, env=env)
        cli_ack = res.stdout.strip()
        # print(f"[CLI] Message Ack: {cli_ack[:90]}")

        # --- Artifact Completion Polling (Zero transcript.jsonl dependency) ---
        # print(f"[Bridge Job] Waiting for agent artifact output -> {output_file.name}...")
        job_done = False
        max_wait_seconds = 60
        scan_start = time.time()

        while time.time() - scan_start < max_wait_seconds:
            if output_file.exists():
                content = output_file.read_text(encoding="utf-8").strip()
                if output_file.stat().st_mtime >= (dispatch_time - 1.0) and len(content) > 200:
                    print(f"{output_file}")
                    job_done = True
                    break
            time.sleep(2)

        if not job_done:
            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"✓ Output file present -> {output_file}")
            else:
                print(f"[CLI Dispatch] Request dispatched to session {session_id[:8]}... Output pending -> {output_file}")

    print("Done!")


if __name__ == "__main__":
    main()
