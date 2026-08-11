#!/usr/bin/env python3
"""Convert YAML frontmatter in all Cresmo wiki files to new structure:
type, content, domain, cluster, source, aliases (without tags: or type/ tag)."""

from pathlib import Path
import re

WIKI_DIR = Path("/mnt/gamer_d/Fausto Stangler/Documentos/Python/PES/playground/cresmo/wiki")

def transform_frontmatter(content: str) -> str:
    """Transform YAML frontmatter from old tags-based format to new structured format."""
    if not content.startswith("---"):
        return content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return content

    frontmatter_text = parts[1]
    body = parts[2]

    # Parse key values
    note_type = ""
    aliases_line = ""
    content_list = []
    domain_val = ""
    cluster_val = ""
    source_val = ""

    lines = frontmatter_text.splitlines()
    in_tags = False
    in_aliases = False

    for line in lines:
        stripped = line.strip()

        # Existing top-level keys
        if line.startswith("type:"):
            note_type = line.split(":", 1)[1].strip()
            in_tags = False
            in_aliases = False
            continue

        if line.startswith("aliases:"):
            aliases_line = line.strip()
            in_tags = False
            in_aliases = True
            continue

        if line.startswith("domain:") and not line.startswith("domain/"):
            domain_val = line.split(":", 1)[1].strip()
            in_tags = False
            continue

        if line.startswith("cluster:") and not line.startswith("cluster/"):
            cluster_val = line.split(":", 1)[1].strip()
            in_tags = False
            continue

        if line.startswith("source:") and not line.startswith("source/"):
            source_val = line.split(":", 1)[1].strip()
            in_tags = False
            continue

        if line.startswith("content:") and not line.startswith("content/"):
            in_tags = False
            continue

        if line.startswith("tags:"):
            in_tags = True
            in_aliases = False
            # Check inline list tags: [tag1, tag2]
            inline_match = re.match(r"^tags:\s*\[(.*)\]$", line)
            if inline_match:
                raw_tags = [t.strip().strip("'\"") for t in inline_match.group(1).split(",")]
                for tag in raw_tags:
                    process_tag(tag, content_list, domain_val, cluster_val, source_val)
                in_tags = False
            continue

        if in_tags:
            if re.match(r"^[a-zA-Z0-9_-]+:", line):
                in_tags = False
                continue

            if stripped.startswith("- "):
                tag_item = stripped[2:].strip().strip("'\"")
                # Split comma if present
                tags = [t.strip().strip("'\"") for t in tag_item.split(",")]
                for tag in tags:
                    d, c, s = process_tag(tag, content_list)
                    if d and not domain_val:
                        domain_val = d
                    if c and not cluster_val:
                        cluster_val = c
                    if s and not source_val:
                        source_val = s
                continue
            elif stripped == "":
                in_tags = False
                continue

        if in_aliases and line.startswith("  - "):
            aliases_line += "\n" + line

    # Build new frontmatter lines
    new_lines = []
    if note_type:
        new_lines.append(f"type: {note_type}")

    if content_list:
        new_lines.append("content:")
        # Deduplicate while preserving order
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
    return f"---{chr(10)}{new_frontmatter}{chr(10)}---{body}"


def process_tag(tag: str, content_list: list) -> tuple[str, str, str]:
    """Parse single tag item and assign to appropriate field."""
    domain_val = ""
    cluster_val = ""
    source_val = ""

    if tag.startswith("type/"):
        # Ignore type/ tag
        pass
    elif tag.startswith("content/"):
        item = tag[len("content/"):].strip()
        if item:
            content_list.append(item)
    elif tag.startswith("domain/"):
        domain_val = tag[len("domain/"):].strip()
    elif tag.startswith("cluster/"):
        cluster_val = tag[len("cluster/"):].strip()
    elif tag.startswith("source/"):
        source_val = tag[len("source/"):].strip()
    else:
        # Generic tag becomes content tag
        if tag:
            content_list.append(tag)

    return domain_val, cluster_val, source_val


def main():
    md_files = list(WIKI_DIR.rglob("*.md"))
    modified_count = 0

    print(f"Converting YAML frontmatter in {len(md_files)} markdown files...")

    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        new_text = transform_frontmatter(text)
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            modified_count += 1
            print(f"  ✓ Transformed: {md_file.relative_to(WIKI_DIR)}")

    print(f"\nDone! Successfully transformed {modified_count} out of {len(md_files)} files.")


if __name__ == "__main__":
    main()
