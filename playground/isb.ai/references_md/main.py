#!/usr/bin/env python3
"""ISB.AI GOD Monolith - References Processing Tool.

Provides sequential processing of reference backups, duplicate removal,
and merging/summarization of sets into a master indexed workspace.
"""

import json
import csv
import re
import shutil
import sys
import time
import unicodedata
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
import httpx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# --- Config ---
REFERENCES_DIR = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills/stangler-doctor/references")
TIME_LOG_PATH = Path(__file__).parent / "time_log.csv"
TIME_LOG_CHART_PATH = Path(__file__).parent / "time_log_chart.png"
SEPARATOR = "--------------------------------------------------------------------------------"
SEPARATOR_PATTERN = r"(?m)^--------------------------------------------------------------------------------$"

# Ollama LLM Config
OLLAMA_MODEL = "qwen2.5:7b" #"gemma3:270m"
OLLAMA_URL = "http://localhost:11434"


def normalize_keyword(kw: str) -> str:
    """Normalizes keyword to lowercase ASCII, stripping diacritics."""
    if not kw or not kw.strip():
        return ""
    # Decompose unicode characters and remove combining diacritical marks
    nfkd = unicodedata.normalize("NFKD", kw.strip())
    ascii_kw = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_kw.lower().strip()


def normalize_title_for_cache(title: str) -> str:
    """Normalizes a title to an alphanumeric-only lowercase ASCII string to ensure robust cache hits."""
    if not title:
        return ""
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_title = "".join(c for c in nfkd if not unicodedata.combining(c))
    return "".join(c for c in ascii_title if c.isalnum()).lower()


def process_backups():
    print(f"Scanning references directory for backups: {REFERENCES_DIR}")
    
    if not REFERENCES_DIR.exists():
        print(f"Error: References directory {REFERENCES_DIR} does not exist!", file=sys.stderr)
        return

    # Find all backup directories matching *-backup-YYYY-MM-DD
    backup_dirs = [
        d for d in REFERENCES_DIR.iterdir()
        if d.is_dir() and re.search(r"-backup-\d{4}-\d{2}-\d{2}$", d.name)
    ]

    if not backup_dirs:
        print("No backup directories matching '-backup-YYYY-MM-DD' found to process.")
        return

    print(f"Found {len(backup_dirs)} backup directories to process:")
    for d in backup_dirs:
        print(f"  - {d.name}")

    # Process each backup directory independently
    for backup_dir in backup_dirs:
        # Determine the target set name
        set_name = re.sub(r"-backup-\d{4}-\d{2}-\d{2}$", "", backup_dir.name)
        
        # Apply the XX-YY-rest_of_name mask
        match_pattern = re.match(r"^(\d+)\.(\d+)\.\s*(.*)$", set_name)
        if match_pattern:
            xx = f"{int(match_pattern.group(1)):02d}"
            yy = f"{int(match_pattern.group(2)):02d}"
            rest_of_name = match_pattern.group(3).lower()
            formatted_set_name = f"{xx}-{yy} {rest_of_name}"
        else:
            formatted_set_name = set_name

        print(f"\n==========================================")
        print(f"Processing Set: '{formatted_set_name}' (Original: '{set_name}')")
        print(f"Source: {backup_dir.name}")
        print(f"==========================================")

        # Find all markdown files in this backup directory
        files_in_dir = list(backup_dir.glob("*.md"))
        if not files_in_dir:
            print(f"  No markdown files found in {backup_dir.name}!")
            continue

        # Parse and group files
        grouped_files = []
        for p in files_in_dir:
            match = re.match(r"^(\d+)-", p.name)
            if match:
                num = int(match.group(1))
                
                # Extract the final number from the end of the filename (before .md)
                num_match = re.search(r"(\d+)\.md$", p.name)
                if num_match:
                    final_num = num_match.group(1)
                else:
                    final_num = str(num)
                
                # Construct renamed filename directly under the references root
                renamed_filename = f"{formatted_set_name} {final_num}.md"
                
                grouped_files.append({
                    "num": num,
                    "path": p,
                    "renamed_filename": renamed_filename,
                    "set_name": formatted_set_name
                })
            else:
                # If a file doesn't start with a number, just copy it to target
                dest = REFERENCES_DIR / p.name
                shutil.copy2(p, dest)
                p.unlink(missing_ok=True)
                print(f"  Moved non-sequenced file directly: {p.name} -> {dest.name}")

        if not grouped_files:
            print("  No sequenced files found to process in this directory.")
            # Clean up empty backup dir
            if not list(backup_dir.iterdir()):
                backup_dir.rmdir()
            continue

        # Sort files in group by their sequence number
        grouped_files.sort(key=lambda x: x["num"])

        # Load files and split by separator
        files_articles = []
        original_total_articles = 0
        for item in grouped_files:
            p = item["path"]
            content = p.read_text(encoding="utf-8")
            
            # Normalize alternative separators (e.g., "---" followed by "## Source:") to SEPARATOR + "Source:"
            content = re.sub(r"(?m)^---\s*\n+(\s*)#*\s*Source:", rf"{SEPARATOR}\n\1Source:", content)
            
            articles = content.split(SEPARATOR)
            original_total_articles += len(articles)
            print(f"  File {p.name}: {len(articles)} articles found.")
            files_articles.append({
                "item": item,
                "articles": articles
            })

        # Re-organize (shift last article of file i to the start of file i+1 if there's more than one article)
        shifts_performed = 0
        for i in range(len(files_articles) - 1):
            if len(files_articles[i]["articles"]) > 1:
                last_article = files_articles[i]["articles"].pop()
                files_articles[i+1]["articles"][0] = last_article + files_articles[i+1]["articles"][0]
                shifts_performed += 1
            else:
                print(f"  Warning: File {files_articles[i]['item']['path'].name} has only 1 article. Skipping shift to avoid empty file.")

        # Verify article counts
        new_total_articles = sum(len(f["articles"]) for f in files_articles)
        expected_articles = original_total_articles - shifts_performed
        assert new_total_articles == expected_articles, (
            f"Set '{set_name}': Expected {expected_articles} articles, but got {new_total_articles}"
        )

        # Write new files
        original_paths_to_delete = []
        for f_art in files_articles:
            item = f_art["item"]
            old_path = item["path"]

            # Save directly under REFERENCES_DIR
            new_path = REFERENCES_DIR / item["renamed_filename"]

            # Join articles and write
            new_content = SEPARATOR.join(f_art["articles"])
            new_path.write_text(new_content, encoding="utf-8")
            print(f"    Saved: {new_path.relative_to(REFERENCES_DIR.parent)}")

            assert new_path.exists(), f"Target file {new_path} does not exist after writing!"
            original_paths_to_delete.append(old_path)

        # Clean up original files for this set
        print("  Cleaning up original files in backup directory...")
        for old_path in original_paths_to_delete:
            old_path.unlink(missing_ok=True)
            print(f"    Deleted original: {old_path.name}")

        # Remove the backup directory if it's now empty
        if not list(backup_dir.iterdir()):
            backup_dir.rmdir()
            print(f"  Removed empty backup directory: {backup_dir.name}")
        else:
            print(f"  Warning: Backup directory {backup_dir.name} not empty, did not remove.")

    print("\nAll backup sets processed successfully!")


