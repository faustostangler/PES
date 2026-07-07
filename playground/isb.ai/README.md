# ISB.AI — Intelligent Second Brain Ingestion & Curadoria

An automated, premium knowledge ingestion and curation system that consumes YouTube video feeds/playlists, transcribes content, structures insights into atomic facts or technical notes, and dynamically builds an Obsidian-based Map of Content (MOC) graph.

---

## 🏛️ Architecture & Layout

This project implements a flat, direct **KISS "GOD Monolith"** layout. All orchestrators, crawlers, and processors reside directly in the root directory to maintain high cohesion and low coupling across methods, facilitating easy readability and zero-overhead imports.

```
playground/isb.ai/
├── downloader.py             # yt-dlp subtitles extractor and OGG audio downloader
├── transcriber.py            # Whisper transcription handler (local fallback)
├── helper.py                 # Common YAML frontmatter parser and text sanitizers
├── sync_channels.py          # Ingestion orchestrator (syncs latest channel uploads)
├── gemini_web.py             # Playwright browser automation for Gemini Web UI
├── main.py                   # GOD Monolith CLI Entrypoint (sync & process subcommands)
├── sanity_check.py           # Unit tests & verification suite
├── playlist.txt              # Feed seed YouTube URLs
├── processed_gemini.json     # Idempotency log for Gemini processed blocks
├── raw/                      # Raw text transcripts segregated by channel
└── wiki/                     # Curated Obsidian vault output
    ├── MOCs/                 # Automatically generated and linked Maps of Content
    └── *.md                  # Atomic notes (R_ reference, A_ action, or News facts)
```

---

## ⚡ Pipelines

### 1. Ingestion: First Pass (`main.py sync`)
* Fetches the uploads playlist of channels defined in `playlist.txt`.
* Queries recent video uploads within a configurable temporal limit (`--days`).
* Checks subtitles availability:
  1. **Tier 1:** Parse YouTube JSON3 subtitles into structured paragraphs.
  2. **Tier 2:** Parse YouTube SRV1 subtitles.
  3. **Tier 3 (Fallback):** Download audio stream as `.ogg` and transcribe locally using Whisper.
* Consolidates transcripts inside monthly text files in `raw/[Channel_Name]/[Channel_Name] - YYYY-MM.txt` containing YAML headers.

### 2. Curadoria: Second Pass (`main.py process`)
* Scans `raw/` directories to extract individual video blocks.
* Skips already-processed blocks idempotently using `processed_gemini.json`.
* Launches a persistent Playwright browser instance connected to `gemini.google.com` (preserving your Google session login cookies).
* Classifies the channel deterministically in Python (`news` vs `technical`).
* Performs **Absolute Temporal Anchoring**: extracts the video date from YAML, feeds it as `[DATA_YAML]` reference in system prompts, and converts all relative references into absolute ISO 8601 format (`YYYY-MM-DD`).
* Sweeps `wiki/MOCs/` folder to build a catalog of existing Maps of Content.
* Submits the transcript, MOC list, and temporal anchor to Gemini Web using the structured code block envelope technique (ensuring raw markdown syntax characters like `#` and `---` are not lost during rendering).
* Parses Gemini's output boundaries, saves notes under `wiki/`, and dynamically updates/creates Map of Content indexes in `wiki/MOCs/`.
* Cleans up by deleting the active Gemini chat thread to keep your account history pristine.

---

## 📑 Curadoria Output Formats

### News Channels (`news`)
Generates independent atomic fact notes with:
* **Nominal Title:** Sentence nominal describing the fact.
* **YAML Frontmatter:** Absolute date of the event and list of entities involved.
* **Context Body:** Concise summary and connections using double-brackets (`[[Link]]`).

### Technical Channels (`technical`)
Applies universal RAE-PKM ontology, partitioning technical knowledge into reciprocal notes:
* **Reference Note (`R_[Conceito].md`):** Durable conceptual truths, laws, theories, formulas.
* **Action Note (`A_[Procedimento].md`):** Volatile step-by-step procedures, terminal commands, version-specific syntaxes.

---

## 🚀 Setup & Execution

### 1. Requirements
Ensure you are running on your Python environment (Python 3.13+) and have Playwright dependencies installed:
```bash
# Install dependencies
uv pip install -r ../../pyproject.toml

# Install Playwright browser binaries
playwright install chromium
```

### 2. Syncing Channels (First Pass)
Download new video transcripts uploaded in the last 7 days:
```bash
python main.py sync --days 7
```

### 3. Processing Transcripts (Second Pass)
Verify pending blocks without launching the browser session (Dry-Run):
```bash
python main.py process --dry-run
```

Run the Playwright Gemini automation on the first 5 pending blocks (it will open a window and wait for confirmation of your Google session during the first launch):
```bash
python main.py process --limit 5
```

### 4. Verification Suite
Verify formatting utilities, date calculations, and YAML parsing functions:
```bash
python sanity_check.py
```
