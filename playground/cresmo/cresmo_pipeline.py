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
from pathlib import Path
import re
import sys
import textwrap
import time

# Ensure script directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from cresmo_shared import (
    BRAIN_DIR,
    DATETIME_FORMAT,
    DEFAULT_CATEGORIES,
    DEFAULT_CRESMO_DIR,
    DEFAULT_CRESMO_WIKI_DIR,
    DEFAULT_ENRICHED_DIR,
    DEFAULT_RAW_DIR,
    PROCESSED_CRESMO_LOG,
    SENTINEL_PREFIX,
    SKILL_ATOMIC_PATH,
    SKILL_EXPANDER_PATH,
    SKILL_MOC_MANAGER_PATH,
    classify_channel,
    clear_session_history,
    load_processed_cresmo_log,
    parse_merged_transcriptions,
    resolve_active_session,
    save_processed_cresmo_log,
    send_agent_message,
)

# --- Polling & Timing Defaults ---
DEFAULT_TRAJECTORY_TIMEOUT_SECONDS: int = 15
POLL_MAX_ATTEMPTS: int = 1000
POLL_SLEEP_SECONDS: float = 1.0
POLL_DISPATCH_TIME_BUFFER: float = 1.0

# --- Payload & File Size Thresholds ---
PROMPT_MAX_BYTES_INLINE: int = 40_000
MIN_ENRICHED_EXISTING_BYTES: int = 500
MIN_VALID_OUTPUT_BYTES: int = 300
MIN_RECONCILIATION_LOG_BYTES: int = 200
MAX_CANDIDATE_PARSE_LIMIT: int = 1000

# --- Domain & Typology Standards ---
VALID_NOTE_TYPES: frozenset[str] = frozenset({"entity", "concept", "event", "process"})
DEFAULT_NOTE_TYPE: str = "concept"
DEFAULT_NOTE_TITLE: str = "Untitled_Note"
DEFAULT_CHANNEL_NAME: str = "Unknown Channel"
DEFAULT_VIDEO_ID: str = "unknown"
INDEX_JSON_FILENAME: str = "_index.json"

# --- Markers & Tag Delimiters ---
TAG_MARKDOWN_H2: str = "## "
TAG_COMPLEMENTARY_INFO: str = "## Informações Complementares"
TAG_XML_OPEN: str = "<xml>"
TAG_XML_CLOSE: str = "</xml>"

# --- Compiled Regular Expressions ---
YT_ID_PATTERN: re.Pattern[str] = re.compile(r"^.*-([a-zA-Z0-9_-]{11})$")
NOTA_XML_PATTERN: re.Pattern[str] = re.compile(r"<nota>(.*?)</nota>", re.DOTALL)
CDATA_START_PATTERN: re.Pattern[str] = re.compile(r"^\s*<!\[CDATA\[\s*")
CDATA_END_PATTERN: re.Pattern[str] = re.compile(r"\s*\]\]>\s*$")
TITLE_H1_BRACKET_PATTERN: re.Pattern[str] = re.compile(r"^\s*#\s+\[\[(.*?)\]\]", re.MULTILINE)
TITLE_H1_PATTERN: re.Pattern[str] = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
BRACKETS_PATTERN: re.Pattern[str] = re.compile(r"\[\[(.*?)\]\]")
CLEAN_TITLE_SANITIZE_PATTERN: re.Pattern[str] = re.compile(r'[\\/*?:"<>|%\[\]]')
TYPE_EXTRACT_PATTERN: re.Pattern[str] = re.compile(r"type:\s*(\w+)")
ALIASES_EXTRACT_PATTERN: re.Pattern[str] = re.compile(r"aliases:\s*\[(.*?)\]")
TAGS_INLINE_PATTERN: re.Pattern[str] = re.compile(r"^tags:\s*\[(.*)\]$")
INLINE_LIST_PATTERN: re.Pattern[str] = re.compile(r"^\[(.*)\]$")
YAML_KEY_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_-]+:")

