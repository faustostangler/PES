# Cresmo Strategic Domain Model & Invariants Blueprint

**Context**: Cresmo Knowledge Synthesis  
**Phase**: Phase 1 — Stereoscopy  
**Status**: APPROVED SPECIFICATION  
**Governing ADR**: [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md)  

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

---

## 2. Aggregates & Entities (Always Valid at Construction)

Entities enforce business invariants during `__init__` / `model_validator(mode="after")`. There is no "build now, validate later" state.

### 2.1 `RawTranscript` Aggregate
- **Root Entity**: `RawTranscript`
- **Attributes**:
  - `content_id: ContentId`
  - `channel_name: str`
  - `upload_date: datetime.date | None`
  - `title: str`
  - `source_url: str`
  - `body: str` (Verbatim spoken text)
- **Invariants**:
  - `body` must not be empty or whitespace.
  - `content_id` must be valid.

### 2.2 `EnrichedCompendium` Aggregate
- **Root Entity**: `EnrichedCompendium`
- **Attributes**:
  - `content_id: ContentId`
  - `channel_name: str`
  - `title: NoteTitle`
  - `body: str` (Continuous fluid prose)
  - `complementary_info: str` (Historical & scientific data)
  - `pass_count: int`
- **Invariants**:
  - `body` must not contain markdown tables or bulleted lists in the main text.
  - `complementary_info` must not be empty.
  - `pass_count >= 1`.

### 2.3 `AtomicNote` Aggregate
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

### 2.4 `MapOfContent` (MOC) Aggregate
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
- `RawTranscriptIngestedEvent(content_id: ContentId, timestamp: datetime.datetime)`
- `CompendiumEnrichedEvent(content_id: ContentId, pass_count: int)`
- `AtomicNoteSynthesizedEvent(title: NoteTitle, note_type: NoteType, source_id: ContentId)`
- `VaultReconciledEvent(total_notes: int, moc_count: int)`
