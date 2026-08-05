---
name: cresmo
description: Master orchestrator skill for processing raw transcripts, lecture notes, and draft texts into rich, interlinked atomic Obsidian notes and managing Maps of Content (MOCs). Coordinates the Cresmo family pipeline (cresmo-expander, cresmo-atomic, cresmo-moc-manager). Use whenever the user requests full-cycle transcript processing, speech detranscription, gap expansion, atomic note generation, Obsidian Second Brain vault integration, WikiLink mapping, or MOC management. Make sure to use this skill whenever the user mentions transcripts, audio transcriptions, atomic notes, Obsidian vaults, WikiLinks, or MOCs, even if they do not explicitly mention "cresmo".
---

# Cresmo Master Orchestrator

## Overview

The `cresmo` master skill orchestrates and coordinates the specialized sub-skills in the Cresmo ecosystem. It manages the complete end-to-end lifecycle of knowledge extraction from raw audio/speech transcripts—starting from Socratic gap expansion and diagram suppression, proceeding to atomic note extraction with Obsidian WikiLinks, and concluding with vault entity reconciliation and Map of Content (MOC) narrative integration.

### Input Specification & YAML Metadata Protocol

Input transcripts are supplied with a standardized YouTube YAML frontmatter header, as this example:

```yaml
---
video_title: [video_title]
video_id: [video_id]
channel_name: [channel_name]
channel_id: [channel_id]
channel_category: [channel_category]
url: [url]
video_date: [video_date]
video_description: description of video
---
[Raw transcript content follows]
```

**`transcript_slug` Rule**: The `<transcript_slug>` identifier used across all pipeline file paths MUST be set strictly to the YouTube `video_id` extracted from the input YAML frontmatter (e.g., `eYFTRQHaPgw`).

All pipeline outputs are stored systematically under:
`playground/cresmo/<video_id>/`

---

## Ecosystem Sub-Skills Registry

### Core Pipeline Sub-Skills

#### cresmo-expander
Purges speech noise, oralities, hesitations, direct audience interactions, diagrams, tables, formulas, and bullet lists. Conducts fact-checking and a 2-pass Socratic/Genealogical gap audit, producing continuous fluid Markdown prose with markdown headings and a complementary information section.
Target Skill File: [`cresmo-expander`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/cresmo-expander/SKILL.md)

#### cresmo-atomic
Transforms expanded fluid text into autonomous, semantically dense Atomic Notes formatted for an Obsidian Second Brain vault. Enforces strict typologies (`entity`, `concept`, `event`, `process`), Big-Endian event titles, YAML frontmatter, declarative triple connections, causal attribution matrices, and bi-directional WikiLinks, outputting an XML batch. Extracts `channel_name` and `video_id` from the source header to construct source tags `#fonte/[channel_name]/[video_id]`.
Target Skill File: [`cresmo-atomic`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/cresmo-atomic/SKILL.md)

#### cresmo-moc-manager
Reconciles incoming XML atomic notes with an active Obsidian Vault environment. Executes a 3-tier lookup protocol (`_index.json` -> Category MOCs -> Semantic audit), performs non-destructive incremental note merging, updates reciprocal back-links trans-textually, enforces tag governance (`#fonte/[channel_name]/[video_id]`), and integrates every note into narrative Maps of Content (MOCs) with zero orphaned notes.
Target Skill File: [`cresmo-moc-manager`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/cresmo-moc-manager/SKILL.md)

---

## Orchestration Pipelines & Execution Modes

`cresmo` analyzes the user request and selects one of the following execution pipelines:

