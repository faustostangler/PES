#!/usr/bin/env python3
"""Convert PDF documents into high-quality MP3 audiobooks using pypdf and edge-tts."""

import argparse
import asyncio
import io
import re
import sys
import time
import unicodedata
from pathlib import Path

import edge_tts
import pypdf

# --- Configuration Defaults ---
DEFAULT_PDF = Path("fine-tuning-de-llms-na-pratica.pdf")
DEFAULT_VOICE = "pt-BR-AntonioNeural"
DEFAULT_CHUNK_SIZE = 3500


def clean_page_text(raw_text: str) -> str:
    """Normalize unicode and strip recurring header, footer, and watermark patterns.

    >>> clean_page_text("ﬁne-tuning\\nLicenciado para - USER - 123\\nPage content")
    'fine-tuning\\nPage content'
    """
    normalized = unicodedata.normalize("NFKC", raw_text)
    filtered_lines = []

    for line in normalized.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Strip Eduzz license watermark
        if re.search(r"Licenciado para|Protegido por Eduzz", stripped, re.I):
            continue
        # Strip recurring top running header
        if re.search(r"^FINE-TUNING DE LLMS NA PRÁTICA$", stripped, re.I):
            continue
        # Strip recurring chapter running footers (e.g., "CAPÍTULO 1. ... 7")
        if re.search(r"^CAPÍTULO \d+\..*\s+\d+$", stripped, re.I):
            continue
        # Strip standalone page numbers
        if re.fullmatch(r"\d+", stripped):
            continue
        filtered_lines.append(stripped)

    return "\n".join(filtered_lines)


def split_text_into_chunks(text: str, max_chars: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    """Split text into manageable chunks respecting sentence and paragraph boundaries.

    >>> split_text_into_chunks("Short text.", max_chars=100)
    ['Short text.']
    >>> len(split_text_into_chunks("Sentence one. Sentence two.", max_chars=20))
    2
    """
    if len(text) <= max_chars:
        return [text] if text.strip() else []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for para in paragraphs:
        if current_length + len(para) + 2 <= max_chars:
            current_chunk.append(para)
            current_length += len(para) + 2
        else:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_length = 0

            # If single paragraph is larger than max_chars, split by sentence
            if len(para) > max_chars:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sentence in sentences:
                    if current_length + len(sentence) + 1 <= max_chars:
                        current_chunk.append(sentence)
                        current_length += len(sentence) + 1
                    else:
                        if current_chunk:
                            chunks.append(" ".join(current_chunk))
                        current_chunk = [sentence]
                        current_length = len(sentence)
            else:
                current_chunk.append(para)
                current_length = len(para)

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return [c.strip() for c in chunks if c.strip()]


def extract_pdf_text(pdf_path: Path, start_page: int = 1, end_page: int | None = None) -> str:
    """Extract and sanitize text across specified page range of a PDF."""
    assert pdf_path.exists(), f"PDF file not found: {pdf_path}"

    reader = pypdf.PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    assert total_pages > 0, "PDF has no pages"

    last_page = min(end_page or total_pages, total_pages)
    first_page = max(1, start_page)

    extracted_pages: list[str] = []
    for page_idx in range(first_page - 1, last_page):
        page = reader.pages[page_idx]
        raw_text = page.extract_text() or ""
        cleaned = clean_page_text(raw_text)
        if cleaned:
            extracted_pages.append(cleaned)

    full_text = "\n\n".join(extracted_pages)
    assert full_text.strip(), f"No readable text extracted from pages {first_page} to {last_page}"
    return full_text


async def synthesize_chunk_to_bytes(text: str, voice: str, rate: str = "+0%", max_retries: int = 3) -> bytes:
    """Synthesize text chunk to MP3 bytes using Microsoft Edge TTS with automatic retries."""
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buffer.write(chunk["data"])
            audio_bytes = buffer.getvalue()
            assert len(audio_bytes) > 0, "Empty audio buffer returned by TTS"
            return audio_bytes
        except Exception as err:
            if attempt == max_retries:
                raise RuntimeError(f"Failed to synthesize chunk after {max_retries} attempts: {err}") from err
            await asyncio.sleep(1.5 * attempt)
    return b""


async def convert_pdf(
    pdf_path: Path,
    output_path: Path,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    start_page: int = 1,
    end_page: int | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> None:
    """Execute the full PDF to MP3 conversion pipeline."""
    print(f"Loading PDF: {pdf_path}")
    text = extract_pdf_text(pdf_path, start_page=start_page, end_page=end_page)
    words_count = len(text.split())
    chars_count = len(text)
    print(f"Extracted text: {chars_count:,} characters ({words_count:,} words)")

    chunks = split_text_into_chunks(text, max_chars=chunk_size)
    assert len(chunks) > 0, "Chunking produced no text chunks"
    print(f"Created {len(chunks)} audio synthesis chunks (target max ~{chunk_size} chars/chunk)")

    start_time = time.time()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as outfile:
        for idx, chunk in enumerate(chunks, 1):
            print(f"[{idx:02d}/{len(chunks):02d}] Synthesizing {len(chunk):,} chars with voice '{voice}'...", end="", flush=True)
            chunk_start = time.time()
            audio_bytes = await synthesize_chunk_to_bytes(chunk, voice=voice, rate=rate)
            outfile.write(audio_bytes)
            outfile.flush()
            print(f" Done ({len(audio_bytes):,} bytes, {time.time() - chunk_start:.1f}s)")

    elapsed = time.time() - start_time
    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    assert output_path.exists(), f"Target file was not created: {output_path}"
    assert output_path.stat().st_size > 0, "Target MP3 file is empty"

    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print(f"Output MP3:     {output_path.resolve()}")
    print(f"Total Size:     {file_size_mb:.2f} MB")
    print(f"Total Chunks:   {len(chunks)}")
    print(f"Total Time:     {elapsed:.1f}s")
    print("=" * 60)


def main() -> None:
    """Parse command line arguments and execute conversion."""
    parser = argparse.ArgumentParser(description="Convert PDF book into MP3 audio.")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF, help="Path to input PDF file")
    parser.add_argument("--output", type=Path, default=None, help="Path to output MP3 file (default: <pdf_stem>.mp3)")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help=f"Edge TTS voice (default: {DEFAULT_VOICE})")
    parser.add_argument("--rate", type=str, default="+0%", help="Playback speed adjustment, e.g. +10%%, +20%% (default: +0%%)")
    parser.add_argument("--start-page", type=int, default=1, help="First page to convert (1-indexed)")
    parser.add_argument("--end-page", type=int, default=None, help="Last page to convert (1-indexed, default: end of PDF)")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help="Max characters per chunk")

    args = parser.parse_args()
    pdf_path = args.pdf
    output_path = args.output or pdf_path.with_suffix(".mp3")

    asyncio.run(
        convert_pdf(
            pdf_path=pdf_path,
            output_path=output_path,
            voice=args.voice,
            rate=args.rate,
            start_page=args.start_page,
            end_page=args.end_page,
            chunk_size=args.chunk_size,
        )
    )


if __name__ == "__main__":
    main()