# --- Prompts & Directives ---
STAGE2_PROMPT_TASK: str = (
    "You are Cresmo Expander. This is your most important task: Clean the transcript, "
    "purge all oralities, speech noise, direct audience addresses, \n"
    "and REMOVE ALL DIAGRAMS/ASCII ART/TABLES/BULLET LISTS. Produce continuous fluid Markdown prose.\n"
)
STAGE3_PRE_PROMPT: str = (
    "You are Cresmo Atomic. Extract atomic Obsidian notes from the enriched text inside "
    "<xml> <notas><nota></nota></notas> tags.\n"
)


def fetch_trajectory_response(
    session_id: str,
    tag_open: str,
    tag_close: str,
    timeout_seconds: int = DEFAULT_TRAJECTORY_TIMEOUT_SECONDS,
) -> str:
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
        time.sleep(POLL_SLEEP_SECONDS)
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
    isolate_context: bool = True,
    restart_server: bool = False,
) -> Path:
    """Stage 2: Pre-processing and Enrichment (cresmo-expander).

    Reads the raw transcript from `raw/` and saves the expanded, enriched
    compendium Markdown directly into the `enriched/` directory:
    `playground/cresmo/enriched/[Channel_Name]/[Video_ID].md`.
    Stage 2 output is saved in the enriched directory and NEVER in the raw directory.
    """
    channel_name = meta.get("channel_name", DEFAULT_CHANNEL_NAME)
    video_id = meta.get("video_id", txt_file.stem)

    # Target directory is strictly within enriched/
    channel_dir = output_dir / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    enriched_file = channel_dir / f"{video_id}.md"

    if not force and enriched_file.exists() and enriched_file.stat().st_size > MIN_ENRICHED_EXISTING_BYTES:
        return enriched_file

    with open(txt_file, "r", encoding="utf-8") as f:
        raw_text = f.read().strip()

    skill_doc = SKILL_EXPANDER_PATH.read_text(encoding="utf-8") if SKILL_EXPANDER_PATH.exists() else ""

    prompt = STAGE2_PROMPT_TASK + (
        f"Save output directly to enriched file: {enriched_file.resolve()}\n\n"
        f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
        f"--- RAW TRANSCRIPT METADATA & TEXT ---\nFile: {txt_file.name}\n{raw_text}"
    )

    if len(prompt.encode("utf-8")) > PROMPT_MAX_BYTES_INLINE:
        prompt = STAGE2_PROMPT_TASK + (
            f"Save output directly to enriched file: {enriched_file.resolve()}\n"
            f"Input raw transcript file: {txt_file.resolve()}\n"
            f"Skill specification: {SKILL_EXPANDER_PATH.resolve()}\n"
            f"Please read the input raw transcript, run cresmo-expander skill, and write the output directly to {enriched_file.resolve()} in the enriched directory (never in raw)."
        )

    if isolate_context:
        clear_session_history(session_id, restart_server=restart_server)
        prompt = SENTINEL_PREFIX + prompt

    dispatch_time = time.time()
    send_agent_message(prompt, session_id)

    # Poll for Option A direct file write
    for _ in range(POLL_MAX_ATTEMPTS):
        if (
            enriched_file.exists()
            and enriched_file.stat().st_mtime >= (dispatch_time - POLL_DISPATCH_TIME_BUFFER)
            and enriched_file.stat().st_size > MIN_VALID_OUTPUT_BYTES
        ):
            print(f"  ✓ [Stage 2 Success] Enriched text created -> {enriched_file}")
            return enriched_file
        time.sleep(POLL_SLEEP_SECONDS)

    # Fallback Option B
    content = fetch_trajectory_response(session_id, TAG_MARKDOWN_H2, TAG_COMPLEMENTARY_INFO)
    if content:
        enriched_file.write_text(content, encoding="utf-8")
        print(f"  ✓ [Stage 2 Fallback Success] Saved enriched text -> {enriched_file}")
    elif not enriched_file.exists():
        # Fallback Option C: Write raw text if file was not generated by agent
        enriched_file.write_text(raw_text, encoding="utf-8")
        print(f"  ✓ [Stage 2 Raw Fallback] Saved raw text -> {enriched_file}")

    return enriched_file


