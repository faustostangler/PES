# Cresmo Strategic Domain Model & Invariants Blueprint

**Context**: Cresmo Knowledge Synthesis  
**Phase**: Phase 1 — Stereoscopy  
**Status**: APPROVED SPECIFICATION  
**Governing ADRs**: [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-019`](../adr/ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md), [`ADR-028`](../adr/ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-031`](../adr/ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md)  

---

## 1. Value Objects (Zero Primitive Obsession)

All business concepts must be modeled as immutable Value Objects enforcing domain invariants at instantiation.

### 1.1 `ContentId`
- **Definition**: Unique identifier for media content (YouTube video ID or hash).
- **Invariants**:
  - Must not be empty or whitespace-only.
  - Must match regex `^[a-zA-Z0-9_-]{8,64}$`.
- **Implementation Rules**:
  - Implemented via `@dataclass(frozen=True)` or Pydantic V2 `BaseModel(frozen=True)`.
  - Construction rejects invalid strings immediately (`raise DomainValidationError`).

### 1.2 `NoteTitle`
- **Definition**: Canonical title of an Atomic Note.
- **Invariants**:
  - Length between 1 and 200 characters.
  - Automatically sanitized of `[[`, `]]`, newline characters, and filesystem illegal characters (`/ \ : * ? " < > | %`).
  - Cannot be generic placeholder (`"Untitled"`, `"Untitled_Note"`).

### 1.3 `NoteType`
- **Definition**: Categorical typology of an Atomic Note.
- **Invariants**:
  - Must strictly be one of: `NoteType.CONCEPT`, `NoteType.ENTITY`, `NoteType.EVENT`, `NoteType.PROCESS`.
  - Case-insensitive string normalization at construction.

### 1.4 `CausalMatrix`
- **Definition**: Ternary attribution model of causality.
- **Attributes**:
  - `cause: str` (Underlying premise/cause).
  - `effect: str` (Observable impact/outcome).
  - `epistemic_attribution: str` (Authoritative source or philosophical lineage).
- **Invariants**:
  - All attributes trimmed.
  - At least `cause` and `effect` must contain non-empty content when present.

### 1.5 `CrossContextRelations`
- **Definition**: Triad connecting a concept across historical, lateral, and consequential axes.
- **Attributes**:
  - `precursors: str` (Historical precursors).
  - `lateral_events: str` (Synchronous occurrences).
  - `aftermath: str` (Long-term consequences).

