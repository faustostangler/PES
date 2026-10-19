# Cresmo Strategic Domain Model & Invariants Blueprint

**Context**: Cresmo Knowledge Synthesis  
**Phase**: Phase 1 — Stereoscopy  
**Status**: APPROVED SPECIFICATION (SYNCHRONIZED WITH ADR-033 & ADR-038)  
**Governing ADRs**: [`ADR-000`](../adr/ADR-000-patterns-antipatterns.md), [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-019`](../adr/ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md), [`ADR-028`](../adr/ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-031`](../adr/ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), [`ADR-032`](../adr/ADR-032-composite-channel-and-content-value-objects.md), [`ADR-033`](../adr/ADR-033-composite-value-objects-identity-parity-and-tenant-simplification.md), [`ADR-038`](../adr/ADR-038-pure-value-object-triad-composition.md)  

---

## 1. Value Objects (Zero Primitive Obsession & Intentional Asymmetric Hybrid Composition)

All business concepts must be modeled as immutable Value Objects enforcing domain invariants at instantiation. Per [`ADR-033`](../adr/ADR-033-composite-value-objects-identity-parity-and-tenant-simplification.md), we reject both *Primitive Obsession* (raw strings for domain identifiers) and *Primitive Obsession Obsession* (dummy single-field wrappers for every string), establishing **Intentional Asymmetric Hybrid Composition**.

### 1.1 Identity Value Objects

#### `ContentId`
- **Definition**: Strongly-typed platform identifier for media content (YouTube video ID or sha256 hash).
- **Invariants**:
  - Must not be empty or whitespace-only.
  - Rejects path traversal and command injection tokens.
  - Matches regex `^[a-zA-Z0-9_-]{8,64}$`.

#### `ChannelId`
- **Definition**: Strongly-typed canonical platform creator identifier (e.g. YouTube `UC...`).
- **Invariants**:
  - Must not be empty or whitespace.
  - Rejects invalid characters and path traversal.

### 1.2 Composite Value Objects (ADR-032, ADR-033, ADR-038)

#### `Channel` (Composite Value Object)
- **Definition**: Encapsulates creator provenance, platform identities, and tenant cost center.
- **Attributes**:
  - `id: ChannelId | None` (Algorithmic Platform Key).
  - `name: str` (Cognitive Key — self-validating non-empty string, max 120 chars, prohibits traversal).
  - `category: str = ""` (Taxonomy category).
  - `url: str | None = None` (Explicit source URL).
- **Properties & Intrinsic Capabilities**:
  - `tenant_key -> str`: Intrinsic tenant cost-center representation (`"channel:{id or name}"`), replacing decommissioned `ChannelTenantId`.
  - `canonical_url -> str`: Automatically derives normalized channel URL.

#### `MediaProvenance` (Composite Value Object — ADR-038)
- **Definition**: Encapsulates external acquisition metadata and temporal grounding.
- **Attributes**:
  - `url: str = ""` (Source canonical media or file URL).
  - `description: str = ""` (Original media summary/description).
  - `publication_date: datetime.date | None = None` (Canonical publication timestamp).
- **Invariants**:
  - Eliminates legacy `upload_date` alias per ADR-038 (`Duplicate Temporal Aliasing*` banned).

#### `Content` (Composite Value Object — ADR-032, ADR-038)
- **Definition**: Encapsulates text payload, title, and algorithmic ID.
- **Attributes**:
  - `id: ContentId` (Algorithmic Key).
  - `title: str = ""` (Cognitive Key — sanitized title).
  - `body: str` (Canonical text payload for raw audio or synthesized prose).
- **Invariants**:
  - `body` cannot be empty or whitespace-only.
  - Replaces legacy type alias `Video` (eliminated per ADR-033).

### 1.3 Cognitive & Intermediate Value Objects

#### `CandidateText` (ADR-031)
- **Definition**: Validated domain container for intermediate LLM transformation outputs during pipeline stages.
- **Attributes**:
  - `text: str` (Transformed text payload).
  - `stage_name: str` (Identifier of producing pipeline stage).
  - `metadata: dict[str, Any]` (Stage metrics and telemetry attributes).
- **Invariants**:
  - `text` cannot be empty or whitespace-only (`raise DomainValidationError`).

#### `NoteTitle`
- **Definition**: Canonical title of an Atomic Note.
- **Invariants**:
  - Length between 1 and 200 characters.
  - Automatically sanitized of `[[`, `]]`, newlines, and illegal filesystem characters (`/ \ : * ? " < > | %`).
  - Cannot be generic placeholder (`"Untitled"`).

#### `NoteType`
- **Definition**: Categorical typology of an Atomic Note (`CONCEPT`, `ENTITY`, `EVENT`, `PROCESS`).