def execute_stage3_atomic_notes(
    enriched_file: Path,
    meta: dict,
    session_id: str,
    cresmo_dir: Path = DEFAULT_CRESMO_DIR,
    force: bool = False,
    isolate_context: bool = True,
    restart_server: bool = False,
) -> tuple[Path, bool]:
    """Stage 3: Atomic Note Generation (cresmo-atomic). Returns (xml_file, is_newly_generated)."""
    video_id = meta.get("video_id", enriched_file.stem)
    xml_output_file = enriched_file.parent / f"{video_id}.xml"

    if not force and xml_output_file.exists() and xml_output_file.stat().st_size > MIN_VALID_OUTPUT_BYTES:
        return xml_output_file, False

    if not enriched_file.exists():
        return xml_output_file, False

    enriched_text = enriched_file.read_text(encoding="utf-8")
    skill_doc = SKILL_ATOMIC_PATH.read_text(encoding="utf-8") if SKILL_ATOMIC_PATH.exists() else ""

    prompt = STAGE3_PRE_PROMPT + (
        f"Source metadata: channel_name='{meta.get('channel_name')}', video_id='{video_id}'\n"
        f"Save output directly to file: {xml_output_file.resolve()}\n\n"
        f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
        f"--- ENRICHED TEXT ---\n{enriched_text}"
    )

    if len(prompt.encode("utf-8")) > PROMPT_MAX_BYTES_INLINE:
        prompt = STAGE3_PRE_PROMPT + (
            f"Source metadata: channel_name='{meta.get('channel_name')}', video_id='{video_id}'\n"
            f"Save output directly to file: {xml_output_file.resolve()}\n"
            f"Input enriched file: {enriched_file.resolve()}\n"
            f"Skill specification: {SKILL_ATOMIC_PATH.resolve()}\n"
            f"Please read the input file, apply cresmo-atomic skill, and write the XML result directly to {xml_output_file.resolve()}."
        )

    if isolate_context:
        clear_session_history(session_id, restart_server=restart_server)
        prompt = SENTINEL_PREFIX + prompt

    dispatch_time = time.time()
    send_agent_message(prompt, session_id)

    for _ in range(POLL_MAX_ATTEMPTS):
        if (
            xml_output_file.exists()
            and xml_output_file.stat().st_mtime >= (dispatch_time - POLL_DISPATCH_TIME_BUFFER)
            and xml_output_file.stat().st_size > MIN_VALID_OUTPUT_BYTES
        ):
            print(f"  ✓ [Stage 3 Success] Atomic XML generated -> {xml_output_file}")
            return xml_output_file, True
        time.sleep(POLL_SLEEP_SECONDS)

    content = fetch_trajectory_response(session_id, TAG_XML_OPEN, TAG_XML_CLOSE)
    if content:
        xml_output_file.write_text(content, encoding="utf-8")
        print(f"  ✓ [Stage 3 Fallback Success] Saved Atomic XML -> {xml_output_file}")
        return xml_output_file, True

    return xml_output_file, False


