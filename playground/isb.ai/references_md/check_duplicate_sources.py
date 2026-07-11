#!/usr/bin/env python3
"""Script to scan reference markdown files, check for duplicate sources, and remove intra-set duplicates."""

import re
import sys
from collections import defaultdict
from pathlib import Path

# --- Config ---
REFERENCES_DIR = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills/stangler-doctor/references")
REPORT_PATH = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/playground/isb.ai/references_md/duplicates_report.txt")
SEPARATOR = "--------------------------------------------------------------------------------"
SEPARATOR_PATTERN = r"(?m)^--------------------------------------------------------------------------------$"

def generate_report_content(md_files):
    source_registry = defaultdict(list)
    total_sources_count = 0
    warnings = []

    for file_path in md_files:
        if not file_path.exists():
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            warnings.append(f"Error reading file {file_path.name}: {e}")
            continue

        blocks = re.split(SEPARATOR_PATTERN, content)
        for idx, block in enumerate(blocks, start=1):
            block_stripped = block.strip()
            if not block_stripped:
                continue

            lines = [line.strip() for line in block.splitlines() if line.strip()]
            found_source = False
            if lines:
                first_line = lines[0]
                if first_line.startswith("Source:"):
                    source_title = first_line[len("Source:"):].strip()
                    if source_title:
                        source_entry = f"Source: {source_title}"
                        normalized = source_entry.lower().strip()
                        source_registry[normalized].append((file_path.name, source_entry))
                        total_sources_count += 1
                        found_source = True
            
            if not found_source:
                # Optionally report if a block does not contain a "Source:" line
                # Commented out warning printing as requested by user edits
                pass

    duplicates = {norm: occurrences for norm, occurrences in source_registry.items() if len(occurrences) > 1}

    report_lines = []
    if warnings:
        report_lines.extend(warnings)
        report_lines.append("")

    report_lines.append("=" * 50)
    report_lines.append("ANALYSIS RESULTS")
    report_lines.append("=" * 50)
    report_lines.append(f"Total markdown files processed: {len(md_files)}")
    report_lines.append(f"Total sources found:            {total_sources_count}")
    report_lines.append(f"Unique sources:                 {len(source_registry)}")
    report_lines.append(f"Duplicate sources:              {len(duplicates)}")
    report_lines.append("=" * 50 + "\n")

    if duplicates:
        report_lines.append("DUPLICATE SOURCES DETAILS:")
        report_lines.append("-" * 50)
        sorted_duplicates = sorted(duplicates.items(), key=lambda item: len(item[1]), reverse=True)
        for idx, (norm_name, occurrences) in enumerate(sorted_duplicates, start=1):
            report_lines.append(f"{idx}. {occurrences[0][1]}")
            report_lines.append(f"   Occurrences: {len(occurrences)}")
            report_lines.append("   Found in:")
            for file_name, orig_entry in occurrences:
                report_lines.append(f"     - {file_name}")
            report_lines.append("-" * 50)
    else:
        report_lines.append("No duplicate sources found! All references are unique.")

    return "\n".join(report_lines)

def main():
    print(f"Scanning references directory: {REFERENCES_DIR}")
    
    if not REFERENCES_DIR.exists():
        print(f"Error: References directory {REFERENCES_DIR} does not exist!", file=sys.stderr)
        sys.exit(1)

    # Find all Markdown files
    md_files = sorted(list(REFERENCES_DIR.glob("*.md")))
    if not md_files:
        print("No markdown files found in the references directory.")
        sys.exit(0)

    print(f"Found {len(md_files)} markdown files to process.")

    # Step 1: Analyze and cache file data
    file_data = []
    source_registry = defaultdict(list)
    total_sources_count = 0

    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading file {file_path.name}: {e}", file=sys.stderr)
            continue

        # Extract set name (everything before the last space and number)
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
                file_path.unlink()
                print(f"  --> Deleted empty file: {file_info['name']}")

    print("\n" + "=" * 50)
    print("CLEANUP SUMMARY")
    print("=" * 50)
    print(f"Duplicate sources removed:      {removed_count}")
    print(f"Files modified/deleted:         {modified_files_count}")
    print("=" * 50 + "\n")

    # Step 3: Regenerate and save the post-cleanup report
    print(f"Generating updated duplicates report to: {REPORT_PATH}")
    updated_md_files = sorted(list(REFERENCES_DIR.glob("*.md")))
    report_content = generate_report_content(updated_md_files)
    REPORT_PATH.write_text(report_content, encoding="utf-8")
    print("Report written successfully.")

if __name__ == "__main__":
    main()