def remove_duplicate_sources():
    print(f"\nScanning processed references for duplicates: {REFERENCES_DIR}")
    
    if not REFERENCES_DIR.exists():
        print(f"Error: References directory {REFERENCES_DIR} does not exist!", file=sys.stderr)
        return

    # Find all Markdown files (both segmented and merged if they exist)
    md_files = sorted(list(REFERENCES_DIR.glob("*.md")))
    if not md_files:
        print("No markdown files found in the references directory.")
        return

    # Exclude index.md from duplicate analysis
    md_files = [p for p in md_files if p.name.lower() != "index.md"]

    print(f"Found {len(md_files)} markdown files to check.")

    file_data = []
    source_registry = defaultdict(list)
    total_sources_count = 0

    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading file {file_path.name}: {e}", file=sys.stderr)
            continue

        # Extract set name
        set_name = file_path.name.rsplit(" ", 1)[0]

        # Normalize alternative separators (--- followed by ## Source:) to standard format
        content = re.sub(r"(?m)^---\s*\n+(\s*)#*\s*Source:", r"--------------------------------------------------------------------------------\n\1Source:", content)

        blocks = re.split(SEPARATOR_PATTERN, content)
        parsed_blocks = []

        for idx, block in enumerate(blocks, start=1):
            block_stripped = block.strip()
            if not block_stripped:
                continue

            lines = [line.strip() for line in block.splitlines() if line.strip()]
            source_entry = None
            source_key = None

            if lines:
                first_line = lines[0]
                if first_line.startswith("Source:"):
                    source_title = first_line[len("Source:"):].strip()
                    if source_title:
                        source_entry = f"Source: {source_title}"
                        source_key = source_entry.lower().strip()

            if source_key:
                source_registry[source_key].append({
                    "file_name": file_path.name,
                    "set_name": set_name,
                    "original_entry": source_entry,
                    "block_idx": idx
                })
                total_sources_count += 1

            parsed_blocks.append({
                "original_index": idx,
                "content": block,
                "source_key": source_key,
                "source_entry": source_entry
            })

        file_data.append({
            "path": file_path,
            "name": file_path.name,
            "set_name": set_name,
            "blocks": parsed_blocks
        })

    duplicates = {norm: occurrences for norm, occurrences in source_registry.items() if len(occurrences) > 1}

    print("\n" + "=" * 50)
    print("INITIAL ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Total markdown files processed: {len(md_files)}")
    print(f"Total sources found:            {total_sources_count}")
    print(f"Unique sources:                 {len(source_registry)}")
    print(f"Duplicate sources:              {len(duplicates)}")
    print("=" * 50 + "\n")

    # Step 2: Remove duplicates in the same set_name
    seen_in_set = defaultdict(set)
    removed_count = 0
    modified_files_count = 0

    for file_info in file_data:
        file_path = file_info["path"]
        set_name = file_info["set_name"]
        keep_blocks = []
        file_modified = False

        for block in file_info["blocks"]:
            source_key = block["source_key"]
            source_entry = block["source_entry"]

            if source_key:
                if set_name in seen_in_set[source_key]:
                    # Duplicate in same set! Remove it
                    print(f"Removing duplicate source from '{file_info['name']}':")
                    print(f"  ✓ {source_entry}")
                    file_modified = True
                    removed_count += 1
                    continue
                else:
                    seen_in_set[source_key].add(set_name)
                    keep_blocks.append(block["content"])
            else:
                keep_blocks.append(block["content"])

        if file_modified:
            modified_files_count += 1
            stripped_blocks = [b.strip() for b in keep_blocks if b.strip()]
            
            if stripped_blocks:
                new_content = ("\n" + SEPARATOR + "\n").join(stripped_blocks) + "\n"
                file_path.write_text(new_content, encoding="utf-8")
                print(f"  --> Updated file: {file_info['name']}")
            else:
                file_path.unlink(missing_ok=True)
                print(f"  --> Deleted empty file: {file_info['name']}")

    print("\n" + "=" * 50)
    print("CLEANUP SUMMARY")
    print("=" * 50)
    print(f"Duplicate sources removed:      {removed_count}")
    print(f"Files modified/deleted:         {modified_files_count}")
    print("=" * 50 + "\n")


