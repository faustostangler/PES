#!/usr/bin/env python3
"""Index raw transcript files using local Ollama LLM into paratactic CSV summaries with standardized PES ETA logging."""

import argparse
import atexit
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# --- Config defaults ---
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "phi3:mini"
DEFAULT_RAW_DIR = Path(__file__).resolve().parent / "raw"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent
MAX_TRANSCRIPT_CHARS = 2500

SYSTEM_PROMPT = """Act as a domain expert in conceptual synthesis.
Analyze the provided title and transcript excerpt.
Output EXACTLY ONE LINE in this format (no markdown, no quotes, no extra words):
<Key Concept (2 to 4 words)>, <One sentence synthesis in Original Language>

Style guidelines:
- Use parataxis, direct and swift word order, single and self-contained clauses.
- Use asyndetic juxtaposition of ideas, rapid and incisive rhythm.
- Aim for syntactic clarity and an exoteric, crystalline style where form is an invisible medium.

Example:
Geometria Latente CLIP, Modelos de difusão acoplados à arquitetura CLIP sintetizam imagens alinhando representações vetoriais textuais e visuais em espaços latentes de alta dimensão regidos por processos estocásticos reversos.
"""


def format_duration(seconds: float) -> str:
    """Format duration in seconds to xxhxxmxxs (e.g. 02h14m45s) matching PES standard.

    >>> format_duration(15)
    '00h00m15s'
    >>> format_duration(95)
    '00h01m35s'
    >>> format_duration(3665)
    '01h01m05s'
    """
    secs = int(max(0, round(seconds)))
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    remaining_secs = secs % 60
    return f"{hours:02d}h{minutes:02d}m{remaining_secs:02d}s"


def format_time_block(elapsed: float, eta_sec: float | None) -> str:
    """Format time block as 'elapsed+estimated = total' matching PES standard.

    >>> format_time_block(60, 120)
    '00h01m00s+00h02m00s = 00h03m00s'
    >>> format_time_block(60, None)
    '00h01m00s+--h--m--s = --h--m--s'
    """
    elapsed_str = format_duration(elapsed)
    if eta_sec is not None and eta_sec >= 0:
        eta_str = format_duration(eta_sec)
        total_time_str = format_duration(elapsed + eta_sec)
        return f"{elapsed_str}+{eta_str} = {total_time_str}"
    return f"{elapsed_str}+--h--m--s = --h--m--s"