### 1. Full 3-Stage Master Pipeline (Transcript to Vault)
Executed when a raw transcript, lecture audio text, or draft document needs full processing into an Obsidian Vault.
Sequence: `cresmo-expander` -> `cresmo-atomic` -> `cresmo-moc-manager`
- **Stage 1**: `cresmo-expander` cleans transcript, strips diagrams/tables/lists, audits gaps, and outputs fluid text to `playground/cresmo/<video_id>/01_expanded.md`.
- **Stage 2**: `cresmo-atomic` reads `01_expanded.md`, extracts atomic notes with WikiLinks, includes source metadata tags (`#fonte/[channel_name]/[video_id]`), and outputs XML batch to `playground/cresmo/<video_id>/02_atomic_notes.xml`.
- **Stage 3**: `cresmo-moc-manager` reads `02_atomic_notes.xml`, reconciles files against `_index.json`, merges notes, syncs bi-directional links, updates MOCs, proliferates atomic notes to `playground/cresmo/wiki/<note_type>/[Exact Note Title].md`, and outputs reconciliation summary to `playground/cresmo/<video_id>/03_moc_reconciliation.md`.

### 2. Transcript-to-Atomic Pipeline
Executed when the user wants to convert a transcript into atomic notes without performing immediate vault reconciliation.
Sequence: `cresmo-expander` -> `cresmo-atomic`

### 3. XML Vault Integration Pipeline
Executed when the user already has an XML batch of atomic notes and wants to integrate them into an Obsidian vault.
Sequence: `cresmo-moc-manager`

### 4. Direct Sub-Skill Routing
Executed when the user requests a single isolated task (e.g., only expand a text via `cresmo-expander`, only extract atomic notes via `cresmo-atomic`, or reconcile MOCs via `cresmo-moc-manager`).

---

## Inter-Skill Data Contracts & Anti-Corruption Layer (ACL)

When chaining sub-skills in multi-stage pipelines, `cresmo` enforces the following data transfer rules:

### Directory & File Conventions
All outputs MUST be saved under the designated playground structure:
- Main pipeline directory: `playground/cresmo/<video_id>/` (where `<video_id>` is the YouTube `video_id` extracted from input YAML frontmatter).
- Atomic notes wiki proliferation directory: `playground/cresmo/wiki/<note_type>/` (where `<note_type>` is `entity`, `concept`, `event`, or `process`).

Stage Outputs:
- **Stage 1 Output**: `01_expanded.md` (Strictly continuous narrative Markdown prose; no diagrams, tables, formulas, blockquotes, or bullet lists).
- **Stage 2 Output**: `02_atomic_notes.xml` (Strictly `<xml><nota>...</nota></xml>` XML container with Obsidian YAML frontmatter and WikiLinks).
- **Stage 3 Output**:
  - Individual Atomic Note `.md` Files: Placed in `playground/cresmo/wiki/<note_type>/[Exact Note Title].md` (file proliferation phase).
  - Global Reconciliation Report: `playground/cresmo/<video_id>/03_moc_reconciliation.md` (Reconciliation log, entity resolution audit, and updated MOC narrative summaries).

---

## Operational Execution Protocol

1. **Analyze Intent**: Determine whether the user requires the full 3-stage master flow, a 2-stage flow, or a single sub-skill execution.
2. **Initialize Workspace**: Create directory `playground/cresmo/<transcript_slug>/`.
3. **Execute Stage 1 (`cresmo-expander`)**: Pass the input transcript to `cresmo-expander`. Ensure all diagrams, ASCII art, and bullet lists are purged and converted into fluid prose paragraphs. Save result to `01_expanded.md`.
4. **Execute Stage 2 (`cresmo-atomic`)**: Pass `01_expanded.md` to `cresmo-atomic`. Extract atomic notes with YAML frontmatter, WikiLinks (`[[Title]]`), and XML container tags. Save result to `02_atomic_notes.xml`.
5. **Execute Stage 3 (`cresmo-moc-manager`)**: Pass `02_atomic_notes.xml` to `cresmo-moc-manager`. Reconcile against `_index.json`, perform incremental merges, update trans-text back-links, and weave every note into a narrative MOC. Save summary to `03_moc_reconciliation.md`.
6. **Deliver Final Summary**: Present delivery report with exact clickable file links to all created output files.
