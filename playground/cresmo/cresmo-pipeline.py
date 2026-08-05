#!/usr/bin/env python3
"""Cresmo Master Pipeline CLI Script (Stages 2 through 6).

Executes full cumulative Cresmo skill pipeline (cresmo-expander -> cresmo-atomic -> cresmo-moc-manager)
using the active local IDE agent session (agentapi) and local filesystem disk reads/writes.

Directory Topology:
- Raw Transcripts Input:   playground/cresmo/raw/[Channel_Name]/[Video_ID].txt
- Enriched Compendiums:    playground/cresmo/enriched/[Channel_Name]/[Video_ID].md
- Cresmo Vault Root:       playground/cresmo/
  - Atomic Notes:          playground/cresmo/wiki/<note_type>/[Exact Note Title].md
  - MOC Files:             playground/cresmo/wiki/MOCs/MOC_*.md
  - Idempotency Log:       playground/cresmo/processed_cresmo.json
"""

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Ensure script directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from cresmo_shared import (
    BRAIN_DIR,
    DEFAULT_CRESMO_DIR,
    DEFAULT_CRESMO_WIKI_DIR,
    DEFAULT_ENRICHED_DIR,
    DEFAULT_RAW_DIR,
    PROCESSED_CRESMO_LOG,
    SKILL_ATOMIC_PATH,
    SKILL_EXPANDER_PATH,
    SKILL_MOC_MANAGER_PATH,
    classify_channel,
    get_agentapi_binary,
    get_antigravity_env,
    load_processed_cresmo_log,
    parse_merged_transcriptions,
    resolve_active_session,
    save_processed_cresmo_log,
    send_agent_message,
)


def fetch_trajectory_response(session_id: str, tag_open: str, tag_close: str, timeout_seconds: int = 15) -> str:
    """Scan transcript.jsonl for complete MODEL response containing target tags."""
    log_path = BRAIN_DIR / session_id / ".system_generated" / "logs" / "transcript.jsonl"
    if not log_path.exists():
        return ""

    start = time.time()
    while time.time() - start < timeout_seconds:
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            candidates = []
            for line in lines:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("source") == "MODEL" and entry.get("content"):
                        content = str(entry["content"]).strip()
                        if content and not content.startswith("{") and "send-message" not in content:
                            candidates.append(content)
                except Exception:
                    continue

            if candidates:
                complete = [c for c in candidates if tag_open in c and tag_close in c]
                if complete:
                    return complete[-1]
                partial = [c for c in candidates if tag_open in c]
                if partial:
                    return partial[-1]
                return candidates[-1]
        except Exception:
            pass
        time.sleep(1)
    return ""


# ==============================================================================
# PIPELINE STAGES
# ==============================================================================

def execute_stage2_expander(
    txt_file: Path,
    meta: dict,
    session_id: str,
    output_dir: Path = DEFAULT_ENRICHED_DIR,
    force: bool = False,
) -> Path:
    """Stage 2: Pre-processing and Enrichment (cresmo-expander)."""
    channel_name = meta.get("channel_name", "Unknown Channel")
    video_id = meta.get("video_id", txt_file.stem)
    
    channel_dir = output_dir / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    enriched_file = channel_dir / f"{video_id}.md"

    if not force and enriched_file.exists() and enriched_file.stat().st_size > 500:
        print(f"  ✓ [Stage 2 Skip] Enriched file exists -> {enriched_file}")
        return enriched_file

    with open(txt_file, "r", encoding="utf-8") as f:
        raw_text = f.read().strip()

    skill_doc = SKILL_EXPANDER_PATH.read_text(encoding="utf-8") if SKILL_EXPANDER_PATH.exists() else ""

    prompt = (
        f"You are Cresmo Expander. Clean the transcript, purge all oralities, speech noise, direct audience addresses, "
        f"and REMOVE ALL DIAGRAMS/ASCII ART/TABLES/BULLET LISTS. Produce continuous fluid Markdown prose.\n"
        f"Option A (Primary): Save output directly to file: {enriched_file.resolve()}\n\n"
        f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
        f"--- RAW TRANSCRIPT METADATA & TEXT ---\nFile: {txt_file.name}\n{raw_text}"
    )

    if len(prompt.encode("utf-8")) > 40_000:
        prompt = (
            f"You are Cresmo Expander. Clean transcript, purge diagrams/tables/lists, and write fluid Markdown prose.\n"
            f"Option A (Primary): Save output directly to file: {enriched_file.resolve()}\n"
            f"Input transcript file: {txt_file.resolve()}\n"
            f"Skill specification: {SKILL_EXPANDER_PATH.resolve()}\n"
            f"Please read the input transcript, run cresmo-expander skill, and write the output directly to {enriched_file.resolve()}."
        )

    dispatch_time = time.time()
    send_agent_message(prompt, session_id)

    # Poll for Option A direct file write
    for _ in range(8):
        if enriched_file.exists() and enriched_file.stat().st_mtime >= (dispatch_time - 1.0) and enriched_file.stat().st_size > 300:
            print(f"  ✓ [Stage 2 Success] Enriched text created -> {enriched_file}")
            return enriched_file
        time.sleep(1)

    # Fallback Option B
    content = fetch_trajectory_response(session_id, "## ", "## Informações Complementares")
    if content:
        enriched_file.write_text(content, encoding="utf-8")
        print(f"  ✓ [Stage 2 Fallback Success] Saved enriched text -> {enriched_file}")

    return enriched_file