def extract_frontmatter_and_body(text: str) -> tuple[str, str]:
    """Extract video title from frontmatter and return clean transcript excerpt."""
    title = ""
    body = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2].strip()
            # Extract video_title
            match = re.search(r'video_title:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
            if match:
                title = match.group(1).strip()

    # Truncate body to keep prompt lightweight for local CPU inference
    clean_body = " ".join(body[:MAX_TRANSCRIPT_CHARS].split())
    return title, clean_body


def unload_ollama_model(model: str = DEFAULT_MODEL, base_url: str = DEFAULT_OLLAMA_URL) -> None:
    """Explicitly tell Ollama to unload model weights and free RAM/VRAM immediately."""
    endpoint = f"{base_url.rstrip('/')}/api/generate"
    payload = {"model": model, "keep_alive": 0}
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
    except Exception:
        pass


def call_ollama(
    prompt: str,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_OLLAMA_URL,
    temperature: float = 0.2,
    keep_alive: str = "5m",
) -> str:
    """Send prompt to local Ollama instance and return raw response string."""
    endpoint = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": keep_alive,
        "options": {
            "temperature": temperature,
            "num_predict": 120,
            "num_gpu": 99,  # Offload all layers to GPU when NVIDIA driver/device is available
            "num_thread": min(4, os.cpu_count() or 4),  # Cap CPU threads to prevent system freeze
            "num_ctx": 2048,  # Truncate context to save memory (excerpts are only 2500 chars)
        },
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result.get("response", "").strip()


def parse_summary_line(raw_output: str) -> tuple[str, str]:
    """Parse output into (concept, synthesis) tuple with fallback.

    >>> parse_summary_line("Geometria CLIP, Processos difusivos alinham texto.")
    ('Geometria CLIP', 'Processos difusivos alinham texto.')
    """
    clean = raw_output.replace('"', "").replace("'", "").strip()
    # If the response returned multiple lines, take the first non-empty line
    lines = [line.strip() for line in clean.splitlines() if line.strip()]
    target_line = lines[0] if lines else clean

    if "," in target_line:
        concept, synthesis = target_line.split(",", 1)
        return concept.strip(), synthesis.strip()

    return "Síntese Conceitual", target_line.strip()


INDICATIVE_KEYWORDS: tuple[str, ...] = (
    "one sentence synthesis in original language",
    "one sentence synthesis",
    "synthesis in original language",
    "síntese conceitual",
    "sintese conceitual",
    "conceptual synthesis",
    "key concepts",
    "key concept",
    "key-concept",
    "conceitos-chave",
    "conceito-chave",
    "conceitos chave",
    "conceito chave",
    "síntese",
    "sintese",
    "synthesis",
    "conceitos",
    "conceito",
    "concepts",
    "concept",
    "concepto",
    "conceptos",
    "video title",
    "título",
    "titulo",
    "title",
)


def extract_essence(text: str) -> str:
    """Iteratively strip indicative keywords, markdown, prompt echoes, and delimiters using a while loop.

    >>> extract_essence("Key Concept: Gênero em Debate Social")
    'Gênero em Debate Social'
    >>> extract_essence("Síntese Conceitual")
    ''
    >>> extract_essence("Key Concept: Reception Ceremony (2 words)")
    'Reception Ceremony'
    >>> extract_essence("**Key Concept**: Family Influence in Adolescence")
    'Family Influence in Adolescence'
    >>> extract_essence("Síntese Conceitual: Human Error or System Failure?")
    'Human Error or System Failure?'
    >>> extract_essence("Key Concept: Key Concept: Double Stack")
    'Double Stack'
    """
    result = text.strip()
    while True:
        original = result
        # 1. Strip leading punctuation, quotes, markdown symbols, dashes, pipes
        result = re.sub(r"^[\s\"'*_\-–—:;|#]+", "", result).strip()

        # 2. Check and strip leading indicative prefixes (case-insensitive)
        for prefix in INDICATIVE_KEYWORDS:
            if result.lower().startswith(prefix):
                rest = result[len(prefix):]
                # Optional parenthetical qualifier right after keyword, e.g. "Key Concept (2 words):"
                m_paren = re.match(r"^\s*[\(\[][^\)\]]*[\)\]]", rest)
                if m_paren:
                    rest = rest[m_paren.end():]
                if not rest or rest[0] in " \t:=-–—_*#|([.,":
                    result = rest.strip()
                    break

        result = re.sub(r"^[\s\"'*_\-–—:;|#]+", "", result).strip()

        # 3. Strip trailing prompt echoes like (2 words), (2 to 4 words), (Original Language), (Key Concept)
        result = re.sub(
            r"\s*[\(\[](?:key\s*concepts?|conceitos?[\s\-]chave|s[íi]ntese(?:\s*conceitual)?|synthesis|\d+\s*(?:to\s*\d+\s*)?words?|original\s*language)[\)\]]?\s*$",
            "",
            result,
            flags=re.IGNORECASE,
        ).strip()

        # 4. Strip trailing punctuation/markdown
        result = re.sub(r"[\s\"'*_\-–—:;|#]+$", "", result).strip()

        if result == original:
            break

    return result


def clean_concept_and_synthesis(
    concept: str,
    synthesis: str,
    fallback_title: str = "",
) -> tuple[str, str]:
    """Clean concept and synthesis, recovering missing parts and stripping boilerplate keywords.

    Uses extract_essence() to iteratively remove prefixes/suffixes.
    If concept is empty or generic (e.g. from fallback 'Síntese Conceitual'),
    attempts to split synthesis or use synthesis/title as concept.
    """
    clean_c = extract_essence(concept)
    clean_s = extract_essence(synthesis)

    if not clean_c:
        # Check if synthesis contains a separator between concept and synthesis
        for sep in (" - ", " – ", " — ", " | "):
            if sep in clean_s:
                part_c, part_s = clean_s.split(sep, 1)
                cand_c = extract_essence(part_c)
                cand_s = extract_essence(part_s)
                if cand_c and cand_s:
                    clean_c = cand_c
                    clean_s = cand_s
                    break

        # If still no concept, but clean_s exists, synthesis itself might be the concept
        if not clean_c and clean_s:
            clean_c = clean_s
            clean_s = fallback_title or clean_s

        # Fallback to title if still empty
        if not clean_c:
            clean_c = fallback_title

    if not clean_s:
        clean_s = fallback_title or clean_c

    return clean_c, clean_s


def load_indexed_files(index_file: Path) -> set[str]:
    """Load filenames already present in index to prevent duplicate work."""
    if not index_file.exists():
        return set()

    indexed = set()
    with open(index_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                indexed.add(row[0].strip())
    return indexed


def get_channel_pending_files(folder: Path, output_dir: Path | None = None) -> list[Path]:
    """Return sorted list of txt files pending indexing for a given channel."""
    target_dir = output_dir if output_dir is not None else folder
    index_file = target_dir / f"index-{folder.name}.txt"
    already_indexed = load_indexed_files(index_file)

    txt_files: list[Path] = []
    with os.scandir(folder) as it:
        for entry in it:
            if entry.name.endswith(".txt") and not entry.name.startswith("index"):
                if entry.name not in already_indexed:
                    txt_files.append(Path(entry.path))
    txt_files.sort(key=lambda p: p.name)
    return txt_files


def process_channel_folder(
    folder: Path,
    channel_idx: int,
    total_channels: int,
    global_start_time: float,
    output_dir: Path | None = None,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_OLLAMA_URL,
    limit: int | None = None,
) -> int:
    """Process channel folder printing strictly one line per channel and one line per file in PES standard."""
    channel_name = folder.name
    target_dir = output_dir if output_dir is not None else folder
    index_file = target_dir / f"index-{channel_name}.txt"

    pending_files = get_channel_pending_files(folder, output_dir=output_dir)
    if not pending_files:
        return 0

    if limit:
        pending_files = pending_files[:limit]

    total_in_channel = len(pending_files)

    # 1. Strictly ONE line for the channel: [c+remaining=total] [percent%] [time_block] CHANNEL: name
    ch_elapsed = time.time() - global_start_time
    ch_remaining = total_channels - channel_idx
    ch_percent = ((channel_idx - 1) / total_channels) * 100

    if channel_idx == 1:
        ch_time_block = format_time_block(ch_elapsed, None)
    else:
        ch_done = channel_idx - 1
        avg_ch_sec = ch_elapsed / ch_done
        ch_eta_sec = (total_channels - ch_done) * avg_ch_sec
        ch_time_block = format_time_block(ch_elapsed, ch_eta_sec)

    print(f"\n{channel_idx}+{ch_remaining}={total_channels} ({ch_percent:6.2f}%) {ch_time_block} CHANNEL: {channel_name} ({total_in_channel} files)")

    # 2. Strictly ONE line per file: f+remaining=total (percent%) time_block filename | title
    channel_start_time = time.time()
    processed_count = 0

    with open(index_file, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        for f_idx, filepath in enumerate(pending_files, 1):
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                title, excerpt = extract_frontmatter_and_body(content)

                prompt = (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"Video Title: {title or filepath.stem}\n"
                    f"Transcript Excerpt:\n{excerpt}\n"
                )

                raw_response = call_ollama(prompt, model=model, base_url=base_url)
                concept, synthesis = parse_summary_line(raw_response)

                # Post-extraction check: iteratively extract essence and strip indicative keywords
                concept, synthesis = clean_concept_and_synthesis(
                    concept, synthesis, fallback_title=title or filepath.stem
                )

                writer.writerow([filepath.name, concept, synthesis])
                f.flush()
                processed_count += 1

                file_elapsed = time.time() - channel_start_time
                f_remaining = total_in_channel - f_idx
                f_percent = (f_idx / total_in_channel) * 100

                if f_idx == 1:
                    file_time_block = format_time_block(file_elapsed, None)
                else:
                    avg_file_sec = file_elapsed / f_idx
                    file_eta_sec = f_remaining * avg_file_sec
                    file_time_block = format_time_block(file_elapsed, file_eta_sec)

                display_title = concept if concept else (title or filepath.stem)
                print(f"{f_idx}+{f_remaining}={total_in_channel} ({f_percent:6.2f}%) {file_time_block} {filepath.name} | {display_title}")

            except Exception as exc:
                f_remaining = total_in_channel - f_idx
                f_percent = (f_idx / total_in_channel) * 100
                print(f"{f_idx}+{f_remaining}={total_in_channel} ({f_percent:6.2f}%) FAILED {filepath.name} | {exc}")

    return processed_count


# --- Self-validation asserts ---
def _run_sanity_checks():
    assert format_duration(15) == "00h00m15s"
    assert format_duration(95) == "00h01m35s"
    assert format_duration(3665) == "01h01m05s"
    assert format_time_block(60, 120) == "00h01m00s+00h02m00s = 00h03m00s"
    assert format_time_block(60, None) == "00h01m00s+--h--m--s = --h--m--s"

    c, s = parse_summary_line("Alpha, Beta gamma delta")
    assert c == "Alpha"
    assert s == "Beta gamma delta"

    # Essence extraction with while loop checks
    assert extract_essence("Key Concept: Gênero em Debate Social") == "Gênero em Debate Social"
    assert extract_essence("Key Concepts: Financial Education") == "Financial Education"
    assert extract_essence("Síntese Conceitual") == ""
    assert extract_essence("Key Concept (2 words): Reception Ceremony") == "Reception Ceremony"
    assert extract_essence("Key Concept: Reception Ceremony (2 words)") == "Reception Ceremony"
    assert extract_essence("**Key Concept**: Family Influence in Adolescence") == "Family Influence in Adolescence"
    assert extract_essence("Síntese Conceitual: Key Concept: Double Stack") == "Double Stack"
    assert extract_essence("Key Concept: Odisseuss vengeance (Odiseus se vinga)") == "Odisseuss vengeance (Odiseus se vinga)"
    assert extract_essence("Banco Centrals Liquidation Decision (Key Concept") == "Banco Centrals Liquidation Decision"

    # Clean concept and synthesis recovery checks
    c1, s1 = clean_concept_and_synthesis("Key Concept: Alpha", "Síntese: Beta gamma")
    assert c1 == "Alpha"
    assert s1 == "Beta gamma"

    c2, s2 = clean_concept_and_synthesis("Síntese Conceitual", "Key Concept: Human Error or System Failure?", fallback_title="Default")
    assert c2 == "Human Error or System Failure?"

    c3, s3 = clean_concept_and_synthesis(
        "Síntese Conceitual",
        "Liberalismo em Declínio - Javier Milé transforma a identidade liberal",
        fallback_title="Default",
    )
    assert c3 == "Liberalismo em Declínio"
    assert s3 == "Javier Milé transforma a identidade liberal"


if __name__ == "__main__":
    _run_sanity_checks()

    parser = argparse.ArgumentParser(description="Index raw transcript files with Ollama with standardized PES ETAs.")
    parser.add_argument(
        "--channel",
        "-c",
        type=str,
        default=None,
        help="Specific channel folder to index (e.g. '3Blue1Brown'). Defaults to all.",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Ollama model name (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help="Path to raw transcripts directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional custom directory to save index-*.txt files. Defaults to inside each channel folder.",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Limit number of files per channel (useful for testing).",
    )
    args = parser.parse_args()

    if not args.raw_dir.exists():
        sys.exit(1)

    if args.channel:
        target_folder = args.raw_dir / args.channel
        if not target_folder.is_dir():
            sys.exit(1)
        target_folders = [target_folder]
    else:
        target_folders = sorted([d for d in args.raw_dir.iterdir() if d.is_dir()])

    # Filter folders with pending files
    active_folders: list[tuple[Path, list[Path]]] = []
    for folder in target_folders:
        pending = get_channel_pending_files(folder, output_dir=args.output_dir)
        if pending:
            active_folders.append((folder, pending))

    total_channels = len(active_folders)
    global_start_time = time.time()

    atexit.register(unload_ollama_model, model=args.model, base_url=DEFAULT_OLLAMA_URL)
    try:
        for idx, (folder, _) in enumerate(active_folders, 1):
            process_channel_folder(
                folder=folder,
                channel_idx=idx,
                total_channels=total_channels,
                global_start_time=global_start_time,
                output_dir=args.output_dir,
                model=args.model,
                limit=args.limit,
            )
    finally:
        unload_ollama_model(model=args.model, base_url=DEFAULT_OLLAMA_URL)
