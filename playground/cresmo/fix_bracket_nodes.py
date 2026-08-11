#!/usr/bin/env python3
"""Clean bracketed filenames and H1 titles across Cresmo wiki and merge colliding files."""

import json
import re
from pathlib import Path

WIKI_DIR = Path("/mnt/gamer_d/Fausto Stangler/Documentos/Python/PES/playground/cresmo/wiki")
INDEX_FILE = WIKI_DIR / "_index.json"


def clean_title_str(title: str) -> str:
    """Remove brackets [[ and ]] from title string."""
    return re.sub(r'\[\[(.*?)\]\]', r'\1', title).strip()


def parse_frontmatter_and_body(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter dictionary and markdown body."""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    fm_raw = parts[1]
    body = parts[2]

    # Extract simple key-values
    fm_dict = {
        "type": "",
        "content": [],
        "domain": "",
        "cluster": "",
        "source": "",
        "aliases": []
    }

    lines = fm_raw.splitlines()
    in_content = False

    for line in lines:
        stripped = line.strip()
        if line.startswith("type:"):
            fm_dict["type"] = line.split(":", 1)[1].strip()
            in_content = False
        elif line.startswith("domain:"):
            fm_dict["domain"] = line.split(":", 1)[1].strip()
            in_content = False
        elif line.startswith("cluster:"):
            fm_dict["cluster"] = line.split(":", 1)[1].strip()
            in_content = False
        elif line.startswith("source:"):
            fm_dict["source"] = line.split(":", 1)[1].strip()
            in_content = False
        elif line.startswith("aliases:"):
            aliases_raw = line.split(":", 1)[1].strip()
            try:
                fm_dict["aliases"] = json.loads(aliases_raw)
            except Exception:
                fm_dict["aliases"] = [a.strip().strip("'\"") for a in aliases_raw.strip("[]").split(",") if a.strip()]
            in_content = False
        elif line.startswith("content:"):
            in_content = True
        elif in_content:
            if re.match(r"^[a-zA-Z0-9_-]+:", line):
                in_content = False
            elif stripped.startswith("- "):
                fm_dict["content"].append(stripped[2:].strip().strip("'\""))

    return fm_dict, body


def format_markdown_file(fm: dict, clean_title: str, body: str) -> str:
    """Format markdown file with clean H1 and normalized frontmatter."""
    # Ensure H1 title is clean (no [[ ]])
    body_lines = body.splitlines()
    new_body_lines = []
    h1_found = False

    for line in body_lines:
        if not h1_found and line.strip().startswith("# "):
            new_body_lines.append(f"# {clean_title}")
            h1_found = True
        else:
            new_body_lines.append(line)

    if not h1_found:
        new_body_lines.insert(0, f"# {clean_title}\n")

    # Format frontmatter
    fm_lines = []
    if fm.get("type"):
        fm_lines.append(f"type: {fm['type']}")

    if fm.get("content"):
        fm_lines.append("content:")
        seen = set()
        for c in fm["content"]:
            if c not in seen:
                seen.add(c)
                fm_lines.append(f"  - {c}")

    if fm.get("domain"):
        fm_lines.append(f"domain: {fm['domain']}")

    if fm.get("cluster"):
        fm_lines.append(f"cluster: {fm['cluster']}")

    if fm.get("source"):
        fm_lines.append(f"source: {fm['source']}")

    if fm.get("aliases"):
        # Format aliases list nicely
        aliases_json = json.dumps(list(dict.fromkeys(fm["aliases"])), ensure_ascii=False)
        fm_lines.append(f"aliases: {aliases_json}")

    fm_str = "\n".join(fm_lines)
    body_str = "\n".join(new_body_lines)

    return f"---{chr(10)}{fm_str}{chr(10)}---{chr(10)}{body_str}"


def merge_files(primary_path: Path, secondary_path: Path, clean_title: str):
    """Merge secondary_path into primary_path and remove secondary_path."""
    print(f"  🔄 Merging: {secondary_path.name} -> {primary_path.name}")
    text1 = primary_path.read_text(encoding="utf-8")
    text2 = secondary_path.read_text(encoding="utf-8")

    fm1, body1 = parse_frontmatter_and_body(text1)
    fm2, body2 = parse_frontmatter_and_body(text2)

    # Merge frontmatter
    merged_fm = {
        "type": fm1.get("type") or fm2.get("type") or "concept",
        "content": list(dict.fromkeys(fm1.get("content", []) + fm2.get("content", []))),
        "domain": fm1.get("domain") or fm2.get("domain") or "",
        "cluster": fm1.get("cluster") or fm2.get("cluster") or "",
        "source": fm1.get("source") or fm2.get("source") or "",
        "aliases": list(dict.fromkeys(fm1.get("aliases", []) + fm2.get("aliases", []))),
    }

    # Merge bodies section by section
    merged_body_lines = []
    lines1 = body1.splitlines()
    lines2 = body2.splitlines()

    # Simple non-destructive merge: preserve lines from body1, append non-duplicate lines from body2
    seen_lines = set(l.strip() for l in lines1 if l.strip())
    merged_body_lines = list(lines1)

    for l in lines2:
        stripped = l.strip()
        if stripped and not stripped.startswith("# ") and stripped not in seen_lines:
            merged_body_lines.append(l)
            seen_lines.add(stripped)

    merged_body = "\n".join(merged_body_lines)
    final_content = format_markdown_file(merged_fm, clean_title, merged_body)

    primary_path.write_text(final_content, encoding="utf-8")
    secondary_path.unlink()  # Remove secondary file


def run_fix():
    md_files = list(WIKI_DIR.rglob("*.md"))
    print(f"Scanning {len(md_files)} markdown files in {WIKI_DIR}...")

    # Step 1: Handle bracketed filenames
    bracket_files = [f for f in md_files if "[[" in f.name or "]]" in f.name]
    print(f"Found {len(bracket_files)} files with brackets in filename.")

    for bfile in bracket_files:
        clean_name = clean_title_str(bfile.stem) + ".md"
        target_path = bfile.parent / clean_name

        if target_path.exists() and target_path != bfile:
            merge_files(target_path, bfile, clean_title_str(bfile.stem))
        else:
            # Simple rename + clean header
            text = bfile.read_text(encoding="utf-8")
            fm, body = parse_frontmatter_and_body(text)
            clean_t = clean_title_str(bfile.stem)
            new_content = format_markdown_file(fm, clean_t, body)

            target_path.write_text(new_content, encoding="utf-8")
            bfile.unlink()
            print(f"  ✓ Renamed: {bfile.name} -> {target_path.name}")

    # Step 2: Clean H1 titles in all remaining files
    all_files = list(WIKI_DIR.rglob("*.md"))
    title_fixed_count = 0

    for f in all_files:
        text = f.read_text(encoding="utf-8")
        clean_t = clean_title_str(f.stem)

        # Check if H1 has [[
        if re.search(r'^#\s+\[\[', text, re.MULTILINE):
            fm, body = parse_frontmatter_and_body(text)
            new_content = format_markdown_file(fm, clean_t, body)
            f.write_text(new_content, encoding="utf-8")
            title_fixed_count += 1
            print(f"  ✓ Cleaned H1 title in: {f.relative_to(WIKI_DIR)}")

    # Step 3: Update _index.json
    if INDEX_FILE.exists():
        print("\nUpdating _index.json entries...")
        index_data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        notes = index_data.get("notes", {})
        new_notes = {}
        index_updated = False

        for title, info in notes.items():
            clean_title_key = clean_title_str(title)
            raw_path = info.get("path", "")
            clean_path = re.sub(r'\[\[(.*?)\]\]', r'\1', raw_path)

            if clean_title_key != title or clean_path != raw_path:
                index_updated = True

            info["path"] = clean_path
            new_notes[clean_title_key] = info

        index_data["notes"] = new_notes
        if index_updated:
            INDEX_FILE.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print("  ✓ Cleaned bracketed entries in _index.json")

    print(f"\nDone! Cleaned H1 titles in {title_fixed_count} files.")


if __name__ == "__main__":
    run_fix()
