# Comprehensive ISB.AI Pipeline Plan: Ingestion to Reconciliation

This plan outlines the complete programmatic lifecycle of the Intelligent Second Brain (ISB.AI) system, spanning from raw data collection, multi-stage LLM enrichment, curation, and folder organization, up to weekly semantic maintenance.

---

## 🏛️ Pipeline Topology Overview

The system is structured as a **six-stage sequential pipeline**, combining fast local shell operations, Playwright-driven LLM synthesis via custom Gems, and automated graph reconciliation.

```mermaid
flowchart TD
    subgraph Stage 1: Ingest
        A[YouTube Playlist / RSS] -->|yt-dlp| B[Subtitles JSON3/SRV1]
        A -->|Audio Fallback| C[Local Whisper Transcription]
        B --> D[raw/ txt files per video]
        C --> D
    end

    subgraph Stage 2: Pre-process & Enrichment Gems
        D -->|Step 2.1: Detranscriptor Gem| E1[Structured Text Response]
        E1 -->|Step 2.2: Extractor Gem| E2[Knowledge Graph Structure]
        E2 -->|Step 2.3: Expander Gap Filler Gem x5| E3[Max-Expansion Compendium]
        E3 -->|Step 2.4: Downgrader Gem| E4[Upgraded Trimmed Compendium]
    end

    subgraph Stage 3: Curate
        E4 -->|Idempotency Filter| F[Pending Enriched Compendiums]
        F -->|Domain Classifier| G{Perennial vs Volatile?}
        G -->|Perennial| H[TECHNICAL Prompt]
        G -->|Volatile| I[NEWS Prompt]
        H -->|Playwright| J[Gemini Web UI]
        I -->|Playwright| J
    end

    subgraph Stage 4: Segment & Write
        J -->|Regex Parser| K[Extracted Note Files]
        K -->|resolve_note_path| L[(Folder Structure)]
        L -->|concepts/| M[R_Reference Notes]
        L -->|procedures/| N[A_Action Notes]
        L -->|chronicles/| O[Factual Chronicle Notes]
    end

    subgraph Stage 5: Connect
        L -->|MOC Registration| P[wiki/MOCs/]
        L -->|Vault Grep & Replace| Q[Inject Backlinks [[Note]]]
    end

    subgraph Stage 6: Reconcile
        Q -->|Weekly Schedule| R[Semantic Reconciliation]
        R -->|Gemini Analysis| S[Merge Synonyms & Fix Links]
    end
```

---

## 📑 Detailed Pipeline Steps

### Stage 1: Raw Ingestion (`main.py sync`)
* **Trigger**: Scheduled cron job or manual CLI execution.
* **Operations**:
  1. Reads target channel URLs from `playlist.txt`.
  2. Queries the YouTube API/feed via `yt-dlp` for videos uploaded within the last $N$ days.
  3. Extracts transcriptions using a **three-tier fallback strategy**:
     * **Tier 1**: Pulls native YouTube `json3` subtitles and reconstructs them into paragraphs.
     * **Tier 2**: Pulls `srv1` subtitles.
     * **Tier 3 (Fallback)**: Downloads the audio track as `.ogg` and runs local `Whisper` transcription.
  4. **Atomic Ingestion (SOTA)**: Saves the text transcript along with a YAML metadata header into isolated files per video: `raw/[Channel]/[Video_ID].txt` (or `.json`). This enables fast idempotency checks, clean git history, and simple individual parsing.

---

