#!/usr/bin/env python3
"""Concatenate enriched markdown documents into master files per folder.

This script scans each subfolder in the `enriched` directory, concatenates all
`*.md` files found within it, and outputs the result to the `master` directory
as `{folder}.md`. If the total word count exceeds the maximum threshold
(default 500,000 words), the output is automatically split into numbered
files: `{folder}-1.md`, `{folder}-2.md`, etc.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


DEFAULT_MAX_WORDS = 500_000


def count_words(text: str) -> int:
    """Count the total number of whitespace-delimited words in a string.

    Args:
        text: The string to count words in.

    Returns:
        The total number of words.
    """
    return len(text.split())


def split_text_by_words(text: str, max_words: int) -> list[str]:
    """Split a single large text into chunks with at most `max_words` words.

    Args:
        text: The text content to split.
        max_words: Maximum word limit per chunk.

    Returns:
        A list of chunked strings.
    """
    words = text.split()
    if len(words) <= max_words:
        return [text]

    chunks = []
    # Split by word boundaries
    for i in range(0, len(words), max_words):
        chunk_words = words[i : i + max_words]
        chunks.append(" ".join(chunk_words))
    return chunks


def concatenate_folder(
    folder_path: Path,
    output_dir: Path,
    max_words: int = DEFAULT_MAX_WORDS,
) -> list[tuple[Path, int]]:
    """Concatenate all markdown files within a folder into master document(s).

    Args:
        folder_path: The subfolder containing `.md` files.
        output_dir: The destination directory for master files.
        max_words: Word threshold before splitting into multiple parts.

    Returns:
        A list of tuples containing (written_file_path, word_count).
    """
    folder_name = folder_path.name
    md_files = sorted(folder_path.glob("*.md"))

    if not md_files:
        print(f"  [SKIP] No .md files found in '{folder_path}'")
        return []

    # Clean up any existing master files for this folder
    for existing_file in output_dir.glob(f"{folder_name}*.md"):
        # Match either exact {folder_name}.md or {folder_name}-[0-9]+.md
        if existing_file.name == f"{folder_name}.md" or existing_file.name.startswith(f"{folder_name}-"):
            existing_file.unlink(missing_ok=True)

    chunks: list[list[str]] = [[]]
    current_chunk_words = 0

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = md_file.read_text(encoding="utf-8", errors="replace")

        # Strip trailing/leading spaces to keep consistent formatting
        content = content.strip()
        if not content:
            continue

        file_words = count_words(content)

        # If a single file exceeds max_words on its own
        if file_words > max_words:
            # Finalize current chunk if non-empty
            if chunks[-1]:
                chunks.append([])
                current_chunk_words = 0

            sub_chunks = split_text_by_words(content, max_words)
            for sub_chunk in sub_chunks:
                chunks[-1].append(sub_chunk)
                chunks.append([])
            chunks.pop()  # Remove trailing empty chunk
            current_chunk_words = count_words(chunks[-1][0]) if chunks and chunks[-1] else 0
            continue

        # If adding this file exceeds limit, rollover to next chunk
        if current_chunk_words + file_words > max_words and chunks[-1]:
            chunks.append([])
            current_chunk_words = 0

        chunks[-1].append(content)
        current_chunk_words += file_words

    # Filter out empty chunks
    valid_chunks = [c for c in chunks if c]

    if not valid_chunks:
        print(f"  [EMPTY] No content to write for '{folder_name}'")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    written_files: list[tuple[Path, int]] = []

    # If only 1 chunk, name it {folder}.md; otherwise {folder}-1.md, {folder}-2.md, ...
    is_multi_part = len(valid_chunks) > 1

    for idx, chunk in enumerate(valid_chunks, start=1):
        filename = f"{folder_name}-{idx}.md" if is_multi_part else f"{folder_name}.md"
        target_path = output_dir / filename
        merged_text = "\n\n---\n\n".join(chunk) + "\n"
        target_path.write_text(merged_text, encoding="utf-8")

        total_words = count_words(merged_text)
        written_files.append((target_path, total_words))

    return written_files


def run_concatenation(
    enriched_dir: Path,
    master_dir: Path,
    max_words: int = DEFAULT_MAX_WORDS,
) -> None:
    """Scan all subfolders in enriched directory and concatenate markdown files.

    Args:
        enriched_dir: Path to the enriched root directory.
        master_dir: Path to the output master directory.
        max_words: Maximum word limit per master document.
    """
    if not enriched_dir.exists() or not enriched_dir.is_dir():
        print(f"Error: Enriched directory does not exist: {enriched_dir}", file=sys.stderr)
        sys.exit(1)

    subfolders = sorted([d for d in enriched_dir.iterdir() if d.is_dir()])

    if not subfolders:
        print(f"Warning: No subfolders found in {enriched_dir}")
        return

    print(f"Found {len(subfolders)} folder(s) in {enriched_dir}")
    print(f"Output directory: {master_dir}")
    print(f"Max words per document: {max_words:,}\n")

    total_master_files = 0
    total_words_written = 0

    for folder in subfolders:
        print(f"Processing '{folder.name}'...")
        written = concatenate_folder(folder, master_dir, max_words=max_words)
        for out_file, words in written:
            print(f"  ✓ Created: {out_file.name} ({words:,} words)")
            total_master_files += 1
            total_words_written += words

    print("\n" + "=" * 60)
    print(f"Finished: {total_master_files} master file(s) generated ({total_words_written:,} total words).")


def main() -> None:
    """CLI entrypoint."""
    base_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Concatenate enriched markdown files into master documents per folder."
    )
    parser.add_argument(
        "--enriched-dir",
        type=Path,
        default=base_dir / "enriched",
        help="Path to the enriched directory containing subfolders.",
    )
    parser.add_argument(
        "--master-dir",
        type=Path,
        default=base_dir / "master",
        help="Path to the master output directory.",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=DEFAULT_MAX_WORDS,
        help=f"Maximum word limit per master document (default: {DEFAULT_MAX_WORDS:,}).",
    )

    args = parser.parse_args()
    run_concatenation(
        enriched_dir=args.enriched_dir.resolve(),
        master_dir=args.master_dir.resolve(),
        max_words=args.max_words,
    )


if __name__ == "__main__":
    main()