#### `CausalMatrix` & `CrossContextRelations`
- **Definition**: Ternary attribution models representing causes, effects, precursors, lateral events, and aftermath.

### 1.4 Telemetry Identity Value Objects

#### `PipelineSessionId` (ADR-027, ADR-033, ADR-035)
- **Definition**: Value Object representing the single-video holistic lifecycle session for Langfuse session replay.
- **Format**: `{channel_id}:{content_id}` (or fallback `{channel_name}:{content_id}`).
- **Invariants**:
  - Bound to exactly 1 processed work item per ADR-035.
  - Eradicates `.video_id` property per ADR-033.

#### `UserIdentity` (ADR-027)
- **Definition**: Polymorphic operator identity (`anonymous`, `user:{provider}:{subject}`, `system:{worker}`).
- **Invariant**: Channels and tenants are strictly segregated from user identities.

#### `ChannelTenantId` *(DECOMMISSIONED per ADR-033)*
- **Status**: Completely eliminated in favor of `Channel.tenant_key`.

---

## 2. Aggregates & Entities: Pure 3-Value-Object Triad Composition (ADR-038)

Per [`ADR-038`](../adr/ADR-038-pure-value-object-triad-composition.md), all transcript aggregates are structured as a pure composition of three cohesive, immutable Value Objects, eliminating `Flat Transcript Property Sprawl*`:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      TRANSCRIPT AGGREGATE ROOT                         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. channel: Channel                      (Origin, Creator, Tenant)     │
│ 2. provenance: MediaProvenance           (Acquisition, Date, Metadata) │
│ 3. content: Content                      (ID, Title, Text Body)        │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 `SourceTranscript` Aggregate (ADR-010, ADR-031, ADR-038)
- **Root Entity**: `SourceTranscript` (Canonical input entity; replacing deprecated `RawTranscript`).
- **Composition**:
  - `channel: Channel`
  - `provenance: MediaProvenance`
  - `content: Content` (holds verbatim spoken text or source markdown)
  - `metadata: dict[str, Any]` (extensible non-domain telemetry metadata)
- **Invariants**:
  - `content.body` must not be empty or whitespace (audio silence rejected).
  - `content.id` and `channel.name` must be valid at construction.
  - Algorithmic parity (`channel.id` + `content.id`) and Cognitive parity (`channel.name` + `content.title`) enforced structurally.

### 2.2 `FluidTranscript` Aggregate (ADR-028, ADR-038)
- **Root Entity**: `FluidTranscript` (Stage 1 linguistic normalization output).
- **Composition**:
  - `channel: Channel`
  - `provenance: MediaProvenance`
  - `content: Content` (holds third-person neutral prose free of speech noise and oralities)
  - `metadata: dict[str, Any]`
- **Invariants**:
  - `content.body` must be continuous narrative prose; markdown tables and bulleted lists are forbidden in the core narrative.
  - Preserves exact identity parity with originating `SourceTranscript`.

### 2.3 `EnrichedCompendium` Aggregate
- **Root Entity**: `EnrichedCompendium` (Historical and scientific gap-filling output).
- **Attributes**:
  - `content_id: ContentId`
  - `channel: Channel`
  - `title: NoteTitle`
  - `body: str` (Continuous fluid prose)
  - `complementary_info: str` (Historical & scientific data)
  - `pass_count: int >= 1`

### 2.4 `AtomicNote` Aggregate
- **Root Entity**: `AtomicNote` (Atomic Second Brain note).
- **Attributes**:
  - `title: NoteTitle`
  - `note_type: NoteType`
  - `content_tags: tuple[str, ...]`
  - `domain: str`, `cluster: str`, `source: str`
  - `definition: str` (minimum 20 chars)
  - `direct_relations: tuple[NoteTitle, ...]` (no self-referential cycles)
  - `causal_matrix: CausalMatrix | None`
  - `cross_context: CrossContextRelations | None`

### 2.5 `MapOfContent` (MOC) Aggregate
- **Root Entity**: `MapOfContent` (High-level conceptual index note).
- **Attributes**:
  - `title: NoteTitle`
  - `theme: str`
  - `overview: str`
  - `associated_notes: tuple[NoteTitle, ...]` (minimum 1 note, zero duplicates)

---

## 3. Domain Events

Cross-aggregate lifecycle changes produce immutable domain events:
- `SourceTranscriptIngestedEvent(content_id: ContentId, timestamp: datetime.datetime)`
- `FluidTranscriptDetranscribedEvent(content_id: ContentId, title: str)`
- `CompendiumEnrichedEvent(content_id: ContentId, pass_count: int)`
- `AtomicNoteSynthesizedEvent(title: NoteTitle, note_type: NoteType, source_id: ContentId)`
- `VaultReconciledEvent(total_notes: int, moc_count: int)`