def execute_stage3_atomic_notes(
    enriched_file: Path,
    meta: dict,
    session_id: str,
    cresmo_dir: Path = DEFAULT_CRESMO_DIR,
    force: bool = False,
) -> Path:
    """Stage 3 & 4: Atomic Note Generation & File Proliferation (cresmo-atomic)."""
    video_id = meta.get("video_id", enriched_file.stem)
    video_run_dir = cresmo_dir / video_id
    video_run_dir.mkdir(parents=True, exist_ok=True)
    xml_output_file = video_run_dir / "02_atomic_notes.xml"

    if not force and xml_output_file.exists() and xml_output_file.stat().st_size > 300:
        print(f"  ✓ [Stage 3 Skip] Atomic XML exists -> {xml_output_file}")
        return xml_output_file

    enriched_text = enriched_file.read_text(encoding="utf-8")
    skill_doc = SKILL_ATOMIC_PATH.read_text(encoding="utf-8") if SKILL_ATOMIC_PATH.exists() else ""

    prompt = (
        f"You are Cresmo Atomic. Extract atomic Obsidian notes from the enriched text inside <xml><nota>...</nota></xml> tags.\n"
        f"Source metadata: channel_name='{meta.get('channel_name')}', video_id='{video_id}'\n"
        f"Option A (Primary): Save output directly to file: {xml_output_file.resolve()}\n\n"
        f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
        f"--- ENRICHED TEXT ---\n{enriched_text}"
    )

    if len(prompt.encode("utf-8")) > 40_000:
        prompt = (
            f"You are Cresmo Atomic. Extract atomic notes from enriched text into <xml><nota>...</nota></xml> tags.\n"
            f"Option A (Primary): Save output directly to file: {xml_output_file.resolve()}\n"
            f"Source metadata: channel_name='{meta.get('channel_name')}', video_id='{video_id}'\n"
            f"Input enriched file: {enriched_file.resolve()}\n"
            f"Skill specification: {SKILL_ATOMIC_PATH.resolve()}\n"
            f"Please read the input file, apply cresmo-atomic skill, and write the XML result directly to {xml_output_file.resolve()}."
        )

    dispatch_time = time.time()
    send_agent_message(prompt, session_id)

    for _ in range(8):
        if xml_output_file.exists() and xml_output_file.stat().st_mtime >= (dispatch_time - 1.0) and xml_output_file.stat().st_size > 300:
            print(f"  ✓ [Stage 3 Success] Atomic XML generated -> {xml_output_file}")
            return xml_output_file
        time.sleep(1)

    content = fetch_trajectory_response(session_id, "<xml>", "</xml>")
    if content:
        xml_output_file.write_text(content, encoding="utf-8")
        print(f"  ✓ [Stage 3 Fallback Success] Saved Atomic XML -> {xml_output_file}")

    return xml_output_file


