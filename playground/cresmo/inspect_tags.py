#!/usr/bin/env python3
"""Inspect YAML frontmatters across all Markdown files in Cresmo wiki."""

from pathlib import Path

# --- Constants & Defaults ---
DEFAULT_WIKI_DIR: Path = Path(__file__).parent.resolve() / "wiki"
TAG_PREFIX_DELIMITER: str = "/"


def inspect(wiki_dir: Path = DEFAULT_WIKI_DIR) -> None:
    """Inspect discovered tag prefixes across all markdown files."""
    md_files = list(wiki_dir.rglob("*.md"))
    print(f"Total MD files: {len(md_files)}")
    tag_prefixes = set()

    for f in md_files:
        content = f.read_text(encoding="utf-8")
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        frontmatter = parts[1]
        for line in frontmatter.splitlines():
            line = line.strip()
            if line.startswith("- "):
                item = line[2:].strip()
                prefix = item.split(TAG_PREFIX_DELIMITER)[0] if TAG_PREFIX_DELIMITER in item else item
                tag_prefixes.add(prefix)

    print(f"Discovered tag prefixes: {sorted(tag_prefixes)}")


if __name__ == "__main__":
    inspect()