def normalize_yaml_tags(content: str) -> str:
    """Format YAML frontmatter to structured format: type, content, domain, cluster, source, aliases."""
    content = textwrap.dedent(content).strip()
    if not content.startswith("---"):
        return content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return content

    frontmatter_text = parts[1]
    body = textwrap.dedent(parts[2]).rstrip()

    note_type = ""
    aliases_line = ""
    content_list = []
    domain_val = ""
    cluster_val = ""
    source_val = ""

    lines = frontmatter_text.splitlines()
    in_tags = False
    in_content = False
    in_aliases = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("type:"):
            note_type = stripped.split(":", 1)[1].strip().lower()
            in_tags = False
            in_content = False
            in_aliases = False
            continue

        if stripped.startswith("aliases:"):
            aliases_line = stripped
            in_tags = False
            in_content = False
            in_aliases = True
            continue

        if stripped.startswith("domain:") and not stripped.startswith("domain/"):
            domain_val = stripped.split(":", 1)[1].strip()
            in_tags = False
            in_content = False
            in_aliases = False
            continue

        if stripped.startswith("cluster:") and not stripped.startswith("cluster/"):
            cluster_val = stripped.split(":", 1)[1].strip()
            in_tags = False
            in_content = False
            in_aliases = False
            continue

        if stripped.startswith("source:") and not stripped.startswith("source/"):
            source_val = stripped.split(":", 1)[1].strip()
            in_tags = False
            in_content = False
            in_aliases = False
            continue

        if stripped.startswith("content:") and not stripped.startswith("content/"):
            in_content = True
            in_tags = False
            in_aliases = False
            inline_content = stripped.split(":", 1)[1].strip()
            if inline_content:
                inline_match = INLINE_LIST_PATTERN.match(inline_content)
                if inline_match:
                    for item in inline_match.group(1).split(","):
                        if item.strip():
                            content_list.append(item.strip().strip("'\""))
            continue

        if stripped.startswith("tags:"):
            in_tags = True
            in_content = False
            in_aliases = False
            inline_match = TAGS_INLINE_PATTERN.match(stripped)
            if inline_match:
                raw_tags = [t.strip().strip("'\"") for t in inline_match.group(1).split(",")]
                for tag in raw_tags:
                    if tag.startswith("content/"):
                        content_list.append(tag[8:].strip())
                    elif tag.startswith("domain/"):
                        domain_val = tag[7:].strip()
                    elif tag.startswith("cluster/"):
                        cluster_val = tag[8:].strip()
                    elif tag.startswith("source/"):
                        source_val = tag[7:].strip()
                    elif not tag.startswith("type/"):
                        content_list.append(tag)
                in_tags = False
            continue

        if in_content:
            if YAML_KEY_PATTERN.match(stripped):
                in_content = False
            elif stripped.startswith("- "):
                content_item = stripped[2:].strip().strip("'\"")
                if content_item:
                    content_list.append(content_item)
                continue
            else:
                in_content = False

        if in_tags:
            if YAML_KEY_PATTERN.match(stripped):
                in_tags = False
            elif stripped.startswith("- "):
                tag_item = stripped[2:].strip().strip("'\"")
                tags = [t.strip().strip("'\"") for t in tag_item.split(",")]
                for tag in tags:
                    if tag.startswith("content/"):
                        content_list.append(tag[8:].strip())
                    elif tag.startswith("domain/") and not domain_val:
                        domain_val = tag[7:].strip()
                    elif tag.startswith("cluster/") and not cluster_val:
                        cluster_val = tag[8:].strip()
                    elif tag.startswith("source/") and not source_val:
                        source_val = tag[7:].strip()
                    elif not tag.startswith("type/"):
                        content_list.append(tag)
                continue
            else:
                in_tags = False

        if in_aliases and stripped.startswith("- "):
            aliases_line += "\n  " + stripped

    new_lines = []
    if note_type:
        new_lines.append(f"type: {note_type}")

    if content_list:
        new_lines.append("content:")
        seen = set()
        for item in content_list:
            if item not in seen:
                seen.add(item)
                new_lines.append(f"  - {item}")

    if domain_val:
        new_lines.append(f"domain: {domain_val}")

    if cluster_val:
        new_lines.append(f"cluster: {cluster_val}")

    if source_val:
        new_lines.append(f"source: {source_val}")

    if aliases_line:
        new_lines.append(aliases_line)

    new_frontmatter = "\n".join(new_lines)
    return f"---{chr(10)}{new_frontmatter}{chr(10)}---{chr(10)}{body.strip()}{chr(10)}"