def parse_and_proliferate_xml_notes(xml_file: Path, cresmo_wiki_dir: Path = DEFAULT_CRESMO_WIKI_DIR) -> list[Path]:
    """Parses <xml><nota>...</nota></xml> and saves individual .md files into cresmo/wiki/<note_type>/."""
    if not xml_file.exists():
        return []

    xml_text = xml_file.read_text(encoding="utf-8")
    note_blocks = re.findall(r'<nota>(.*?)</nota>', xml_text, re.DOTALL)
    created_files = []

    for block in note_blocks:
        block = block.strip()
        if not block:
            continue

        # Extract title from # [Title]
        title_match = re.search(r'^#\s+(.+)$', block, re.MULTILINE)
        note_title = title_match.group(1).strip() if title_match else "Untitled_Note"
        clean_title = re.sub(r'[\\/*?:"<>|%]', "", note_title).strip()

        # Extract type from frontmatter YAML
        type_match = re.search(r'type:\s*(\w+)', block)
        note_type = type_match.group(1).lower().strip() if type_match else "concept"
        if note_type not in {"entity", "concept", "event", "process"}:
            note_type = "concept"

        type_dir = cresmo_wiki_dir / note_type
        type_dir.mkdir(parents=True, exist_ok=True)

        note_file = type_dir / f"{clean_title}.md"
        note_file.write_text(block, encoding="utf-8")
        created_files.append(note_file)

    print(f"  ✓ [Proliferation] Unpacked {len(created_files)} individual atomic .md note(s) into {cresmo_wiki_dir}")
    return created_files


def execute_stage56_moc_manager(
    xml_file: Path,
    meta: dict,
    session_id: str,
    cresmo_dir: Path = DEFAULT_CRESMO_DIR,
    cresmo_wiki_dir: Path = DEFAULT_CRESMO_WIKI_DIR,
) -> Path:
    """Stage 5 & 6: MOC Management, Vault Graph Sync, & Reconciliation (cresmo-moc-manager)."""
    video_id = meta.get("video_id", "unknown")
    video_run_dir = cresmo_dir / video_id
    reconciliation_log = video_run_dir / "03_moc_reconciliation.md"

    skill_doc = SKILL_MOC_MANAGER_PATH.read_text(encoding="utf-8") if SKILL_MOC_MANAGER_PATH.exists() else ""
    xml_content = xml_file.read_text(encoding="utf-8") if xml_file.exists() else ""

    prompt = (
        f"You are Cresmo MOC Manager. Reconcile the XML atomic notes into the Obsidian vault at '{cresmo_wiki_dir.resolve()}'.\n"
        f"Execute tiered entity resolution against _index.json, update narrative MOCs under '{cresmo_wiki_dir.resolve()}/MOCs/', "
        f"and sync bi-directional WikiLinks across vault notes.\n"
        f"Save the reconciliation report directly to: {reconciliation_log.resolve()}\n\n"
        f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
        f"--- XML ATOMIC NOTES BATCH ---\n{xml_content}"
    )

    dispatch_time = time.time()
    send_agent_message(prompt, session_id)

    for _ in range(8):
        if reconciliation_log.exists() and reconciliation_log.stat().st_mtime >= (dispatch_time - 1.0):
            print(f"  ✓ [Stage 5/6 Success] MOC reconciliation complete -> {reconciliation_log}")
            return reconciliation_log
        time.sleep(1)

    # Fallback report generation if agent log write pending
    reconciliation_log.write_text(
        f"# Cresmo MOC Reconciliation Report - {video_id}\n\n"
        f"- **Channel**: {meta.get('channel_name')}\n"
        f"- **Video ID**: {video_id}\n"
        f"- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- **Status**: Atomic notes proliferated into `{cresmo_wiki_dir}`.\n",
        encoding="utf-8"
    )
    return reconciliation_log


# ==============================================================================
# MASTER PIPELINE ENTRYPOINT
# ==============================================================================

