---
name: cresmo-moc-manager
description: Reconciles XML atomic notes into an Obsidian Vault. Performs entity resolution, tiered lookups against _index.json, incremental note merging, bi-directional cross-text linking, tag governance, and Maps of Content (MOC) integration with zero orphaned notes. Use whenever atomic notes need to be merged into an existing Obsidian vault, reconciled with index files, or linked into MOCs. Make sure to trigger this skill during Stage 3 of the Cresmo pipeline or whenever MOC management and vault reconciliation are requested.
---

# Cresmo MOC Manager (Obsidian Vault & MOC Integration Agent)

## Overview

The `cresmo-moc-manager` skill acts as the Second Brain Vault Integrator for Obsidian. It takes incoming batches of atomic notes (formatted in XML `<xml><nota>...</nota></xml>`) and reconciles them into an active Obsidian Vault environment.

It enforces zero orphaned notes (every note is woven into a hierarchically organized Map of Content - MOC), executes tiered entity resolution against `_index.json`, performs non-destructive incremental note merging for existing notes, synchronizes bi-directional links trans-textually across existing vault files, and maintains tag governance.

**File Proliferation Directive**: This phase transforms the XML batch of atomic notes into individual Markdown (.md) files. Each atomic note extracted from `<xml><nota>...</nota></xml>` must be saved as an individual `.md` file in `playground/cresmo/wiki/<note_type>/` (where `<note_type>` is `entity`, `concept`, `event`, or `process`), named exactly after the note's title (`[Exact Note Title].md`). 

Save the overall reconciliation log report directly to `playground/cresmo/enriched/<channel_name>/<video_id>_reconciliation.md`.

---

## Core Vault Rules & Operating Principles

1. **Zero Orphaned Notes**: Every atomic note MUST be linked within the hierarchical structure of at least one Map of Content (MOC). Unlinked, floating notes are strictly prohibited.
2. **Bi-Directional Trans-Textual Sync**: When a new note references existing vault notes, the agent MUST update those existing notes with back-links (`[[WikiLink]]`), maintaining full symmetry across the vault.
3. **Non-Destructive Incremental Merging**: Never overwrite historical vault data. When an incoming note matches an existing file, merge tags, aliases, context, triples, and causal matrices incrementally.

---

## Tiered Entity Resolution Protocol

To reconcile incoming candidates without redundant file creation or vault corruption, execute a 3-tier lookup in continuous fluid sequence:

First, perform a Tier 1 Global Index Check by matching the note title and aliases against `_index.json` (or `mapa_aliases.md`). If a direct match or registered alias exists, redirect the incoming payload to the existing note file for incremental merging.

Second, if `_index.json` presents ambiguity or homonyms, perform a Tier 2 Category MOC Lookup by inspecting the relevant epistemological MOC (e.g., `[[MOC Geopolítica]]`) to determine if the concept or entity is already addressed under another denomination.

Third, if ambiguity persists after the first two tiers, perform a Tier 3 Semantic Deep Audit by conducting a full text analysis of definitions to decide conclusively whether to merge the content into an existing note or generate a new atomic note file.

---

## Incremental Note Merging Protocol

When entity resolution determines a candidate note already exists in the vault, merge using the following rules:

1. **YAML Frontmatter**: Merge `tags` (deduplicating) and append new items to `aliases`.
2. **Contextual Analysis & Divergent Data**: Synthesize new factual data into existing paragraphs without destroying previous context. If source data divergence exists between the incoming candidate and historical vault records, explicitly state both positions in the analysis text with their respective epistemic attributions.
3. **Triples & Connections**: Append new declarative triples (`* [[Source]] -> [Action] -> [[Target]]`), deduplicating statements.
4. **Causal Matrix & Cross-Context**: Append new premisses, effects, precursors, lateral events, and ramifications.
5. **Trans-Text Bi-Directional Sync**: Inspect newly added `[[WikiLinks]]` and open target existing files in the vault to insert reciprocal back-links.

---

## Map of Content (MOC) Architecture

### MOC Hierarchy
- **Global Epistemological MOCs**: Macro domain categories (e.g., `[[MOC Geopolítica]]`, `[[MOC História Contemporânea]]`, `[[MOC Física e Tecnologia]]`, `[[MOC Biologia e Medicina]]`).
- **Thematic Sub-MOCs**: Created within a Global MOC when a dense semantic cluster emerges (e.g., `[[MOC Conflitos no Leste Europeu]]`, `[[MOC Oftalmologia]]`).

### MOC Narrative Format
MOCs are NOT simple bulleted lists of links. MOCs MUST be structured as an hierarquical index based on context, with `[[WikiLinks]]` to atomic notes.

In an old-style prose-like MOC is found, convert it to the correct format (an hierarquical index based on context, with `[[WikiLinks]]` to atomic notes).

---

## Tag Governance System

All notes must follow the nested forward-slash tag hierarchy (`#category/sub-category`):

- **Type Tags**: `#tipo/entidade`, `#tipo/conceito`, `#tipo/evento`, `#tipo/processo`
- **Source Tags**: `#fonte/[channel_name]/[video_id]`
- **Domain Tags**: `#dominio/geopolitica`, `#dominio/defesa/nuclear`, `#dominio/historia`
- **Cluster Tags**: `#cluster/crise-ucrania-2022`, `#cluster/controle-de-armas`

Rule: Notes in the same semantic micro-context MUST share at least one `#cluster/*` tag and one `#dominio/*` tag in their YAML frontmatter.

---

## Tool Execution Directive (Strict Automated Governance)

**MANDATORY RULE**: The MOC Manager agent must execute all file modifications, MOC narrative updates, and reconciliation report generation EXCLUSIVELY via native file manipulation tools (`write_to_file`, `replace_file_content`).
- **ABSOLUTE PROHIBITION**: NEVER invoke `run_command` or shell/terminal commands to manipulate files, run python one-liners, or parse XML. 
- In the automated pipeline (`cresmo-pipeline.py`), the proliferation of individual `.md` notes and the synchronization of `_index.json` are performed automatically by Python. The MOC Manager agent's responsibility is to weave the links into the appropriate index MOCs and write the final reconciliation report using `write_to_file`.

---

## Step-by-Step Execution Algorithm

For each incoming XML batch (`<xml><nota>...</nota></xml>`):

1. **Read Candidate Note**: Parse YAML, title, body, and WikiLinks from `<nota>`.
2. **Execute Entity Resolution**: Run Tiered Lookup (`_index.json` -> Category MOC -> Semantic Audit).
   - If match found: Perform **Incremental Merge**.
   - If match not found: Write new `.md` note file in the Vault (or verify pipeline proliferation).
3. **Execute Trans-Text Sync**: Scan note body for references to existing vault files and update those existing files with reciprocal `[[WikiLinks]]`. Use the descriptive narrative content of MOCs to guide exactly where to weave the new back-links naturally into existing paragraphs.
4. **Map Epistemological Category**: Identify the target Global MOC or Sub-MOC.
5. **Update/Create MOC Narrative**: Integrate the note's `[[WikiLink]]` into the fluid text paragraphs of the MOC using `replace_file_content`.
6. **Update Global Index**: Ensure newly created titles and aliases are reflected in `_index.json`.
7. **Generate Reconciliation Summary**: Save a complete log of created, merged, and updated MOC links directly to `cresmo/enriched/<channel_name>/<video_id>_reconciliation.md` using `write_to_file`.
