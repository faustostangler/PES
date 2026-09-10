# Ubiquitous Language Glossary — PES Strategic Knowledge Monolith

This glossary establishes the canonical terminology across all engineering discussions, code identifiers, comments, documentation, and tests for the PES workspace.

---

## 1. Domain Entities & Value Objects

| Canonical Term | Pronunciation / Context | Definition | Aliases to AVOID |
|---|---|---|---|
| **`ContentId`** | Value Object | Strongly-typed unique identifier for a raw media item or transcript, derived from video ID or content hash. Enforces non-empty string and regex validation. | `id`, `video_id_str`, `raw_id` |
| **`NoteTitle`** | Value Object | Validated canonical title of an Atomic Note, automatically sanitized of `[[` brackets, path characters, and trailing whitespace. | `title_str`, `name`, `clean_title` |
| **`NoteType`** | Value Object | Enumerated typology classification restricted to: `concept`, `entity`, `event`, or `process`. | `tag_type`, `category`, `kind` |
| **`CausalMatrix`** | Value Object | Immutable ternary attribution model defining `cause` (underlying premise), `effect` (observable outcome), and `epistemic_attribution` (origin author/school). | `matrix`, `causality`, `premise_pair` |
| **`CrossContextRelations`** | Value Object | Immutable triad connecting a concept to its historical `precursors`, synchronous `lateral_events`, and systemic `aftermath`. | `context_net`, `network_links`, `relations` |
| **`RawTranscript`** | Entity / Aggregate | Unmodified, verbatim text of spoken audio extracted from media feeds, carrying immutable origin metadata. | `raw_text`, `transcript_dump`, `audio_text` |
| **`EnrichedCompendium`** | Entity / Aggregate | Continuous, dense, multi-pass factual prose document generated from a Raw Transcript without bullet lists or tables, containing a mandatory `Informações Complementares` section. | `article`, `expanded_text`, `summary`, `draft` |
| **`AtomicNote`** | Entity / Aggregate | A self-contained, highly-focused semantic unit in the Second Brain vault representing a single concept, entity, event, or process with standardized frontmatter, definition, WikiLinks, causal matrix, and cross-context links. | `note`, `card`, `wiki_page`, `markdown_file` |
| **`MapOfContent` (MOC)** | Entity / Aggregate | Navigational and conceptual synthesis document that groups and reconciles a thematic cluster of Atomic Notes with bidirectional links, ensuring zero orphaned notes. | `hub`, `index_page`, `toc`, `table_of_contents` |
| **`AtomicEntityInventory`** | Value Object | Deduplicated discovery manifest of distinct entities, concepts, events, and processes discovered across an Enriched Compendium prior to batch note generation. | `candidate_list`, `topics`, `tag_candidates` |

---

## 2. Architectural & Infrastructure Terms

| Canonical Term | Definition | Aliases to AVOID |
|---|---|---|
| **`MediaIngestionPort`** | Abstract application interface defining contracts for crawling, downloading subtitles, and transcribing audiovisual media. | `ScraperInterface`, `DownloaderPort` |
| **`LLMTransformationPort`** | Abstract application interface defining contracts for deterministic text generation, inventory discovery, and batched note synthesis. | `AIPort`, `ModelService`, `GenaiPort` |
| **`VaultRepositoryPort`** | Abstract application interface defining contracts for reading, writing, and indexing atomic notes, compendiums, and MOCs in the Second Brain vault. | `FileStoragePort`, `WikiStorage`, `DbPort` |
| **`LedgerRepositoryPort`** | Abstract application interface defining contracts for querying and updating processed media content IDs. | `LogPort`, `HistoryPort`, `TrackingPort` |
| **`LegacyISBMediaIngestionAdapter`** | Anti-Corruption Layer (ACL) that encloses legacy code in `playground/isb.ai/`, isolating `sys.path` modifications and converting legacy dictionaries into domain entities. | `ISBWrapper`, `SyncHelper` |
| **`ObsidianVaultAdapter`** | Infrastructure adapter implementing `VaultRepositoryPort` using atomic `.tmp` rename filesystem operations and frontmatter serialization. | `MarkdownWriter`, `WikiAdapter` |
| **`EvalRubric`** | Quantified scoring criteria (faithfulness, relevance, hallucination, toxicity) executed via Langfuse to validate LLM output quality against frozen thresholds. | `PromptTest`, `QualityCheck`, `EvalSpec` |
