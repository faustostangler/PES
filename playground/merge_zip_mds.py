#!/usr/bin/env python3
"""Extract and merge all .md files inside each .zip into a single .md file per zip."""

from pathlib import Path
import zipfile

# --- Config ---
TARGET_DIR = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/playground/imi")
SEPARATOR = "\n\n" + ("-" * 30) + "\n\n"
MAX_WORD_COUNT = 500_000


def decode_bytes(raw: bytes) -> str:
    """Safely decode bytes trying common text encodings."""
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def merge_zip_markdowns(zip_path: Path, output_dir: Path) -> list[Path]:
    """Extract and combine markdown files from a zip, splitting into _01, _02 subsets if > MAX_WORD_COUNT."""
    chunks: list[list[str]] = []
    current_chunk: list[str] = []
    current_word_count = 0

    with zipfile.ZipFile(zip_path, "r") as archive:
        md_names = sorted(
            name
            for name in archive.namelist()
            if name.lower().endswith(".md")
            and not name.startswith("__MACOSX")
            and not Path(name).name.startswith(".")
        )

        for name in md_names:
            raw_bytes = archive.read(name)
            text = decode_bytes(raw_bytes).strip()
            if not text:
                continue

            word_count = len(text.split())

            # If adding this source exceeds limit and current chunk already has content, start new chunk
            if current_chunk and (current_word_count + word_count > MAX_WORD_COUNT):
                chunks.append(current_chunk)
                current_chunk = [text]
                current_word_count = word_count
            else:
                current_chunk.append(text)
                current_word_count += word_count

    if current_chunk:
        chunks.append(current_chunk)

    output_files: list[Path] = []
    single_file = output_dir / f"{zip_path.stem}.md"

    if len(chunks) <= 1:
        # Fits in a single file
        content = SEPARATOR.join(chunks[0]) + "\n" if chunks else ""
        single_file.write_text(content, encoding="utf-8")
        output_files.append(single_file)
        # Clean up any leftover subset files from previous runs
        for old_subset in output_dir.glob(f"{zip_path.stem}_*.md"):
            old_subset.unlink(missing_ok=True)
    else:
        # Multiple subsets needed (_01, _02, ...)
        if single_file.exists():
            single_file.unlink()

        for idx, chunk in enumerate(chunks, start=1):
            subset_file = output_dir / f"{zip_path.stem}_{idx:02d}.md"
            content = SEPARATOR.join(chunk) + "\n"
            subset_file.write_text(content, encoding="utf-8")
            output_files.append(subset_file)

    return output_files


def main() -> None:
    import sys

    assert TARGET_DIR.exists(), f"Target directory does not exist: {TARGET_DIR}"

    pattern = f"*{sys.argv[1]}*.zip" if len(sys.argv) > 1 else "*.zip"
    zip_files = sorted(TARGET_DIR.glob(pattern))
    assert len(zip_files) > 0, f"No .zip files matching '{pattern}' found in {TARGET_DIR}"

    print(f"Found {len(zip_files)} zip file(s) matching '{pattern}'. Processing with max {MAX_WORD_COUNT:,} words/file...\n")

    created_files: list[Path] = []
    for zip_file in zip_files:
        out_paths = merge_zip_markdowns(zip_file, TARGET_DIR)
        for out_path in out_paths:
            assert out_path.exists(), f"Failed to generate {out_path.name}"
            assert out_path.stat().st_size > 0, f"File {out_path.name} is empty"
            created_files.append(out_path)
            words = len(out_path.read_text(encoding="utf-8").split())
            print(f"  ✓ {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB, {words:,} words)")

    print(f"\nSuccessfully generated {len(created_files)} markdown file(s) in {TARGET_DIR}.")


if __name__ == "__main__":
    main()