def parse_and_proliferate_xml_notes(
    xml_file: Path,
    cresmo_wiki_dir: Path = DEFAULT_CRESMO_WIKI_DIR,
    force: bool = False,
) -> list[Path]:
    """Parses <xml><nota>...</nota></xml>, saves individual .md files into cresmo/wiki/<note_type>/, and updates _index.json."""
    if not xml_file.exists():
        return []

    xml_text = xml_file.read_text(encoding="utf-8")
    note_blocks = NOTA_XML_PATTERN.findall(xml_text)
    created_files = []

    index_file = cresmo_wiki_dir / INDEX_JSON_FILENAME
    index_data = {"notes": {}}
    if index_file.exists():
        try:
            index_data = json.loads(index_file.read_text(encoding="utf-8"))
            if "notes" not in index_data:
                index_data["notes"] = {}
        except Exception:
            index_data = {"notes": {}}

    for block in note_blocks:
        block = block.strip()
        if not block:
            continue

        # Strip CDATA tags if present
        block = CDATA_START_PATTERN.sub("", block)
        block = CDATA_END_PATTERN.sub("", block)
        block = block.replace("<![CDATA[", "").replace("]]>", "").strip()
        block = textwrap.dedent(block).strip()

        block = normalize_yaml_tags(block)

        # Clean H1 title in block if it has [[ ]]
        block = TITLE_H1_BRACKET_PATTERN.sub(r"# \1", block)

        # Extract title from # [Title] (allowing optional leading whitespace)
        title_match = TITLE_H1_PATTERN.search(block)
        note_title = title_match.group(1).strip() if title_match else DEFAULT_NOTE_TITLE
        note_title = BRACKETS_PATTERN.sub(r"\1", note_title).strip()
        clean_title = CLEAN_TITLE_SANITIZE_PATTERN.sub("", note_title).strip()

        # Extract type from frontmatter YAML
        type_match = TYPE_EXTRACT_PATTERN.search(block)
        note_type = type_match.group(1).lower().strip() if type_match else DEFAULT_NOTE_TYPE
        if note_type not in VALID_NOTE_TYPES:
            note_type = DEFAULT_NOTE_TYPE

        # Extract aliases from frontmatter YAML
        aliases = []
        aliases_match = ALIASES_EXTRACT_PATTERN.search(block)
        if aliases_match:
            aliases = [a.strip().strip("'\"") for a in aliases_match.group(1).split(",") if a.strip()]

        type_dir = cresmo_wiki_dir / note_type
        type_dir.mkdir(parents=True, exist_ok=True)

        note_file = type_dir / f"{clean_title}.md"

        # Non-destructive preservation: Only write if note does not exist, or force is True
        if not note_file.exists() or force:
            note_file.write_text(block, encoding="utf-8")
            created_files.append(note_file)
        else:
            print(f"  ℹ [Vault Match] '{clean_title}.md' already exists in vault -> preserved for Stage 5/6 incremental merging")

        # Update index entry
        rel_path = f"{note_type}/{clean_title}.md"
        existing_aliases = index_data["notes"].get(clean_title, {}).get("aliases", [])
        combined_aliases = sorted(list(set(existing_aliases + aliases)))
        index_data["notes"][clean_title] = {
            "type": note_type,
            "path": rel_path,
            "aliases": combined_aliases,
        }

    if len(created_files) > 0 or len(note_blocks) > 0:
        index_file.write_text(json.dumps(index_data, ensure_ascii=False, indent=2), encoding="utf-8")
        if created_files:
            print(f"  ✓ [Proliferation] Unpacked {len(created_files)} new atomic .md note(s) & updated {INDEX_JSON_FILENAME} in {cresmo_wiki_dir}")
        else:
            print(f"  ✓ [Proliferation] All {len(note_blocks)} note(s) already existed in vault & updated {INDEX_JSON_FILENAME}")

    return created_files