### 1.6 `ChannelName` (ADR-019)
- **Definition**: Strongly-typed identifier representing a content creator or media channel.
- **Invariants**:
  - Must not be empty or whitespace.
  - Length capped between 1 and 120 characters.
  - Rejects directory traversal tokens (`..`, `/`, `\`).
  - Case-preserving with transparent equality and hash support.

### 1.7 `ChannelId` (SPEC-003)
- **Definition**: Canonical platform channel identifier (e.g. YouTube `UC...`).
- **Invariants**:
  - Non-empty, alphanumeric string with underscores/hyphens.

### 1.8 `CandidateText` (ADR-031)
- **Definition**: Validated, strongly-typed domain container for intermediate LLM transformation outputs.
- **Attributes**:
  - `text: str` (Transformed text payload).
  - `stage_name: str` (Identifier of producing pipeline stage).
  - `metadata: dict[str, Any]` (Provenance and telemetry attributes).
- **Invariants**:
  - `text` cannot be empty or whitespace-only (`raise DomainValidationError`).

### 1.9 `PipelineSessionId` (ADR-016, ADR-027)
- **Definition**: Value Object representing the holistic single-video lifecycle session for Langfuse session replay.
- **Format**: `{channel_id}:{video_id}` (or legacy `content:{channel}:{content_id}`).
- **Invariants**:
  - Cannot be empty. Components must be valid non-empty tokens.

### 1.10 `ChannelTenantId` & `UserIdentity` (ADR-027)
- **`ChannelTenantId`**: Formatted as `channel:{channel_name_or_id}`, representing the cost center / tenant.
- **`UserIdentity`**: Polymorphic operator identity:
  - Anonymous: `anonymous` or `anon:{token}`
  - Identified: `user:{provider}:{subject}`
  - Scheduled Worker: `system:{worker_name}`

---

## 2. Aggregates & Entities (Always Valid at Construction)

Entities enforce business invariants during `__init__` / `model_validator(mode="after")`. There is no "build now, validate later" state.

### 2.1 `SourceTranscript` Aggregate (ADR-031)
- **Root Entity**: `SourceTranscript` (Standardized replacement for deprecated `RawTranscript` per ADR-010 and ADR-031)
- **Attributes**:
  - `content_id: ContentId`
  - `channel_name: ChannelName` (Enforced Value Object per ADR-019)
  - `body: str` (Verbatim spoken text or canonical source prose)
  - `title: str = ""`
  - `source_url: str = ""`
  - `publication_date: datetime.date | None = None`
  - `upload_date: datetime.date | None = None` (Backward-compatible alias for publication_date)
  - `channel_id: ChannelId | None = None`
  - `channel_category: str = ""`
  - `video_description: str = ""`
  - `metadata: dict[str, Any]`
- **Invariants**:
  - `channel_name` must be a valid, non-empty `ChannelName`.
  - `body` must not be empty or whitespace (audio silence rejected).
  - `content_id` must be valid.
  - Coerces raw string inputs to `ChannelName` and `ChannelId` automatically.

### 2.2 `FluidTranscript` Aggregate (ADR-028)
- **Root Entity**: `FluidTranscript` (Stage 1 linguistic normalization output)
- **Attributes**:
  - `content_id: ContentId`
  - `channel_name: ChannelName`
  - `body: str` (Continuous third-person neutral narrative prose free of oralities and speech noise)
  - `title: str = ""`
  - `source_url: str = ""`
  - `publication_date: datetime.date | None = None`
  - `upload_date: datetime.date | None = None`
  - `channel_id: ChannelId | None = None`
  - `channel_category: str = ""`
  - `video_description: str = ""`
- **Invariants**:
  - `channel_name` cannot be empty or whitespace.
  - `body` cannot be empty or whitespace.
  - `body` must be continuous narrative prose; markdown tables are strictly forbidden (cresmo-style-guide).
- **Post-Processor**:
  - `post_process_fluid_transcript(candidate: CandidateText | str, source: SourceTranscript) -> FluidTranscript`: Strips H1 headers, strips accidental complementary sections, and propagates provenance metadata.

### 2.3 `EnrichedCompendium` Aggregate
- **Root Entity**: `EnrichedCompendium`
- **Attributes**:
  - `content_id: ContentId`
  - `channel_name: ChannelName`
  - `title: NoteTitle`
  - `body: str` (Continuous fluid prose)
  - `complementary_info: str` (Historical & scientific data)
  - `pass_count: int`
- **Invariants**:
  - `body` must not contain markdown tables or bulleted lists in the main text.
  - `complementary_info` must not be empty.
  - `pass_count >= 1`.

### 2.4 `AtomicNote` Aggregate
- **Root Entity**: `AtomicNote`
- **Attributes**:
  - `title: NoteTitle`
  - `note_type: NoteType`
  - `content_tags: tuple[str, ...]`
  - `domain: str`
  - `cluster: str`
  - `source: str`
  - `aliases: tuple[str, ...]`
  - `definition: str`
  - `direct_relations: tuple[NoteTitle, ...]`
  - `causal_matrix: CausalMatrix | None`
  - `cross_context: CrossContextRelations | None`
- **Invariants**:
  - `definition` must be non-empty (minimum 20 characters).
  - `title` cannot be present in its own `direct_relations` (no self-referential cycles).
  - All `direct_relations` must be valid `NoteTitle` instances.

### 2.5 `MapOfContent` (MOC) Aggregate
- **Root Entity**: `MapOfContent`
- **Attributes**:
  - `title: NoteTitle`
  - `theme: str`
  - `overview: str`
  - `associated_notes: tuple[NoteTitle, ...]`
- **Invariants**:
  - `associated_notes` must contain at least 1 note.
  - No duplicate note titles within the MOC.

---

## 3. Domain Events

Cross-aggregate lifecycle changes produce immutable domain events:
- `SourceTranscriptIngestedEvent(content_id: ContentId, timestamp: datetime.datetime)`
- `FluidTranscriptDetranscribedEvent(content_id: ContentId, title: str)`
- `CompendiumEnrichedEvent(content_id: ContentId, pass_count: int)`
- `AtomicNoteSynthesizedEvent(title: NoteTitle, note_type: NoteType, source_id: ContentId)`
- `VaultReconciledEvent(total_notes: int, moc_count: int)`