### Stage 2: Pre-process & Enrichment Gems
* **Trigger**: Executed programmatically post-ingestion via Playwright browser automation navigating to custom Gemini Gems.
* **Operations**:
  1. **Step 2.1: Detranscriptor Gem** ([cc00c0110bf0](https://gemini.google.com/gem/cc00c0110bf0)):
     * **Input**: Full raw transcript.
     * **Process**: Cleans spoken speech, corrects syntax, and returns a fully structured text response.
  2. **Step 2.2: Extractor Gem** ([f7c5da7814b4](https://gemini.google.com/gem/f7c5da7814b4)):
     * **Input**: Detranscribed text.
     * **Process**: Extracts relationships and structures a formal knowledge graph schema.
  3. **Step 2.3: Expander Gap Filler Gem** ([2dd102b966de](https://gemini.google.com/gem/2dd102b966de)):
     * **Input**: Knowledge graph structure.
     * **Process**: Iteratively submitted **5 times**. Each iteration systematically detects knowledge gaps, adds theoretical details, and expands notes (with permission to introduce tangent/context-risking expansions).
  4. **Step 2.4: Downgrader Gem** ([86ba1b4ce534](https://gemini.google.com/gem/86ba1b4ce534)):
     * **Input**: Max-expanded compendium.
     * **Process**: Re-organizes the context, trims tangent/out-of-context additions, and produces the final upgraded compendium.

---

### Stage 3: Curation & Ingestion Pass (`main.py process`)
* **Trigger**: Automatically runs on the final upgraded compendium.
* **Operations**:
  1. **Idempotency Filter**: Scans logs and filters out blocks whose `video_id` already exists in `processed_gemini.json`.
  2. **Thematic Classification (Programmatic)**: Calls the python function `classify_channel(channel_name)` to determine Domain and Category. (Uses a fast static lookup dictionary to prevent LLM latency/costs).
  3. **Context Injection**: Scans `wiki/MOCs/` to compile a list of active Maps of Content (`mocs_list`).
  4. **Absolute Temporal Anchoring (Programmatic + LLM)**: Injects the publication date (`video_date`) as a global anchor string (`{data_yaml}`) in the prompt context. The LLM translates relative text references (e.g. "yesterday") into absolute dates.
  5. **LLM Ingestion Prompting**: Launches Playwright, loads the Chrome profile, and submits the compendium to Gemini Web:
     * If *perennial*, formats `TECHNICAL_SYSTEM_PROMPT` (instructs the model to output `R_` and `A_` notes).
     * If *volatile*, formats `NEWS_SYSTEM_PROMPT` (instructs the model to output nominal dated chronicle files).
  6. **Self-Healing Format Check (Infinite Re-prompt Loop)**: Python validates that the response adheres strictly to parser boundaries (`<<<< FILE:` and `<<<< END FILE >>>>`). If invalid, it enters a `while True` correction loop, submitting the incorrect response back to Gemini Web with format errors until it matches.
  7. **Sidebar Cleanup & Latency Log**:
     * Upon a successful response, Playwright clicks the chat thread options, selects **Delete**, and confirms (redirecting the URL back to a clean state) to prevent account sidebar clutter.
     * Logs the timestamp, prompt size, response size, and generation duration into a local `latency_audit.csv` file to monitor server capacity and rate warnings.

---

### Stage 4: Directory Segmentation & Writing
* **Trigger**: Executes inside the curation response loop.
* **Operations**:
  1. Captures Gemini's markdown response containing file boundaries (`<<<< FILE: filename >>>>` and `<<<< END FILE >>>>`).
  2. For each extracted note, the Python script calls `resolve_note_path(wiki_dir, filename)` (programmatic path resolution based on file prefix):
     * `R_*.md` $\rightarrow$ `wiki/concepts/` (Perennial Reference)
     * `A_*.md` $\rightarrow$ `wiki/procedures/` (Perennial Action)
     * `MOC_*.md` $\rightarrow$ `wiki/MOCs/` (Maps of Content)
     * Any other nominal `*.md` $\rightarrow$ `wiki/chronicles/` (Volatile Chronicles)
  3. Lazily creates the folders if they do not exist and writes the markdown note content to the resolved path.

---

### Stage 5: Graph Connection & Backlinking
* **Trigger**: Runs programmatically after notes are written.
* **Operations**:
  1. **MOC Registration (Programmatic)**: Parses `<<<< MOC_ASSOCIATIONS >>>>` from Gemini's response and appends `- [[Note_Name]]` to the corresponding `MOC_*.md` files under `wiki/MOCs/`.
  2. **Scoped Grep Backlinking (Programmatic)**:
     * The Python script reads the newly extracted entities.
     * It runs a recursive search (`wiki_dir.rglob("*.md")`) over all files.
     * If a note mentions the name/alias of a new concept, it programmatically wraps it in a backlink (e.g., `[[R_Captura_Regulatoria|captura regulatória]]`).
  3. Logs the `video_id` in `processed_gemini.json` to mark it as completed.

---

### Stage 6: Weekly Semantic Reconciliation (`main.py reconcile` - Proposed)
* **Trigger**: Scheduled weekly cron job.
* **Operations**:
  1. **Index Scan**: The script scans the names of all files in `wiki/concepts/`, `wiki/people/`, and `wiki/organizations/`.
  2. **Clustering & Synonym Detection**: Passes batches of note names (along with their brief YAML descriptions) to Gemini Web. The LLM is asked to find semantic duplicates (e.g., `BC` vs `Banco Central` vs `Banco Central do Brasil`).
  3. **Automated Merging**:
     * If duplicates are found, the script designates a **canonical name** (e.g., `Banco Central do Brasil`).
     * It merges the content of the duplicate notes into the canonical file (sorting timelines and combining definitions).
     * It appends the merged synonyms to the `aliases: [...]` list in the canonical note's frontmatter.
     * Deletes the duplicate files (`BC.md`, `Banco_Central.md`).
  4. **Backlink Rewriting**: Scans the entire vault, replacing any outdated links (`[[BC]]`) with the updated alias link (`[[Banco Central do Brasil|BC]]`).
