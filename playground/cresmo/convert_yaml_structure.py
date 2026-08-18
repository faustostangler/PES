#!/usr/bin/env python3
"""Convert YAML frontmatter in all Cresmo wiki files to new structure:
type, content, domain, cluster, source, aliases (without tags: or type/ tag)."""

from pathlib import Path
import re

# --- Constants & Defaults ---
DEFAULT_WIKI_DIR: Path = Path(__file__).parent.resolve() / "wiki"
TAG_TYPE_PREFIX: str = "type/"
TAG_CONTENT_PREFIX: str = "content/"
TAG_DOMAIN_PREFIX: str = "domain/"
TAG_CLUSTER_PREFIX: str = "cluster/"
TAG_SOURCE_PREFIX: str = "source/"

# --- Compiled Regexes ---
INLINE_TAGS_PATTERN: re.Pattern[str] = re.compile(r"^tags:\s*\[(.*)\]$")
YAML_KEY_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_-]+:")


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

        if line.startswith("domain:") and not line.startswith(TAG_DOMAIN_PREFIX):
            domain_val = line.split(":", 1)[1].strip()
            in_tags = False
            continue

        if line.startswith("cluster:") and not line.startswith(TAG_CLUSTER_PREFIX):
            cluster_val = line.split(":", 1)[1].strip()
            in_tags = False
            continue

        if line.startswith("source:") and not line.startswith(TAG_SOURCE_PREFIX):
            source_val = line.split(":", 1)[1].strip()
            in_tags = False
            continue

        if line.startswith("content:") and not line.startswith(TAG_CONTENT_PREFIX):
            in_tags = False
            continue

        if line.startswith("tags:"):
            in_tags = True
            in_aliases = False
            # Check inline list tags: [tag1, tag2]
            inline_match = INLINE_TAGS_PATTERN.match(line)
            if inline_match:
                raw_tags = [t.strip().strip("'\"") for t in inline_match.group(1).split(",")]
                for tag in raw_tags:
                    process_tag(tag, content_list, domain_val, cluster_val, source_val)
                in_tags = False
            continue

        if in_tags:
            if YAML_KEY_PATTERN.match(line):
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


def process_tag(tag: str, content_list: list, domain_hint: str = "", cluster_hint: str = "", source_hint: str = "") -> tuple[str, str, str]:
    """Parse single tag item and assign to appropriate field."""
    domain_val = domain_hint
    cluster_val = cluster_hint
    source_val = source_hint

    if tag.startswith(TAG_TYPE_PREFIX):
        pass
    elif tag.startswith(TAG_CONTENT_PREFIX):
        item = tag[len(TAG_CONTENT_PREFIX):].strip()
        if item:
            content_list.append(item)
    elif tag.startswith(TAG_DOMAIN_PREFIX):
        domain_val = tag[len(TAG_DOMAIN_PREFIX):].strip()
    elif tag.startswith(TAG_CLUSTER_PREFIX):
        cluster_val = tag[len(TAG_CLUSTER_PREFIX):].strip()
    elif tag.startswith(TAG_SOURCE_PREFIX):
        source_val = tag[len(TAG_SOURCE_PREFIX):].strip()
    else:
        # Generic tag becomes content tag
        if tag:
            content_list.append(tag)

    return domain_val, cluster_val, source_val


def main(wiki_dir: Path = DEFAULT_WIKI_DIR) -> None:
    md_files = list(wiki_dir.rglob("*.md"))
    modified_count = 0

    print(f"Converting YAML frontmatter in {len(md_files)} markdown files...")

    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        new_text = transform_frontmatter(text)
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            modified_count += 1
            print(f"  ✓ Transformed: {md_file.relative_to(wiki_dir)}")

    print(f"\nDone! Successfully transformed {modified_count} out of {len(md_files)} files.")


if __name__ == "__main__":
    main()
