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
import datetime
import json
from pathlib import Path
import re
import sys
import textwrap
import time

from typing import Callable

# Ensure script directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from cresmo_shared import (
    BRAIN_DIR,
    DATETIME_FORMAT,
    DEFAULT_CATEGORIES,
    DEFAULT_CRESMO_DIR,
    DEFAULT_CRESMO_WIKI_DIR,
    DEFAULT_ENRICHED_DIR,
    DEFAULT_PLAYLIST_PRIORITY_FILE,
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
    read_priority_entries,
    read_priority_video_ids,
    resolve_active_session,
    sanitize_untrusted_content,
    save_processed_cresmo_log,
    scan_session_for_quota_refresh,
    send_agent_message,
)

# --- Polling & Timing Defaults ---
DEFAULT_TRAJECTORY_TIMEOUT_SECONDS: int = 15
POLL_MAX_ATTEMPTS: int = 300
POLL_SLEEP_SECONDS: float = 1.0
POLL_DISPATCH_TIME_BUFFER: float = 1.0
POLL_FALLBACK_INTERVAL: int = 30


# --- Payload & File Size Thresholds ---
DEFAULT_STAGE2_PASSES: int = 3
PROMPT_MAX_BYTES_INLINE: int = 120_000
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
    "and REMOVE ALL DIAGRAMS/ASCII ART/TABLES/BULLET LISTS/YAML. Produce continuous fluid Markdown prose.\n"
)
STAGE2_V2_PROMPT_TASK: str = (
    "You are Cresmo Expander (Re-Expansion, Epistemic, Dialectical & Theoretical Densification and Definitive Compendium Polish & Synthesis). \n"
    "This is your most important task: Take the previous-pass enriched Markdown document. \n"
    "Purge any remaining oralities, bullet lists, tables, diagrams and YAML metadata. Produce continuous fluid Markdown prose.\n"
    "Perform exhaustive Socratic gap filling, add robust empirical context, quantify claims with exact historical/statistical grounding, and refine causal relationships (historical-scientific genealogy mapping, verifying causal mechanisms, enriching empirical facts and footnotes).\n"
    "Deepen theoretical frameworks, map counter-arguments, sharpen conceptual nuances, and ensure rigorous semantic density throughout the prose and footnotes.\n"
    "Synthesize all historical, empirical, and conceptual threads into a definitive encyclopedic compendium of the highest stylistic and academic rigor.\n"
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
# QUOTA & STRUCTURAL VALIDATORS
# ==============================================================================

def _is_quota_reached(session_id: str) -> bool:
    """Check if the agent session hit a baseline quota wall and block until refresh.

    Returns True if quota was exhausted (caller should re-dispatch), False otherwise.
    """
    quota_refresh = scan_session_for_quota_refresh(session_id)
    if not quota_refresh:
        return False
    _wait_for_quota_refresh(quota_refresh)
    clear_session_history(session_id)
    return True


def is_valid_enriched_markdown(file_path: Path, min_bytes: int = MIN_VALID_OUTPUT_BYTES) -> bool:
    """Validate that the enriched markdown document meets cresmo-expander structural standards.

    Checks that the file exists, has a minimum byte size, contains markdown section headers,
    and includes the mandatory closing complementary information section without premature truncation.
    """
    if not file_path.exists():
        return False
    try:
        if file_path.stat().st_size < min_bytes:
            return False
        content = file_path.read_text(encoding="utf-8").strip()
        if len(content) < min_bytes:
            return False
        # Must contain major section header (# or ##)
        has_header = TAG_MARKDOWN_H2 in content or "\n# " in content or content.startswith("# ")
        # Must contain the mandatory complementary info section
        has_complementary = (
            TAG_COMPLEMENTARY_INFO in content
            or "Informações Complementares" in content
            or "Informacoes Complementares" in content
            or "Complementary Information" in content
        )
        return has_header and has_complementary
    except Exception:
        return False


def is_valid_atomic_xml(file_path: Path, min_bytes: int = MIN_VALID_OUTPUT_BYTES) -> bool:
    """Validate that atomic XML contains properly delimited note tags."""
    if not file_path.exists():
        return False
    try:
        if file_path.stat().st_size < min_bytes:
            return False
        content = file_path.read_text(encoding="utf-8").strip()
        has_xml_tags = (TAG_XML_OPEN in content and TAG_XML_CLOSE in content) or (
            "<notas>" in content and "</notas>" in content
        )
        has_nota = "<nota>" in content and "</nota>" in content
        return (has_xml_tags or has_nota) and len(content) >= min_bytes
    except Exception:
        return False


def is_valid_reconciliation_log(file_path: Path, min_bytes: int = MIN_RECONCILIATION_LOG_BYTES) -> bool:
    """Validate that reconciliation log file is generated and non-empty."""
    if not file_path.exists():
        return False
    try:
        return file_path.stat().st_size >= min_bytes
    except Exception:
        return False


# ==============================================================================
# PIPELINE STAGES
# ==============================================================================

def execute_stage2_expander(
    txt_file: Path,
    meta: dict,
    session_id: str,
    output_dir: Path = DEFAULT_ENRICHED_DIR,
    total_passes: int = DEFAULT_STAGE2_PASSES,
    force: bool = False,
    isolate_context: bool = True,
    restart_server: bool = False,
) -> Path:
    """Stage 2: Progressive Pre-processing and Multi-Pass Enrichment (cresmo-expander).

    Reads the raw transcript from `raw/` and iteratively expands and enriches it
    directly into a single canonical Markdown file in `enriched/`:
    `playground/cresmo/enriched/[Channel_Name]/[Video_ID].md`.
    Stage 2 output is saved in the enriched directory and NEVER in the raw directory.
    """
    channel_name = meta.get("channel_name", DEFAULT_CHANNEL_NAME)
    video_id = meta.get("video_id", txt_file.stem)

    # Target directory is strictly within enriched/
    channel_dir = output_dir / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    enriched_file = channel_dir / f"{video_id}.md"

    if not force and is_valid_enriched_markdown(enriched_file, MIN_ENRICHED_EXISTING_BYTES):
        return enriched_file

    with open(txt_file, "r", encoding="utf-8") as f:
        raw_text = f.read().strip()

    skill_doc = SKILL_EXPANDER_PATH.read_text(encoding="utf-8") if SKILL_EXPANDER_PATH.exists() else ""

    current_text = raw_text

    for pass_num in range(1, total_passes + 1):
        task_prompt = STAGE2_PROMPT_TASK if pass_num == 1 else STAGE2_V2_PROMPT_TASK

        pass_label = f"Pass {pass_num}/{total_passes}" if total_passes > 1 else "Pass 1"
        if pass_num == 1:
            safe_raw = sanitize_untrusted_content(raw_text, source_label=txt_file.name)
            header_context = (
                f"--- ORIGINAL RAW TRANSCRIPT METADATA & TEXT (GROUND TRUTH) ---\n"
                f"File: {txt_file.name}\n"
                f"{safe_raw}"
            )
        else:
            safe_raw = sanitize_untrusted_content(raw_text, source_label=txt_file.name)
            safe_current = sanitize_untrusted_content(current_text, source_label=f"{enriched_file.name} (pass {pass_num - 1})")
            header_context = (
                f"--- ORIGINAL RAW TRANSCRIPT (GROUND TRUTH REFERENCE) ---\n"
                f"File: {txt_file.name}\n"
                f"{safe_raw}\n\n"
                f"--- PREVIOUS PASS EXPANDED COMPENDIUM DRAFT (PASS {pass_num - 1} TO ENRICH & DEEPEN) ---\n"
                f"File: {enriched_file.name}\n"
                f"{safe_current}"
            )

        prompt = task_prompt + (
            f"Save output directly to enriched file: {enriched_file.resolve()}\n\n"
            f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
            f"{header_context}"
        )

        if len(prompt.encode("utf-8")) > PROMPT_MAX_BYTES_INLINE:
            if pass_num == 1:
                input_desc = f"Input raw transcript file: {txt_file.resolve()}\n"
            else:
                input_desc = (
                    f"Input raw transcript reference: {txt_file.resolve()}\n"
                    f"Input previous-pass enriched text to expand: {enriched_file.resolve()}\n"
                )
            prompt = task_prompt + (
                f"Save output directly to enriched file: {enriched_file.resolve()}\n"
                f"{input_desc}"
                f"Skill specification: {SKILL_EXPANDER_PATH.resolve()}\n"
                f"Please read the input text(s), run cresmo-expander {pass_label}, and write the output directly to {enriched_file.resolve()} in the enriched directory (never in raw)."
            )

        if isolate_context:
            # Context isolation and Sentinel reset are strictly applied to Pass 1.
            # Passes > 1 must retain conversational continuity to enable progressive enrichment
            # without triggering an adversarial context-reset prompt instruction.
            if pass_num == 1:
                clear_session_history(session_id, restart_server=restart_server)
                prompt = SENTINEL_PREFIX + prompt

        dispatch_time = time.time()
        send_agent_message(prompt, session_id)

        pass_completed = False
        # Poll for Option A direct file write with periodic Option B trajectory fallback
        for attempt in range(1, POLL_MAX_ATTEMPTS + 1):
            if (
                enriched_file.exists()
                and enriched_file.stat().st_mtime >= (dispatch_time - POLL_DISPATCH_TIME_BUFFER)
                and is_valid_enriched_markdown(enriched_file, MIN_VALID_OUTPUT_BYTES)
            ):
                print(f"  ✓ [Stage 2 {pass_label} Success] Enriched text updated -> {enriched_file}")
                pass_completed = True
                break

            # Option B: Periodic check for agent textual completion in trajectory every 30 attempts
            if attempt % POLL_FALLBACK_INTERVAL == 0:
                content = fetch_trajectory_response(session_id, TAG_MARKDOWN_H2, TAG_COMPLEMENTARY_INFO)
                if content and (TAG_COMPLEMENTARY_INFO in content or len(content) >= MIN_VALID_OUTPUT_BYTES):
                    enriched_file.write_text(content, encoding="utf-8")
                    print(f"  ✓ [Stage 2 {pass_label} Fast Fallback Success] Saved enriched text -> {enriched_file}")
                    pass_completed = True
                    break

            if _is_quota_reached(session_id):
                dispatch_time = time.time()
                send_agent_message(prompt, session_id)
            time.sleep(POLL_SLEEP_SECONDS)

        if not pass_completed:
            # Fallback Option B
            content = fetch_trajectory_response(session_id, TAG_MARKDOWN_H2, TAG_COMPLEMENTARY_INFO)
            if content and (TAG_COMPLEMENTARY_INFO in content or len(content) >= MIN_VALID_OUTPUT_BYTES):
                enriched_file.write_text(content, encoding="utf-8")
                print(f"  ✓ [Stage 2 {pass_label} Fallback Success] Saved enriched text -> {enriched_file}")
                pass_completed = True
            elif pass_num == 1 and not enriched_file.exists():
                # Fallback Option C: Write current text if file was not generated by agent
                enriched_file.write_text(current_text, encoding="utf-8")
                print(f"  ✓ [Stage 2 {pass_label} Fallback] Saved current text -> {enriched_file}")

        # Update current_text for next pass
        if enriched_file.exists():
            current_text = enriched_file.read_text(encoding="utf-8").strip()

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

    if not force and is_valid_atomic_xml(xml_output_file, MIN_VALID_OUTPUT_BYTES):
        return xml_output_file, False

    if not enriched_file.exists():
        return xml_output_file, False

    enriched_text = enriched_file.read_text(encoding="utf-8")
    skill_doc = SKILL_ATOMIC_PATH.read_text(encoding="utf-8") if SKILL_ATOMIC_PATH.exists() else ""
    safe_enriched = sanitize_untrusted_content(enriched_text, source_label=enriched_file.name)

    prompt = STAGE3_PRE_PROMPT + (
        f"Source metadata: channel_name='{meta.get('channel_name')}', video_id='{video_id}'\n"
        f"Save output directly to file: {xml_output_file.resolve()}\n\n"
        f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
        f"--- ENRICHED TEXT ---\n{safe_enriched}"
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

    # Poll for Option A direct file write with periodic Option B trajectory fallback
    for attempt in range(1, POLL_MAX_ATTEMPTS + 1):
        if (
            xml_output_file.exists()
            and xml_output_file.stat().st_mtime >= (dispatch_time - POLL_DISPATCH_TIME_BUFFER)
            and is_valid_atomic_xml(xml_output_file, MIN_VALID_OUTPUT_BYTES)
        ):
            print(f"  ✓ [Stage 3 Success] Atomic XML generated -> {xml_output_file}")
            return xml_output_file, True

        # Option B: Periodic check for agent textual completion in trajectory every 30 attempts
        if attempt % POLL_FALLBACK_INTERVAL == 0:
            content = fetch_trajectory_response(session_id, TAG_XML_OPEN, TAG_XML_CLOSE)
            if content:
                xml_output_file.write_text(content, encoding="utf-8")
                print(f"  ✓ [Stage 3 Fast Fallback Success] Saved Atomic XML -> {xml_output_file}")
                return xml_output_file, True

        if _is_quota_reached(session_id):
            dispatch_time = time.time()
            send_agent_message(prompt, session_id)
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
    if not force and is_valid_reconciliation_log(reconciliation_log, MIN_RECONCILIATION_LOG_BYTES):
        return reconciliation_log

    skill_doc = SKILL_MOC_MANAGER_PATH.read_text(encoding="utf-8") if SKILL_MOC_MANAGER_PATH.exists() else ""
    xml_content = xml_file.read_text(encoding="utf-8") if xml_file.exists() else ""
    safe_xml = sanitize_untrusted_content(xml_content, source_label=xml_file.name)

    pre_prompt = (
        f"You are Cresmo MOC Manager. Reconcile the XML atomic notes into the Obsidian vault at '{cresmo_wiki_dir.resolve()}'.\n"
    )

    prompt = pre_prompt + (
        f"NOTE: All atomic notes and '{index_file.resolve()}' have ALREADY been unpacked and indexed by the pipeline.\n"
        f"Your tasks are:\n"
        f"1. Weave and integrate the new atomic notes into the relevant narrative Map of Content (MOC) under '{cresmo_wiki_dir.resolve()}/MOCs/' using file writing/editing tools.\n"
        f"2. FINAL STEP: Save the reconciliation report directly to: {reconciliation_log.resolve()} using write_to_file.\n"
        f"--- SKILL SPECIFICATION ---\n{skill_doc}\n\n"
        f"--- XML ATOMIC NOTES BATCH ---\n{safe_xml}"
    )

    if isolate_context:
        clear_session_history(session_id, restart_server=restart_server)
        prompt = SENTINEL_PREFIX + prompt


    dispatch_time = time.time()
    send_agent_message(prompt, session_id)

    # Poll for reconciliation log file write
    for _ in range(POLL_MAX_ATTEMPTS):
        if (
            reconciliation_log.exists()
            and reconciliation_log.stat().st_mtime >= (dispatch_time - POLL_DISPATCH_TIME_BUFFER)
            and is_valid_reconciliation_log(reconciliation_log, MIN_RECONCILIATION_LOG_BYTES)
        ):
            print(f"  ✓ [Stage 5/6 Success] MOC reconciliation complete -> {reconciliation_log}")
            return reconciliation_log
        if _is_quota_reached(session_id):
            dispatch_time = time.time()
            send_agent_message(prompt, session_id)
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


def _wait_for_quota_refresh(refresh_time: datetime.datetime) -> None:
    """Block pipeline execution until the API baseline quota refresh time.

    Adds a 30-second safety buffer beyond the declared refresh deadline to
    account for clock skew between local time and the Antigravity API server.
    Prints a progress heartbeat every 60 seconds so the terminal does not appear
    frozen during long waits.

    Args:
        refresh_time: The datetime at which the Antigravity quota is expected
            to refresh, as parsed from the rate-limit message.
    """
    now = datetime.datetime.now()
    # Add 30-second safety buffer beyond the declared refresh deadline
    safety_buffer = 30
    wait_seconds = max(0.0, (refresh_time - now).total_seconds() + safety_buffer)
    print(f"\n⏸  [QUOTA PAUSE] Baseline quota exhausted.")
    print(f"    Current time:     {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    Refresh at:       {refresh_time.strftime('%Y-%m-%d %H:%M:%S')}")

    remaining = wait_seconds
    while remaining > 0:
        print(f"\r    Quota resume in:  {format_duration(remaining)}...    ", end="", flush=True)
        interval = min(1.0, remaining)
        time.sleep(interval)
        remaining -= interval

    print(f"  ✓ [QUOTA RESUME] Quota refreshed at {datetime.datetime.now().strftime('%H:%M:%S')} — resuming pipeline.\n")


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
        # Stage 2: Expander & Detranscriptor (5 progressive in-place passes)
        enriched_file = execute_stage2_expander(
            txt_file,
            meta,
            session_id,
            output_dir=enriched_dir,
            total_passes=DEFAULT_STAGE2_PASSES,
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
        # Idempotently unpack atomic notes and update _index.json (preserves existing notes unless force=True)
        parse_and_proliferate_xml_notes(xml_file, cresmo_wiki_dir=cresmo_wiki_dir, force=force)

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


def sync_missing_priority_video(video_id: str, url: str, raw_dir: Path) -> Path | None:
    """Perform on-demand single-video ingestion using sync_single_video."""
    try:
        isb_dir = Path(__file__).resolve().parent.parent / "isb.ai"
        if isb_dir.exists() and str(isb_dir) not in sys.path:
            sys.path.insert(0, str(isb_dir))

        import sync_channels
        from cresmo_shared import DEFAULT_COOKIES_FILE
        from export_cookies import ensure_cookies

        ensure_cookies(output_file=DEFAULT_COOKIES_FILE, verbose=False)
        print(f"  ⬇️ [Priority Auto-Sync] Ingesting raw transcript on-demand for video_id: '{video_id}' ({url})...")
        res = sync_channels.sync_single_video(
            url=url,
            output_dir=raw_dir,
            model_name="base",
            keep_audio=False,
        )
        if not res or not res.get("video_id"):
            return None

        matched = list(raw_dir.glob(f"**/*{video_id}*.txt"))
        return matched[0] if matched else None
    except Exception as e:
        print(f"  ❌ [Priority Auto-Sync Error] Failed to ingest {video_id}: {e}")
        return None


def resolve_priority_blocks(
    priority_ids: list[str] | list[dict[str, str]],
    raw_dir: Path,
    processed_log: set[str] | dict,
    force: bool = False,
    auto_sync: bool = True,
    syncer: Callable[[str, str, Path], Path | None] | None = None,
) -> list[dict]:
    """Resolve candidate blocks for priority video IDs directly via fast-path disk lookup,
    optionally triggering on-demand auto-sync for missing transcripts.
    """
    priority_blocks: list[dict] = []
    if not priority_ids:
        return priority_blocks

    effective_syncer = syncer if syncer is not None else sync_missing_priority_video

    for item in priority_ids:
        if isinstance(item, dict):
            vid = item.get("video_id", "")
            url = item.get("url") or f"https://www.youtube.com/watch?v={vid}"
        else:
            vid = item.strip()
            url = f"https://www.youtube.com/watch?v={vid}"

        if not vid:
            continue

        if not force and vid in processed_log:
            continue

        matched_files = list(raw_dir.glob(f"**/*{vid}*.txt"))

        # If missing from raw/ and auto_sync is enabled, attempt on-demand ingestion
        if not matched_files and auto_sync:
            synced_file = effective_syncer(vid, url, raw_dir)
            if synced_file and synced_file.exists():
                matched_files = [synced_file]

        block_found = False
        for txt_file in matched_files:
            blocks = parse_merged_transcriptions(txt_file)
            for b in blocks:
                b["source_file"] = txt_file
                meta = b.get("metadata", {})
                block_vid = meta.get("video_id")
                if not block_vid:
                    m = YT_ID_PATTERN.match(txt_file.stem)
                    block_vid = m.group(1) if m else txt_file.stem
                    meta["video_id"] = block_vid

                if block_vid == vid:
                    channel = meta.get("channel_name", DEFAULT_CHANNEL_NAME)
                    domain, cat_type = classify_channel(channel)
                    meta["domain"] = domain
                    meta["category_type"] = cat_type
                    priority_blocks.append(b)
                    block_found = True
                    break
            if block_found:
                break

        if not block_found:
            print(f"  ⚠️ [Priority Fast-Path] Raw transcript not found for video_id: '{vid}'")

    return priority_blocks


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
    priority_playlist: Path | None = DEFAULT_PLAYLIST_PRIORITY_FILE,
    auto_sync: bool = True,
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

    priority_entries: list[dict[str, str]] = []
    if priority_playlist:
        priority_entries = read_priority_entries(Path(priority_playlist))

    priority_blocks: list[dict] = []
    if priority_entries:
        priority_blocks = resolve_priority_blocks(
            priority_ids=priority_entries,
            raw_dir=raw_dir,
            processed_log=processed_log,
            force=force,
            auto_sync=auto_sync,
        )

    priority_vids = {e["video_id"] for e in priority_entries}
    handled_priority_vids = {
        b.get("metadata", {}).get("video_id") for b in priority_blocks
    } | priority_vids

    print("==================================================")
    print("🧠 Cresmo Master Pipeline (Stages 2 -> 6)")
    print(f"   Raw Directory:      {raw_dir}")
    print(f"   Enriched Directory: {enriched_dir}")
    print(f"   Cresmo Vault:       {cresmo_wiki_dir}")
    print(f"   Processed Log:      {PROCESSED_CRESMO_LOG.name} ({len(processed_log)} items completed)")
    print(f"   Category Filter:    {', '.join(sorted(allowed_categories)) if allowed_categories else 'All Categories'}")
    if priority_entries:
        playlist_name = Path(priority_playlist).name if priority_playlist else "none"
        print(f"   Priority Queue:     {len(priority_blocks)}/{len(priority_entries)} resolved from {playlist_name}")
    print(f"   Auto-Sync On-Demand:{auto_sync}")
    print(f"   Isolate Context:    {isolate_context}")
    print(f"   Restart Server:     {restart_server}")
    print("==================================================")

    # 1. Discover raw transcript files (fail-fast category filtering at directory level)
    if allowed_categories:
        channel_dirs = [d for d in raw_dir.iterdir() if d.is_dir()]
        allowed_dirs = [
            d for d in channel_dirs
            if classify_channel(d.name)[0].lower() in allowed_categories
            or classify_channel(d.name)[1].lower() in allowed_categories
        ]
        txt_files = []
        for d in allowed_dirs:
            txt_files.extend(d.rglob("*.txt"))
        for f in raw_dir.glob("*.txt"):
            txt_files.append(f)
        txt_files.sort()
    else:
        txt_files = sorted(raw_dir.rglob("*.txt"))

    candidate_blocks = []
    total_txt = len(txt_files)
    parse_start_time = time.time()
    last_parse_pct = -1
    target_blocks_limit = limit if (limit is not None and limit > 0) else MAX_CANDIDATE_PARSE_LIMIT

    for txt_idx, txt_file in enumerate(txt_files, 1):
        # Fail fast per-file on allowed categories before parsing content
        rel_parts = txt_file.relative_to(raw_dir).parts
        if allowed_categories and len(rel_parts) > 1:
            folder_domain, folder_cat_type = classify_channel(rel_parts[0])
            if folder_domain.lower() not in allowed_categories and folder_cat_type.lower() not in allowed_categories:
                continue

        blocks = parse_merged_transcriptions(txt_file)
        for b in blocks:
            b["source_file"] = txt_file
            meta = b.get("metadata", {})
            video_id = meta.get("video_id")
            if not video_id:
                m = YT_ID_PATTERN.match(txt_file.stem)
                video_id = m.group(1) if m else txt_file.stem
                meta["video_id"] = video_id

            if video_id in handled_priority_vids:
                continue

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
            if target_blocks_limit and len(candidate_blocks) >= target_blocks_limit:
                break

        if total_txt > 0:
            parse_pct = int((txt_idx / total_txt) * 100)
            if parse_pct > last_parse_pct:
                last_parse_pct = parse_pct
                elapsed = time.time() - parse_start_time
                avg_time = elapsed / txt_idx if txt_idx > 0 else 0
                remaining = avg_time * (total_txt - txt_idx)
                total_est = elapsed + remaining
                eta_str = f"{format_duration(elapsed)} + {format_duration(remaining)} = {format_duration(total_est)}"
                print(f"{txt_idx}/{total_txt} ({parse_pct}%) | Candidates: {len(candidate_blocks)} | {eta_str}", end="\n", flush=True)

        if target_blocks_limit and len(candidate_blocks) >= target_blocks_limit:
            print(f"breaking at {len(candidate_blocks)} candidate blocks")
            break

    candidate_blocks = priority_blocks + candidate_blocks

    if limit:
        candidate_blocks = candidate_blocks[:limit]
        print(f"ℹ️ Limiting pipeline run to first {limit} video block(s).")
    elif MAX_CANDIDATE_PARSE_LIMIT and len(candidate_blocks) >= MAX_CANDIDATE_PARSE_LIMIT:
        candidate_blocks = candidate_blocks[:MAX_CANDIDATE_PARSE_LIMIT]
        print(f"ℹ️ Limiting candidate blocks to {MAX_CANDIDATE_PARSE_LIMIT} records.")

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
    parser.add_argument(
        "--priority-playlist",
        default=str(DEFAULT_PLAYLIST_PRIORITY_FILE),
        help="Path to priority playlist text file (default: playground/cresmo/playlist-priority.txt)",
    )
    parser.add_argument(
        "--auto-sync",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Automatically download/transcribe missing priority videos on-demand (default: True)",
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
        priority_playlist=Path(args.priority_playlist) if args.priority_playlist else None,
        auto_sync=args.auto_sync,
    )
