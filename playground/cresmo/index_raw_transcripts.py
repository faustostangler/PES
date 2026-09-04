#!/usr/bin/env python3
"""Index raw transcript files using local Ollama LLM into paratactic CSV summaries with standardized PES ETA logging."""

import argparse
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


def call_ollama(
    prompt: str,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_OLLAMA_URL,
    temperature: float = 0.2,
) -> str:
    """Send prompt to local Ollama instance and return raw response string."""
    endpoint = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "60m",
        "options": {
            "temperature": temperature,
            "num_predict": 120,
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

                display_title = title if title else concept
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