def execute_stage56_moc_manager(
    xml_file: Path,
    meta: dict,
    session_id: str,
    cresmo_dir: Path = DEFAULT_CRESMO_DIR,
    cresmo_wiki_dir: Path = DEFAULT_CRESMO_WIKI_DIR,
    force: bool = False,
    isolate_context: bool = True,
    restart_server: bool = False,
) -> Path:
    """Stage 5 & 6: MOC Management, Vault Graph Sync, & Reconciliation (cresmo-moc-manager)."""
    video_id = meta.get("video_id", xml_file.stem)
    reconciliation_log = xml_file.parent / f"{video_id}_reconciliation.md"
    index_file = cresmo_wiki_dir / INDEX_JSON_FILENAME

    # Skip if reconciliation log already exists — stages 5 & 6 are complete for this video.
    if not force and reconciliation_log.exists() and reconciliation_log.stat().st_size > MIN_RECONCILIATION_LOG_BYTES:
        return reconciliation_log

    skill_doc = SKILL_MOC_MANAGER_PATH.read_text(encoding="utf-8") if SKILL_MOC_MANAGER_PATH.exists() else ""
    xml_content = xml_file.read_text(encoding="utf-8") if xml_file.exists() else ""

    pre_prompt = (
        f"You are Cresmo MOC Manager. Reconcile the XML atomic notes into the Obsidian vault at '{cresmo_wiki_dir.resolve()}'.\n"
    )

    prompt = pre_prompt + (
        f"NOTE: All atomic notes and '{index_file.resolve()}' have ALREADY been unpacked and indexed by the pipeline.\n"
        f"Your tasks are:\n"
        f"1. Weave and integrate the new atomic notes into the relevant narrative Map of Content (MOC) under '{cresmo_wiki_dir.resolve()}/MOCs/' using file writing/editing tools.\n"
        f"2. FINAL STEP: Save the reconciliation report directly to: {reconciliation_log.resolve()} using write_to_file.\n"
        f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
        f"--- XML ATOMIC NOTES BATCH ---\n{xml_content}"
    )

    if isolate_context:
        clear_session_history(session_id, restart_server=restart_server)
        prompt = SENTINEL_PREFIX + prompt

    dispatch_time = time.time()
    send_agent_message(prompt, session_id)

    for _ in range(POLL_MAX_ATTEMPTS):
        if (
            reconciliation_log.exists()
            and reconciliation_log.stat().st_mtime >= (dispatch_time - POLL_DISPATCH_TIME_BUFFER)
            and reconciliation_log.stat().st_size > MIN_RECONCILIATION_LOG_BYTES
        ):
            print(f"  ✓ [Stage 5/6 Success] MOC reconciliation complete -> {reconciliation_log}")
            return reconciliation_log
        time.sleep(POLL_SLEEP_SECONDS)

    # Fallback report generation if agent log write pending
    reconciliation_log.write_text(
        f"# Cresmo MOC Reconciliation Report - {video_id}\n\n"
        f"- **Channel**: {meta.get('channel_name')}\n"
        f"- **Video ID**: {video_id}\n"
        f"- **Timestamp**: {time.strftime(DATETIME_FORMAT)}\n"
        f"- **Status**: Atomic notes proliferated into `{cresmo_wiki_dir}`.\n",
        encoding="utf-8",
    )
    return reconciliation_log


def format_duration(seconds: float | int) -> str:
    """Format seconds into HHhMMmSSs string."""
    sec = max(0, int(seconds))
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}h{m:02d}m{s:02d}s"
    elif m > 0:
        return f"{m:02d}m{s:02d}s"
    else:
        return f"{s:02d}s"