def get_ollama_summary(source_content: str, set_name: str) -> dict:
    """Invokes local Ollama LLM in JSON mode to generate summary and keywords."""
    truncated_content = source_content[:]

    # Add warning for extremely large files on CPU
    if len(source_content) > 25000:
        print(f"      [Ollama API] Warning: Block is very large ({len(source_content)} chars). CPU prefill may take time.")

    system_prompt = (
        "You are a Principal Socio-Technical Architect and SRE expert.\n"
        "Your task is to analyze the technical reference text and provide:\n"
        "1. A concise, one-line summary in English describing the main topic of the source within the context of the set '{set_name}'.\n"
        "2. A list of 3 to 10 key technical keywords/concepts that support the content of the source.\n\n"
        "Rules:\n"
        "1. Write the summary in English, even if the source is in another language.\n"
        "2. Output MUST be a valid JSON object matching this schema: {\"summary\": string, \"keywords\": [string]}.\n"
        "3. Do not include any markdown code blocks, prefixes, or conversational introduction."
    )

    prompt = f"Source Content:\n{truncated_content}\n\nReturn JSON summary and keywords:"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_predict": 350,  # slightly higher limit to accommodate JSON and keywords list
        }
    }

    start_time = time.time()
    try:
        response = httpx.post(f"{OLLAMA_URL.rstrip('/')}/api/generate", json=payload, timeout=None)
        response.raise_for_status()
        duration = time.time() - start_time
        res_json = response.json()

        # Token and performance stats extraction
        eval_count = res_json.get("eval_count", 0)
        eval_duration_ns = res_json.get("eval_duration", 0)
        prompt_eval_count = res_json.get("prompt_eval_count", 0)
        prompt_eval_duration_ns = res_json.get("prompt_eval_duration", 0)
        total_duration_ns = res_json.get("total_duration", 0)
        load_duration_ns = res_json.get("load_duration", 0)

        # Convert ns to seconds
        eval_dur = eval_duration_ns / 1e9 if eval_duration_ns else 0
        prompt_dur = prompt_eval_duration_ns / 1e9 if prompt_eval_duration_ns else 0
        total_dur = total_duration_ns / 1e9 if total_duration_ns else 0
        load_dur = load_duration_ns / 1e9 if load_duration_ns else 0

        eval_tps = eval_count / eval_dur if eval_dur > 0 else 0
        prompt_tps = prompt_eval_count / prompt_dur if prompt_dur > 0 else 0

        print(f"      [Ollama API Stats]")
        print(f"        - Model: {OLLAMA_MODEL}")
        print(f"        - Total Duration: {total_dur:.2f}s (Load: {load_dur:.2f}s, Process Wall Time: {duration:.2f}s)")
        print(f"        - Prompt: {prompt_eval_count} tokens | Duration: {prompt_dur:.2f}s | Speed: {prompt_tps:.2f} t/s")
        print(f"        - Generation: {eval_count} tokens | Duration: {eval_dur:.2f}s | Speed: {eval_tps:.2f} t/s")

        raw_text = res_json.get("response", "").strip()
        # Clean thought tags from reasoning models
        clean_text = re.sub(r"(?s)<thought>.*?</thought>", "", raw_text).strip()
        
        # Parse JSON
        parsed_data = json.loads(clean_text)
        summary = parsed_data.get("summary", "").strip()
        keywords = parsed_data.get("keywords", [])
        if not isinstance(keywords, list):
            keywords = []
        keywords = [str(k).strip() for k in keywords if str(k).strip()]
        
        return {"summary": summary, "keywords": keywords}
    except Exception as e:
        print(f"Error calling or parsing Ollama API: {e}", file=sys.stderr)
        return {"summary": "Failed to generate summary.", "keywords": []}


