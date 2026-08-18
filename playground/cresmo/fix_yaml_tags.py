#!/usr/bin/env python3
"""Format YAML tags in all Cresmo Markdown vault files to be strictly 1 tag per line."""

from pathlib import Path
import re

# --- Constants & Defaults ---
DEFAULT_WIKI_DIR: Path = Path(__file__).parent.resolve() / "wiki"

# --- Compiled Regexes ---
INLINE_TAGS_PATTERN: re.Pattern[str] = re.compile(r"^tags:\s*\[(.*)\]$")
YAML_KEY_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_-]+:")


def normalize_tags_in_content(content: str) -> str:
    """Find YAML frontmatter and format tags block to have one tag per line."""
    if not content.startswith("---"):
        return content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return content

    frontmatter = parts[1]
    body = parts[2]

    lines = frontmatter.splitlines()
    new_lines = []
    in_tags = False

    for line in lines:
        stripped = line.strip()
        if line.startswith("tags:"):
            in_tags = True
            inline_match = INLINE_TAGS_PATTERN.match(line)
            if inline_match:
                raw_tags = inline_match.group(1).split(",")
                new_lines.append("tags:")
                for t in raw_tags:
                    clean_t = t.strip().strip("'\"")
                    if clean_t:
                        new_lines.append(f"  - {clean_t}")
                in_tags = False
            else:
                new_lines.append("tags:")
            continue

        if in_tags:
            if YAML_KEY_PATTERN.match(line) or line.startswith("---"):
                in_tags = False
                new_lines.append(line)
                continue

            if line.strip().startswith("- "):
                raw_item = line.strip()[2:].strip()
                tags = [t.strip().strip("'\"") for t in raw_item.split(",")]
                for t in tags:
                    if t:
                        new_lines.append(f"  - {t}")
                continue
            elif line.strip() == "":
                in_tags = False
                new_lines.append(line)
                continue

        new_lines.append(line)

    new_frontmatter = "\n".join(new_lines)
    return f"---{new_frontmatter}\n---{body}"


def process_all_files(wiki_dir: Path = DEFAULT_WIKI_DIR) -> None:
    """Scan all Markdown files in wiki directory and normalize tag layout."""
    md_files = list(wiki_dir.rglob("*.md"))
    modified_count = 0

    print(f"Scanning {len(md_files)} markdown files in {wiki_dir}...")

    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8")
            new_text = normalize_tags_in_content(text)
            if new_text != text:
                md_file.write_text(new_text, encoding="utf-8")
                modified_count += 1
                print(f"  ✓ Fixed: {md_file.relative_to(wiki_dir)}")
        except Exception as e:
            print(f"  ❌ Error processing {md_file}: {e}")

    print(f"\nDone! Modified {modified_count} out of {len(md_files)} files.")


if __name__ == "__main__":
    process_all_files()