def process_candidate_blocks(
    candidate_blocks: list[dict],
    session_id: str,
    enriched_dir: Path,
    cresmo_dir: Path,
    cresmo_wiki_dir: Path,
    force: bool = False,
    isolate_context: bool = True,
    restart_server: bool = False,
) -> None:
    """Iterate through candidate blocks and execute Stages 2 through 6 for each video."""
    total_candidates = len(candidate_blocks)
    pipeline_start_time = time.time()

    for idx, block in enumerate(candidate_blocks, 1):
        meta = block.get("metadata", {})
        txt_file_raw = block.get("source_file")
        if not txt_file_raw:
            continue
        txt_file = Path(txt_file_raw)
        video_id = meta.get("video_id", DEFAULT_VIDEO_ID)
        channel = meta.get("channel_name", DEFAULT_CHANNEL_NAME)
        domain, cat_type = classify_channel(channel)

        pct = (idx / total_candidates) * 100
        elapsed = time.time() - pipeline_start_time
        if idx > 1:
            avg_time = elapsed / (idx - 1)
            remaining = avg_time * (total_candidates - idx + 1)
            total_est = elapsed + remaining
            eta_str = f"{format_duration(elapsed)} + {format_duration(remaining)} = {format_duration(total_est)}"
        else:
            eta_str = "0h00m00s"

        print(f"[{idx}/{total_candidates}] ({pct:.1f}% | ETA: {eta_str}) [{domain.upper()}/{cat_type.upper()}] Channel: '{channel}' | Video: {video_id} ({meta.get('video_title', '')[:30]}...)")

        # Derive the completion sentinel path (written only after stage 6 finishes).
        # If it exists, this video was fully processed end-to-end — skip stages 3-6.
        xml_file = enriched_dir / channel / f"{video_id}.xml"
        reconciliation_log = xml_file.parent / f"{video_id}_reconciliation.md"
        if not force and reconciliation_log.exists() and reconciliation_log.stat().st_size > MIN_RECONCILIATION_LOG_BYTES:
            print(f"  ✓ [Full Skip] Already processed end-to-end -> {reconciliation_log}\n")
            continue

        # Stage 2: Expander & Detranscriptor
        enriched_file = execute_stage2_expander(
            txt_file,
            meta,
            session_id,
            output_dir=enriched_dir,
            force=force,
            isolate_context=isolate_context,
            restart_server=restart_server,
        )

        # Stage 3 & 4: Atomic Generator & Proliferation
        xml_file, is_newly_generated = execute_stage3_atomic_notes(
            enriched_file,
            meta,
            session_id,
            cresmo_dir=cresmo_dir,
            force=force,
            isolate_context=isolate_context,
            restart_server=restart_server,
        )
        if is_newly_generated:
            parse_and_proliferate_xml_notes(xml_file, cresmo_wiki_dir=cresmo_wiki_dir, force=force)
        else:
            pass
            # print(f"  ℹ [Stage 4 Skip] XML already exists/cached ({xml_file.name}) -> skipping file proliferation to protect vault")

        # Stage 5 & 6: MOC Manager & Graph Reconciliation
        execute_stage56_moc_manager(
            xml_file,
            meta,
            session_id,
            cresmo_dir=cresmo_dir,
            cresmo_wiki_dir=cresmo_wiki_dir,
            force=force,
            isolate_context=isolate_context,
            restart_server=restart_server,
        )

        # Mark completed in processed_cresmo.json
        save_processed_cresmo_log(video_id, metadata=meta, log_path=PROCESSED_CRESMO_LOG)
        print(f"  ✓ Finished video_id: {video_id}\n")


# ==============================================================================
# MASTER PIPELINE ENTRYPOINT
# ==============================================================================

