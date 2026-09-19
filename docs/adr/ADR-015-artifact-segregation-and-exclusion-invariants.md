# ADR-015: Invariant Exclusion of System Artifacts and Indices from Batch Processing Pipeline

**Status:** ACCEPTED  
**Date:** 2026-09-19  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, 12-Factor App)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-002`](ADR-002-cresmo-presentation-cli.md), [`ADR-007`](ADR-007-pipeline-template-method-dry.md), [`ADR-009`](ADR-009-streaming-batch-source-discovery-producer-consumer.md), [`ADR-012`](ADR-012-multi-criteria-sync-filtering-and-alphabetical-feed-ordering.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md)  

---

## 1. Context & Architectural Problem Statement

When the Cresmo pipeline synthesizes knowledge from external media or text files, it emits structured metadata, indices, and derived compendiums into the filesystem lake:
1. **Channel Semantic Catalogs (`_canal.md`):** Generated in `data/raw/<channel_name>/_canal.md` per ADR-013, maintaining incremental markdown catalogs of indexed videos.
2. **Global Tabular Registry (`brain.csv`):** Generated in `data/brain.csv` per ADR-013, registering semantic taxonomies and keywords.
3. **Obsidian Vault Index (`_index.json`):** Generated in `vault/_index.json`, providing rapid note lookup.
4. **Idempotency Ledger (`cresmo_ledger.db`):** SQLite database tracking completed video and text synthesis runs.
5. **Derived Compendiums & Notes:** Enriched texts in `data/enriched/<channel>/`, consolidated master compendiums in `data/master/<category>/`, and atomic notes in `vault/`.

During subsequent executions of `cresmo run` or batch synchronization workflows, batch discovery (`load_transcript_files` in `discover_batch_sources.py`) recursively inspected `data/raw/` using a naive pattern:
```python
sorted(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"})
```

Because `_canal.md` carries the `.md` extension and resides directly inside channel folders in `data/raw/`, batch discovery identified `_canal.md` as an unprocessed transcript. The pipeline then attempted to synthesize `_canal.md` as if it were a video transcript, causing redundant LLM execution, corrupting domain content IDs (e.g. `_canal_<hash>`), and creating an infinite indexing feedback loop.

---

## 2. Alternatives Considered

1. **Move Indices Out of `data/raw/` entirely:**
   *Rejected.* `_canal.md` co-locating with raw transcripts provides immediate local context and git visibility for channel-level catalogs without cross-directory indirection.
2. **Ad-hoc `if path.name == "_canal.md"` Checks Scattered in Call Sites:**
   *Rejected.* Violates DRY and DDD invariants. Ad-hoc checks fail whenever new index formats or temporary files are introduced, leaving pipelines vulnerable to ingestion leaks.
3. **Domain Invariant Predicate (`is_processable_transcript_file`) with Defense-in-Depth:**
   *Selected.* Encapsulate artifact identification and candidate transcript qualification in a centralized, pure domain invariant function in `cresmo.domain.value_objects`. Apply this check at all architectural boundaries: Batch Discovery, Pipeline Ingestion, Presentation Runner, and Vault Adapters.

---

## 3. Decision

We establish the **Artifact Segregation and Exclusion Invariant** across all layers:

### 3.1 Domain Invariant: `is_processable_transcript_file`
A file path is a processable transcript candidate if and only if all of the following conditions are met:
1. **Extension Filter:** Suffix must strictly be `.md` or `.txt` (case-insensitive).
2. **Hidden / System Prefix:** The file name must NOT start with `_` or `.`.
3. **Hidden / System Directory:** None of the directory components in `path.parts` may start with `_` or `.` (e.g. `.git/`, `.obsidian/`, `_trash/`, `.tmp/`).
4. **Reserved System Artifacts:** The file name must NOT belong to `RESERVED_SYSTEM_FILENAMES`:
   - `_canal.md`
   - `brain.csv`
   - `cresmo_ledger.db` (including WAL/SHM companion files)
   - `playlist.txt`, `playlist-priority.txt`
   - `_index.json`
5. **Temporary / Backup Files:** Suffixes or names ending in `.tmp`, `.bak`, `.swp`, or `~` are strictly excluded.
6. **Derived Directory Exclusion:** If scanning an encompassing directory (e.g. `data/`), files residing inside derived output folders (`enriched`, `master`, `vault`) are excluded.

### 3.2 Defense-in-Depth Layers
- **Discovery Layer (`discover_batch_sources.py`):**
  `load_transcript_files` filters candidates using `is_processable_transcript_file(p)`. `_scan_raw_lake` and `_scan_priority_texts` reject non-qualifying files before inspecting frontmatter or registering `seen_vids`.
- **Pipeline Layer (`pipeline.py`):**
  `run_for_text_file` validates `is_processable_transcript_file(file_path)`; if violated, it raises `CresmoDomainError` with fail-fast semantics, refusing to synthesize system artifacts.
- **Presentation Layer (`run.py`):**
  `execute_batch_run` inspects file targets and marks any discovered system artifact as `[SKIPPED]` with clear console logging.
- **Vault Adapters (`obsidian_vault_adapter.py`):**
  Channel scanning methods ignore files starting with `_` or `.`.

---

## 4. Consequences & Verification

- **Positive:**
  - Prevents recursive synthesis of `_canal.md` and other internal index files.
  - Eliminates corrupted content IDs and accidental LLM token expenditure on metadata files.
  - Zero-drift domain invariant tested with mirrored unit test suites.
- **Negative:**
  - Any user intentionally naming a legitimate transcript starting with an underscore (e.g. `_my_video.md`) will need to rename it without the leading underscore. This is aligned with POSIX and UNIX conventions where leading underscores/dots denote hidden or internal entities.