def generate_index_md(index_data):
    index_file_path = REFERENCES_DIR / "index.md"
    keyword_sources = defaultdict(list)
    
    for set_name, sources in index_data.items():
        encoded_set_name = set_name.replace(" ", "%20")
        for src in sources:
            for kw in src.get("keywords", []):
                norm_kw = normalize_keyword(kw)
                if not norm_kw:
                    continue
                
                already_linked = False
                for existing in keyword_sources[norm_kw]:
                    if existing["title"] == src["title"] and existing["set_name"] == set_name:
                        already_linked = True
                        break
                
                if not already_linked:
                    keyword_sources[norm_kw].append({
                        "title": src["title"],
                        "set_name": set_name,
                        "link": f"{encoded_set_name}.md#L{src['start']}-L{src['end']}"
                    })

    index_lines = [
        "# References Index",
        "",
        "Welcome to the references index. Below is a map of all unique technical and strategic sources grouped by set and key concepts.",
        "Use the links to jump directly to specific source locations.",
        "",
        "## Sources by Set",
        ""
    ]

    for set_name, sources in sorted(index_data.items()):
        encoded_set_name = set_name.replace(" ", "%20")
        index_lines.append(f"### [{set_name}]({encoded_set_name}.md)")
        for src in sources:
            kw_line = ""
            if src.get("keywords"):
                set_kws = []
                for k in src["keywords"]:
                    nk = normalize_keyword(k)
                    if nk and nk not in set_kws:
                        set_kws.append(nk)
                if set_kws:
                    kw_tags = ", ".join(f"`{k}`" for k in set_kws)
                    kw_line = f"\n  - **Keywords:** {kw_tags}"
            
            index_lines.append(f"- [{src['title']}]({encoded_set_name}.md#L{src['start']}-L{src['end']}) - *{src['summary']}*{kw_line}")
        index_lines.append("")

    index_lines.append("---")
    index_lines.append("")
    index_lines.append("## Sources by Keyword")
    index_lines.append("")

    # Sort keywords alphabetically
    for norm_kw, sources in sorted(keyword_sources.items()):
        index_lines.append(f"### `{norm_kw}`")
        for src in sources:
            index_lines.append(f"- [{src['title']}]({src['link']}) (from *{src['set_name']}*)")
        index_lines.append("")

    index_file_path.write_text("\n".join(index_lines), encoding="utf-8")
    # print(f"Generated/updated master index: {index_file_path.name}")


def load_index_data_from_index_md(index_path: Path) -> dict:
    """Parses index.md to rebuild the index_data mapping of sets to sources."""
    index_data = defaultdict(list)
    if not index_path.exists():
        return index_data

    try:
        content = index_path.read_text(encoding="utf-8")
        current_set = None
        
        set_pattern = re.compile(r"^###\s+\[([^\]]+)\]\(([^)]+)\)")
        source_pattern = re.compile(r"^-\s+\[(.*)\]\((?:[^#]+#L(\d+)-L(\d+))\)\s+-\s+\*(.*?)\*(?:\s*|$)")
        keywords_pattern = re.compile(r"^\s+-\s+\*\*Keywords:\*\*\s+(.*)")

        for line in content.splitlines():
            line_str = line.strip()
            if not line_str:
                continue

            set_match = set_pattern.match(line)
            if set_match:
                current_set = set_match.group(1).strip()
                continue

            source_match = source_pattern.match(line)
            if source_match and current_set:
                title = source_match.group(1).strip()
                start = int(source_match.group(2))
                end = int(source_match.group(3))
                summary = source_match.group(4).strip()
                
                index_data[current_set].append({
                    "title": title,
                    "start": start,
                    "end": end,
                    "summary": summary,
                    "keywords": []
                })
                continue

            kw_match = keywords_pattern.match(line)
            if kw_match and current_set and index_data[current_set]:
                kw_str = kw_match.group(1).strip()
                kws = re.findall(r"`([^`]+)`", kw_str)
                index_data[current_set][-1]["keywords"] = [normalize_keyword(k) for k in kws if normalize_keyword(k)]
                
        print(f"Loaded index data for {len(index_data)} sets from index.md.")
    except Exception as e:
        print(f"Warning: Failed to load index data from index.md: {e}", file=sys.stderr)
        
    return index_data