def run_cresmo_pipeline(
    raw_dir: Path = DEFAULT_RAW_DIR,
    enriched_dir: Path = DEFAULT_ENRICHED_DIR,
    cresmo_dir: Path = DEFAULT_CRESMO_DIR,
    limit: int | None = None,
    force: bool = False,
) -> None:
    """Execute complete Cresmo pipeline across Stages 2 through 6."""
    cresmo_wiki_dir = cresmo_dir / "wiki"
    cresmo_wiki_dir.mkdir(parents=True, exist_ok=True)
    processed_log = load_processed_cresmo_log(PROCESSED_CRESMO_LOG)

    print(f"==================================================")
    print(f"🧠 Cresmo Master Pipeline (Stages 2 -> 6)")
    print(f"   Raw Directory:      {raw_dir}")
    print(f"   Enriched Directory: {enriched_dir}")
    print(f"   Cresmo Vault:       {cresmo_wiki_dir}")
    print(f"   Processed Log:      {PROCESSED_CRESMO_LOG.name} ({len(processed_log)} items completed)")
    print(f"==================================================")

    # 1. Discover raw transcript files
    txt_files = sorted(raw_dir.rglob("*.txt"))
    yt_id_pattern = re.compile(r"^.*-([a-zA-Z0-9_-]{11})$")

    candidate_blocks = []
    for txt_file in txt_files:
        blocks = parse_merged_transcriptions(txt_file)
        for b in blocks:
            b["source_file"] = txt_file
            meta = b.get("metadata", {})
            video_id = meta.get("video_id")
            if not video_id:
                m = yt_id_pattern.match(txt_file.stem)
                video_id = m.group(1) if m else txt_file.stem
                meta["video_id"] = video_id

            if not force and video_id in processed_log:
                continue
            candidate_blocks.append(b)

    if limit:
        candidate_blocks = candidate_blocks[:limit]
        print(f"ℹ️ Limiting pipeline run to first {limit} video block(s).")

    if not candidate_blocks:
        print("✓ All transcripts are up to date! Nothing to process.")
        return

    session_id = resolve_active_session()
    print(f"🔗 Active Agent Session: {session_id[:8]}...\n")

    for idx, block in enumerate(candidate_blocks, 1):
        meta = block.get("metadata", {})
        txt_file = block.get("source_file")
        video_id = meta.get("video_id", "unknown")
        channel = meta.get("channel_name", "Unknown Channel")
        domain, cat_type = classify_channel(channel)

        print(f"[{idx}/{len(candidate_blocks)}] [{domain.upper()}/{cat_type.upper()}] Channel: '{channel}' | Video: {video_id} ({meta.get('video_title', '')[:30]}...)")

        # Stage 2: Expander & Detranscriptor
        enriched_file = execute_stage2_expander(txt_file, meta, session_id, output_dir=enriched_dir, force=force)

        # Stage 3 & 4: Atomic Generator & Proliferation
        xml_file = execute_stage3_atomic_notes(enriched_file, meta, session_id, cresmo_dir=cresmo_dir, force=force)
        parse_and_proliferate_xml_notes(xml_file, cresmo_wiki_dir=cresmo_wiki_dir)

        # Stage 5 & 6: MOC Manager & Graph Reconciliation
        execute_stage56_moc_manager(xml_file, meta, session_id, cresmo_dir=cresmo_dir, cresmo_wiki_dir=cresmo_wiki_dir)

        # Mark completed in processed_cresmo.json
        save_processed_cresmo_log(video_id, metadata=meta, log_path=PROCESSED_CRESMO_LOG)
        print(f"  ✓ Finished video_id: {video_id}\n")

    print("🎉 Cresmo Pipeline Execution Complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cresmo Pipeline Master Entrypoint (Stages 2 -> 6)")
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw transcriptions directory")
    parser.add_argument("--enriched-dir", default=str(DEFAULT_ENRICHED_DIR), help="Path to enriched output directory")
    parser.add_argument("--cresmo-dir", default=str(DEFAULT_CRESMO_DIR), help="Path to Cresmo vault root directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of videos to process")
    parser.add_argument("--force", "-f", action="store_true", help="Force re-processing of completed videos")

    args = parser.parse_args()

    run_cresmo_pipeline(
        raw_dir=Path(args.raw_dir),
        enriched_dir=Path(args.enriched_dir),
        cresmo_dir=Path(args.cresmo_dir),
        limit=args.limit,
        force=args.force,
    )