def run_cresmo_pipeline(
    raw_dir: Path = DEFAULT_RAW_DIR,
    enriched_dir: Path = DEFAULT_ENRICHED_DIR,
    cresmo_dir: Path = DEFAULT_CRESMO_DIR,
    limit: int | None = None,
    force: bool = False,
    isolate_context: bool = True,
    restart_server: bool = False,
    categories: list[str] | set[str] | None = None,
) -> None:
    """Execute complete Cresmo pipeline across Stages 2 through 6."""
    cresmo_wiki_dir = cresmo_dir / "wiki"
    cresmo_wiki_dir.mkdir(parents=True, exist_ok=True)
    processed_log = load_processed_cresmo_log(PROCESSED_CRESMO_LOG)

    # Normalize allowed categories filter (default to politics_br, tech_ai)
    active_categories = categories if categories is not None else list(DEFAULT_CATEGORIES)
    allowed_categories: set[str] = set()
    for cat in active_categories:
        if isinstance(cat, str):
            for item in cat.split(","):
                clean = item.strip().lower()
                if clean:
                    allowed_categories.add(clean)

    # If user passed 'all' or '*', disable filtering to process all categories
    if "all" in allowed_categories or "*" in allowed_categories:
        allowed_categories.clear()

    print("==================================================")
    print("🧠 Cresmo Master Pipeline (Stages 2 -> 6)")
    print(f"   Raw Directory:      {raw_dir}")
    print(f"   Enriched Directory: {enriched_dir}")
    print(f"   Cresmo Vault:       {cresmo_wiki_dir}")
    print(f"   Processed Log:      {PROCESSED_CRESMO_LOG.name} ({len(processed_log)} items completed)")
    print(f"   Category Filter:    {', '.join(sorted(allowed_categories)) if allowed_categories else 'All Categories'}")
    print(f"   Isolate Context:    {isolate_context}")
    print(f"   Restart Server:     {restart_server}")
    print("==================================================")

    # 1. Discover raw transcript files
    txt_files = sorted(raw_dir.rglob("*.txt"))

    candidate_blocks = []
    total_txt = len(txt_files)
    parse_start_time = time.time()
    last_parse_pct = -1

    for txt_idx, txt_file in enumerate(txt_files, 1):
        if txt_idx > MAX_CANDIDATE_PARSE_LIMIT:
            print(f"breaking at {MAX_CANDIDATE_PARSE_LIMIT} records")
            break
        blocks = parse_merged_transcriptions(txt_file)
        for b in blocks:
            b["source_file"] = txt_file
            meta = b.get("metadata", {})
            video_id = meta.get("video_id")
            if not video_id:
                m = YT_ID_PATTERN.match(txt_file.stem)
                video_id = m.group(1) if m else txt_file.stem
                meta["video_id"] = video_id

            if not force and video_id in processed_log:
                continue

            channel = meta.get("channel_name", DEFAULT_CHANNEL_NAME)
            domain, cat_type = classify_channel(channel)
            meta["domain"] = domain
            meta["category_type"] = cat_type

            if allowed_categories:
                if domain.lower() not in allowed_categories and cat_type.lower() not in allowed_categories:
                    continue

            candidate_blocks.append(b)

        if total_txt > 0:
            parse_pct = int((txt_idx / total_txt) * 100)
            if parse_pct > last_parse_pct:
                last_parse_pct = parse_pct
                elapsed = time.time() - parse_start_time
                avg_time = elapsed / txt_idx if txt_idx > 0 else 0
                remaining = avg_time * (total_txt - txt_idx)
                total_est = elapsed + remaining
                eta_str = f"{format_duration(elapsed)} + {format_duration(remaining)} = {format_duration(total_est)}"
                print(f"{txt_idx}/{total_txt} ({parse_pct}%) | {eta_str}", end="\n", flush=True)

    if limit:
        candidate_blocks = candidate_blocks[:limit]
        print(f"ℹ️ Limiting pipeline run to first {limit} video block(s).")

    if not candidate_blocks:
        print("✓ All transcripts are up to date! Nothing to process.")
        return

    session_id = resolve_active_session()
    print(f"🔗 Active Agent Session: {session_id[:]}...\n")

    process_candidate_blocks(
        candidate_blocks=candidate_blocks,
        session_id=session_id,
        enriched_dir=enriched_dir,
        cresmo_dir=cresmo_dir,
        cresmo_wiki_dir=cresmo_wiki_dir,
        force=force,
        isolate_context=isolate_context,
        restart_server=restart_server,
    )

    print("🎉 Cresmo Pipeline Execution Complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cresmo Pipeline Master Entrypoint (Stages 2 -> 6)")
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Path to raw transcriptions directory")
    parser.add_argument("--enriched-dir", default=str(DEFAULT_ENRICHED_DIR), help="Path to enriched output directory")
    parser.add_argument("--cresmo-dir", default=str(DEFAULT_CRESMO_DIR), help="Path to Cresmo vault root directory")
    parser.add_argument(
        "--category", "--categories", "-c",
        dest="categories",
        nargs="+",
        default=list(DEFAULT_CATEGORIES),
        help="Filter videos by category (default: 'politics_br,tech_ai'. Use 'all' for all categories)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of videos to process")
    parser.add_argument("--force", "-f", action="store_true", help="Force re-processing of completed videos")
    parser.add_argument(
        "--isolate-context",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Purge session transcript and message history before each dispatch to isolate context (default: True)",
    )
    parser.add_argument(
        "--restart-server",
        action="store_true",
        default=False,
        help="Restart Language Server process before each dispatch to isolate context (default: False)",
    )

    args = parser.parse_args()

    run_cresmo_pipeline(
        raw_dir=Path(args.raw_dir),
        enriched_dir=Path(args.enriched_dir),
        cresmo_dir=Path(args.cresmo_dir),
        categories=args.categories,
        limit=args.limit,
        force=args.force,
        isolate_context=args.isolate_context,
        restart_server=args.restart_server,
    )