def log_time_data(set_name: str, block_idx: int, total_blocks: int, percent: float, elapsed: float, remaining: float):
    """Logs progress tracking data to a CSV file for performance and trend analysis."""
    file_exists = TIME_LOG_PATH.exists()
    
    # Calculate estimated total time
    estimated_total = elapsed + remaining if remaining is not None else None
    
    row = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "set_name": set_name,
        "block_idx": block_idx,
        "total_blocks": total_blocks,
        "percent": round(percent, 2),
        "elapsed_seconds": round(elapsed, 2),
        "estimated_remaining_seconds": round(remaining, 2) if remaining is not None else "",
        "estimated_total_seconds": round(estimated_total, 2) if estimated_total is not None else ""
    }
    
    headers = [
        "timestamp", "set_name", "block_idx", "total_blocks", "percent", 
        "elapsed_seconds", "estimated_remaining_seconds", "estimated_total_seconds"
    ]
    
    try:
        with open(TIME_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"Warning: Failed to write time log: {e}", file=sys.stderr)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to xxhxxmxxs (e.g. 02h14m45s)."""
    secs = int(seconds)
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    remaining_secs = secs % 60
    return f"{hours:02d}h{minutes:02d}m{remaining_secs:02d}s"


def plot_time_log():
    """Generates a beautiful multi-panel stacked area chart (one panel per set)."""
    if not TIME_LOG_PATH.exists():
        return
        
    try:
        df = pd.read_csv(TIME_LOG_PATH)
    except Exception:
        return
        
    if df.empty:
        return

    # Convert fields to numeric
    df['block_idx'] = pd.to_numeric(df['block_idx'], errors='coerce')
    df['percent'] = pd.to_numeric(df['percent'], errors='coerce')
    df['elapsed_seconds'] = pd.to_numeric(df['elapsed_seconds'], errors='coerce')
    df['estimated_remaining_seconds'] = pd.to_numeric(df['estimated_remaining_seconds'], errors='coerce')
    df['estimated_total_seconds'] = pd.to_numeric(df['estimated_total_seconds'], errors='coerce')
    
    # Drop rows without block_idx or elapsed_seconds
    df = df.dropna(subset=['block_idx', 'elapsed_seconds', 'set_name']).reset_index(drop=True)
    
    if df.empty:
        return
        
    df['estimated_remaining_seconds'] = df['estimated_remaining_seconds'].fillna(0)
    df['estimated_total_seconds'] = df['estimated_total_seconds'].fillna(df['elapsed_seconds'])

    # Clean and sanitize data per set to prevent overlapping blocks and time regression bugs in subplots
    cleaned_dfs = []
    for s_name in df['set_name'].unique():
        df_set = df[df['set_name'] == s_name].copy()
        
        # Discard any "future" orphan blocks from previous aborted runs that went further
        if not df_set.empty:
            last_recorded_block = df_set['block_idx'].iloc[-1]
            df_set = df_set[df_set['block_idx'] <= last_recorded_block]
            
        # Drop duplicates of block_idx keeping the last (most recent) run record
        df_set = df_set.drop_duplicates(subset=['block_idx'], keep='last')
        # Sort by block index to ensure monotonic progress on the X-axis
        df_set = df_set.sort_values(by='block_idx').reset_index(drop=True)
        # Prevent elapsed time regressions (due to session restarts or clock drifts)
        df_set['elapsed_seconds'] = df_set['elapsed_seconds'].cummax()
        # Re-align estimated remaining seconds based on the raw estimated total
        df_set['estimated_remaining_seconds'] = (df_set['estimated_total_seconds'] - df_set['elapsed_seconds']).clip(lower=0)
        
        # Ensure the plot starts at 0% progress to avoid whitespace cuts at the beginning of the chart
        if not df_set.empty and df_set['percent'].iloc[0] > 0:
            first_row = df_set.iloc[0].copy()
            first_row['percent'] = 0.0
            first_row['block_idx'] = 0
            first_row['elapsed_seconds'] = 0.0
            first_row['estimated_total_seconds'] = df_set['estimated_total_seconds'].iloc[0]
            first_row['estimated_remaining_seconds'] = first_row['estimated_total_seconds']
            df_set = pd.concat([pd.DataFrame([first_row]), df_set], ignore_index=True)
            
        cleaned_dfs.append(df_set)
        
    if cleaned_dfs:
        df = pd.concat(cleaned_dfs, ignore_index=True)

    # Get unique sets in reverse chronological order (most recent on top, oldest on bottom)
    unique_sets = list(df['set_name'].unique())[::-1]
    num_sets = len(unique_sets)
    
    # Style configuration for Premium Look
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # Adjust figure height dynamically depending on the number of sets
    fig, axes = plt.subplots(nrows=num_sets, ncols=1, figsize=(10, 3.5 * num_sets), dpi=150, sharex=True)
    
    # Handle single subplot case where axes is not a list
    if num_sets == 1:
        axes = [axes]
        
    color_elapsed = '#4f46e5'  # indigo
    color_remaining = '#06b6d4'  # cyan
    
    for idx, (set_name, ax) in enumerate(zip(unique_sets, axes)):
        df_set = df[df['set_name'] == set_name].reset_index(drop=True)
        
        x = df_set['percent']
        y_elapsed = df_set['elapsed_seconds'] / 60
        y_remaining = df_set['estimated_remaining_seconds'] / 60
        y_total = df_set['estimated_total_seconds'] / 60
        
        ax.stackplot(x, y_elapsed, y_remaining, 
                     labels=['Elapsed (m)', 'Est. Remaining (m)'],
                     colors=[color_elapsed, color_remaining], 
                     alpha=0.85,
                     edgecolor='none')
        
        ax.plot(x, y_total, color='#0f172a', linestyle='--', linewidth=1.5, label='Est. Total (m)')
        
        ax.set_title(f"Timing Convergence: {set_name}", fontsize=11, fontweight='bold', pad=8, color='#1e293b')
        ax.set_ylabel("Minutes", fontsize=9, labelpad=8, color='#475569')
        ax.set_xlim(0, 100)
        
        ax.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
        for spine in ax.spines.values():
            spine.set_edgecolor('#e2e8f0')
            
        # Place legend only on the first subplot to save space
        if idx == 0:
            ax.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', framealpha=0.9, fontsize=8)
            
        pass

    # Set common X label on the bottom-most subplot
    axes[-1].set_xlabel("Progress (%)", fontsize=10, labelpad=10, color='#475569')
    
    plt.suptitle("Processing Timing Vibe: Dynamic ETA Convergence", fontsize=13, fontweight='bold', y=0.98, color='#1e293b')
    plt.tight_layout()
    plt.savefig(TIME_LOG_CHART_PATH, dpi=300)
    plt.close(fig)  # prevent memory leaks in loop


def heal_index_line_references(index_data: dict) -> dict:
    """Scan existing merged .md files and update index_data line ranges to match actual file content."""
    for set_name, sources in index_data.items():
        merged_file_path = REFERENCES_DIR / f"{set_name}.md"
        if not merged_file_path.exists():
            continue
        
        try:
            content = merged_file_path.read_text(encoding="utf-8")
            file_lines = content.splitlines()
            
            actual_line_map = {}
            current_block_lines = []
            block_start_line = 1
            
            for line_idx, line in enumerate(file_lines, start=1):
                if line.strip() == SEPARATOR:
                    if current_block_lines:
                        first_lines = [ln.strip() for ln in current_block_lines if ln.strip()]
                        if first_lines and first_lines[0].startswith("Source:"):
                            title_key = first_lines[0][len("Source:"):].strip()
                            actual_line_map[title_key] = (block_start_line, line_idx - 1)
                    current_block_lines = []
                    block_start_line = line_idx + 1
                else:
                    current_block_lines.append(line)
                    
            if current_block_lines:
                first_lines = [ln.strip() for ln in current_block_lines if ln.strip()]
                if first_lines and first_lines[0].startswith("Source:"):
                    title_key = first_lines[0][len("Source:"):].strip()
                    actual_line_map[title_key] = (block_start_line, len(file_lines))
            
            updated_count = 0
            for src in sources:
                title = src["title"]
                if title in actual_line_map:
                    real_start, real_end = actual_line_map[title]
                    if src["start"] != real_start or src["end"] != real_end:
                        src["start"] = real_start
                        src["end"] = real_end
                        updated_count += 1
            
            if updated_count > 0:
                print(f"Healed {updated_count} line reference discrepancies for set '{set_name}'.")
                
        except Exception as e:
            print(f"Warning: Failed to heal line references for '{set_name}': {e}", file=sys.stderr)
            
    return index_data


def compile_and_summarize():
    print(f"\nMerging sources by set name and generating summaries: {REFERENCES_DIR}")
    
    if not REFERENCES_DIR.exists():
        print(f"Error: References directory {REFERENCES_DIR} does not exist!", file=sys.stderr)
        return

    # Load cache and index data directly from index.md (SSOT)
    index_file_path = REFERENCES_DIR / "index.md"
    index_data = load_index_data_from_index_md(index_file_path)
    
    # Heal line references from disk to fix any previous drift in index.md
    index_data = heal_index_line_references(index_data)
    generate_index_md(index_data)

    cache = {}
    for s_name, sources in index_data.items():
        for src in sources:
            cache_key = f"{s_name}:::{normalize_title_for_cache(src['title'])}"
            norm_kws = [normalize_keyword(k) for k in src.get("keywords", []) if normalize_keyword(k)]
            cache[cache_key] = {
                "summary": src["summary"],
                "keywords": norm_kws
            }

    # Fallback/migration: If index.md is empty or missing, load from summaries_cache.json
    cache_path = Path(__file__).parent / "summaries_cache.json"
    if cache_path.exists():
        try:
            legacy_cache = json.loads(cache_path.read_text(encoding="utf-8"))
            migrated_count = 0
            for k, v in legacy_cache.items():
                parts = k.split(":::", 1)
                if len(parts) == 2:
                    cache_key = f"{parts[0]}:::{normalize_title_for_cache(parts[1])}"
                else:
                    cache_key = k
                if cache_key not in cache:
                    if isinstance(v, dict):
                        norm_kws = [normalize_keyword(kw) for kw in v.get("keywords", []) if normalize_keyword(kw)]
                        cache[cache_key] = {
                            "summary": v.get("summary", "").strip(),
                            "keywords": norm_kws
                        }
                    else:
                        cache[cache_key] = {
                            "summary": str(v).strip(),
                            "keywords": []
                        }
                    migrated_count += 1
            if migrated_count > 0:
                print(f"Loaded and migrated {migrated_count} entries from legacy summaries_cache.json.")
        except Exception as e:
            print(f"Warning: Failed to load legacy summaries_cache.json: {e}", file=sys.stderr)

    print(f"Loaded {len(cache)} total summaries into in-memory cache.")

    # Find all segmented Markdown files (ending in a space and a number + .md)
    # E.g. '01-01 product engineering 08.md'
    segmented_files = []
    for p in REFERENCES_DIR.glob("*.md"):
        if re.search(r"\s+\d+\.md$", p.name):
            segmented_files.append(p)

    if not segmented_files:
        print("No segmented markdown files found to merge.")
        # Make sure we still generate the index if we have reconstructed data
        if index_data:
            generate_index_md(index_data)
        return

    print(f"Found {len(segmented_files)} segmented markdown files to merge.")

    # Group files by set name
    set_files = defaultdict(list)
    for p in segmented_files:
        set_name = p.name.rsplit(" ", 1)[0]
        set_files[set_name].append(p)

    # Process each set
    for set_name, paths in sorted(set_files.items()):
        paths.sort()
        
        print(f"\nMerging set: '{set_name}' ({len(paths)} files)")
        
        blocks_to_merge = []
        for path in paths:
            try:
                content = path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  Error reading file {path.name}: {e}", file=sys.stderr)
                continue
            
            # Normalize alternative separators (--- followed by ## Source:) to standard format
            content = re.sub(r"(?m)^---\s*\n+(\s*)#*\s*Source:", r"--------------------------------------------------------------------------------\n\1Source:", content)
            
            blocks = re.split(SEPARATOR_PATTERN, content)
            for block in blocks:
                block_stripped = block.strip()
                if not block_stripped:
                    continue
                
                # Extract source title
                lines = [line.strip() for line in block.splitlines() if line.strip()]
                source_title = None
                if lines and lines[0].startswith("Source:"):
                    source_title = lines[0][len("Source:"):].strip()
                
                blocks_to_merge.append((block_stripped, source_title))

        if not blocks_to_merge:
            print(f"  No valid blocks found to merge for set '{set_name}'.")
            continue

        print(f"  Total blocks to process for this set: {len(blocks_to_merge)}")

        # Clear index data for the active set to prevent duplication
        index_data[set_name] = []

        # Pre-compute block metadata and line ranges
        current_line = 1
        blocks_with_metadata = []
        for block_content, source_title in blocks_to_merge:
            num_lines = len(block_content.splitlines())
            start_line = current_line
            end_line = current_line + num_lines - 1
            blocks_with_metadata.append({
                "content": block_content,
                "title": source_title or "Untitled Source",
                "start": start_line,
                "end": end_line
            })
            current_line += num_lines + 2  # Separator line + newlines around it

        # Process blocks — flush merged file + index.md after every block so
        # both files stay in sync as an incremental SSOT cache.
        merged_content_parts = []
        
        # Get accumulated time offset and historical runs from previous run of the same set to make it cumulative
        accumulated_time_offset = 0.0
        historical_active_runs = 0
        if TIME_LOG_PATH.exists():
            try:
                df_temp = pd.read_csv(TIME_LOG_PATH)
                df_set = df_temp[df_temp['set_name'] == set_name]
                if not df_set.empty:
                    accumulated_time_offset = float(df_set['elapsed_seconds'].iloc[-1])
                    historical_active_runs = int(df_set.shape[0])
            except Exception:
                pass
                
        total_active_runs_session = 0
        set_start_time = time.time()
        block_durations: list[float] = []  # wall time per LLM call (non-cached)
        total_processed = 0  # cached + LLM blocks done so far
        set_entries: list[dict] = []

        merged_file_path = REFERENCES_DIR / f"{set_name}.md"

        def _flush_to_disk() -> None:
            """Write partial merged file then update index.md with correct line refs."""
            # 1. Write (or overwrite) the merged file with content processed so far
            partial_content = ("\n" + SEPARATOR + "\n").join(merged_content_parts) + "\n"
            merged_file_path.write_text(partial_content, encoding="utf-8")

            # 2. Recompute actual line numbers by scanning the partial content line-by-line
            actual_line_map: dict[str, tuple[int, int]] = {}
            file_lines = partial_content.splitlines()
            
            current_block_lines = []
            block_start_line = 1
            
            for line_idx, line in enumerate(file_lines, start=1):
                if line.strip() == SEPARATOR:
                    if current_block_lines:
                        first_lines = [ln.strip() for ln in current_block_lines if ln.strip()]
                        if first_lines and first_lines[0].startswith("Source:"):
                            title_key = first_lines[0][len("Source:"):].strip()
                            actual_line_map[title_key] = (block_start_line, line_idx - 1)
                    current_block_lines = []
                    block_start_line = line_idx + 1
                else:
                    current_block_lines.append(line)
            
            # Flush the last block remaining
            if current_block_lines:
                first_lines = [ln.strip() for ln in current_block_lines if ln.strip()]
                if first_lines and first_lines[0].startswith("Source:"):
                    title_key = first_lines[0][len("Source:"):].strip()
                    actual_line_map[title_key] = (block_start_line, len(file_lines))

            # 3. Update index_data for this set keeping other historical entries intact
            processed_map = {normalize_title_for_cache(entry["title"]): entry for entry in set_entries}
            new_set_entries = []
            processed_titles_norm = set()
            
            for idx_b in range(total_processed):
                block_b = blocks_with_metadata[idx_b]
                t_title = block_b["title"]
                t_norm = normalize_title_for_cache(t_title)
                entry = processed_map.get(t_norm)
                if entry:
                    line_range = actual_line_map.get(t_title, (0, 0))
                    new_set_entries.append({
                        "title": t_title,
                        "start": line_range[0],
                        "end": line_range[1],
                        "summary": entry["summary"],
                        "keywords": entry["keywords"],
                    })
                    processed_titles_norm.add(t_norm)
            
            # Append historical entries for sources that we haven't reached/processed yet in this run
            historical_list = index_data.get(set_name, [])
            for hist in historical_list:
                hist_norm = normalize_title_for_cache(hist["title"])
                if hist_norm not in processed_titles_norm:
                    new_set_entries.append(hist)
                    processed_titles_norm.add(hist_norm)
            
            index_data[set_name] = new_set_entries

            # 4. Write index.md — now references a file that exists on disk
            generate_index_md(index_data)

        for idx, block in enumerate(blocks_with_metadata, start=1):
            block_content = block["content"]
            source_title = block["title"]

            summary = ""
            keywords = []

            if source_title and source_title != "Untitled Source":
                cache_key = f"{set_name}:::{normalize_title_for_cache(source_title)}"
                if cache_key in cache:
                    cached_val = cache[cache_key]
                    summary = cached_val.get("summary", "").strip()
                    keywords = cached_val.get("keywords", [])
                    
                    # Log print for cache hits (identical formatting and global ETA)
                    remaining = len(blocks_to_merge) - idx
                    elapsed_active = time.time() - set_start_time
                    elapsed_to_log = accumulated_time_offset + elapsed_active
                    percent = (idx / len(blocks_to_merge)) * 100
                    total = len(blocks_to_merge)
                    
                    total_runs_so_far = historical_active_runs + total_active_runs_session
                    if total_runs_so_far > 0 and elapsed_to_log > 0:
                        rate = total_runs_so_far / elapsed_to_log
                        eta_sec = remaining / rate
                        elapsed_str = format_duration(elapsed_to_log)
                        eta_str = format_duration(eta_sec)
                        total_time_str = format_duration(elapsed_to_log + eta_sec)
                        time_block = f"{elapsed_str}+{eta_str} = {total_time_str}"
                    else:
                        elapsed_str = format_duration(elapsed_to_log)
                        time_block = f"{elapsed_str}+--h--m--s = --h--m--s"
                        
                    if len(source_title) > 40:
                        print(f"  [{idx}+{remaining} = {total}] [{percent:.2f}%] [{time_block}] {source_title[:40]}...")
                    else:
                        print(f"  [{idx}+{remaining} = {total}] [{percent:.2f}%] [{time_block}] {source_title}")
                else:
                    # ETA: derive rate from global metrics (history + current session)
                    remaining = len(blocks_to_merge) - idx
                    elapsed_active = time.time() - set_start_time
                    elapsed_to_log = accumulated_time_offset + elapsed_active
                    percent = (idx / len(blocks_to_merge)) * 100
                    total = len(blocks_to_merge)
                    
                    total_runs_so_far = historical_active_runs + total_active_runs_session
                    if total_runs_so_far > 0 and elapsed_to_log > 0:
                        rate = total_runs_so_far / elapsed_to_log
                        eta_sec = (remaining + 1) / rate
                        elapsed_str = format_duration(elapsed_to_log)
                        eta_str = format_duration(eta_sec)
                        total_time_str = format_duration(elapsed_to_log + eta_sec)
                        time_block = f"{elapsed_str}+{eta_str} = {total_time_str}"
                    else:
                        elapsed_str = format_duration(elapsed_to_log)
                        time_block = f"{elapsed_str}+--h--m--s = --h--m--s"

                    print(f"  [{idx}+{remaining} = {total}] [{percent:.2f}%] [{time_block}] {source_title[:40]}...")
                    block_t0 = time.time()
                    result = get_ollama_summary(block_content, set_name)
                    block_durations.append(time.time() - block_t0)
                    summary = result.get("summary", "").strip()
                    keywords = result.get("keywords", [])

                    if "Failed to generate" not in summary and summary.strip():
                        cache[cache_key] = {"summary": summary, "keywords": keywords}

                    # Log progress metrics to CSV ONLY for active runs (cumulatively)
                    total_active_runs_session += 1
                    elapsed_active = time.time() - set_start_time
                    elapsed_to_log = accumulated_time_offset + elapsed_active
                    total_runs_so_far = historical_active_runs + total_active_runs_session
                    
                    if total_runs_so_far > 1 and elapsed_to_log > 0:
                        rate = (total_runs_so_far - 1) / elapsed_to_log
                        eta_val = remaining / rate
                    else:
                        eta_val = None

                    log_time_data(set_name, idx, len(blocks_to_merge), percent, elapsed_to_log, eta_val)

                    # Automatically update the stacked area chart in real-time
                    try:
                        plot_time_log()
                    except Exception as e:
                        print(f"Warning: Failed to update time chart: {e}", file=sys.stderr)
            else:
                summary = "No summary available (untitled source)."
                keywords = []

            total_processed += 1
            merged_content_parts.append(block_content)
            set_entries.append({
                "title": source_title,
                "summary": summary,
                "keywords": keywords,
            })

            # Flush merged file + index.md after every block (SSOT cache write)
            _flush_to_disk()

        print(f"  --> Saved merged file: {merged_file_path.name} ({len(blocks_to_merge)} sources)")

        # Cleanup: delete segmented files
        print(f"  Cleaning up segmented files...")
        for path in paths:
            path.unlink(missing_ok=True)
            print(f"    Deleted segmented file: {path.name}")


def main():
    process_backups()
    remove_duplicate_sources()
    compile_and_summarize()


if __name__ == "__main__":
    main()
