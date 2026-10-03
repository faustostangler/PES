# ADR-032: Composite Channel and Content Value Objects and Context Simplification

**Status:** ACCEPTED  
**Date:** 2026-10-02  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [`ADR-019`](ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md), [`ADR-026`](ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), [`ADR-027`](ADR-027-unified-telemetry-vocabulary-and-langfuse-conventions.md), [`ADR-031`](ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md)

---

## 1. Context & Architectural Motivation

In the Cresmo Domain Model, channel identity and media/video identity were historically fragmented across multiple isolated primitives and primitive wrappers:

### Channel Fragmentation:
- `ChannelName` (Value Object: human-readable name, e.g., `"Canal do Meio"`)
- `ChannelId` (Value Object: platform ID, e.g., `"UCxxxx"`)
- `channel_category` (raw `str` on `SourceTranscript`)
- `channel_url` (derived or string on discovery sources)
- `ChannelTenantId` (Entity/VO formatted as `"channel:{token}"`)

### Video / Content Fragmentation:
- `ContentId` (Value Object: canonical identifier, e.g., `"dQw4w9WgXcQ"`)
- `title` (raw `str` on `SourceTranscript`)
- `source_url` (raw `str` on `SourceTranscript`)
- `SourceModality` (Enum: `URL` vs `FILE`)
- `publication_date` / `upload_date` (raw `datetime.date`)

This fragmentation caused parameter clumping and cognitive friction across the application layer. Specifically in `coordinator.py` and `context.py`:
```python
# ANTI-PATTERN: Disconnected Clump
execution_context = PipelineExecutionContext(
    session_id=session_id,
    user_identity=user_identity,
    channel_name=channel_name,
    content_id=content_id,
    channel_id=raw.channel_id,
)
```

By decoupling channel attributes from each other, downstream consumers were forced to query or pass 5+ separate parameters rather than relying on cohesive domain models.

---

## 2. Decision

We establish two canonical composite Value Objects in `src/cresmo/domain/value_objects/identity.py`:

### 2.1 The `Channel` Composite Value Object
Encapsulates complete creator/channel provenance:
- `name: ChannelName` (Human-readable channel name)
- `id: ChannelId | None` (Platform channel ID)
- `category: str` (Taxonomy/category string)
- `url: str | None` (Explicit or derived public URL)

Convenience properties & factories:
- `from_name(name, id=None, category="", url=None) -> Channel`
- `canonical_url -> str` (derives `https://www.youtube.com/channel/{id}` or `https://www.youtube.com/@{name}`)
- `tenant_key -> str` (`"channel:{id or name}"`)

### 2.2 The `Content` Composite Value Object (with `Video` alias)
Encapsulates complete target media/video provenance:
- `id: ContentId` (Canonical content identifier)
- `title: str` (Clean media title)
- `url: str` (Web source URL)
- `modality: SourceModality` (`URL` or `FILE`)
- `publication_date: datetime.date | None`

Convenience properties & factories:
- `create(id, title="", url="", modality=SourceModality.URL, publication_date=None) -> Content`
- `display_title -> str` (returns title or falls back to `id.value`)
- `Video = Content` (alias supporting natural domain terminology)

### 2.3 The 4-Pillar `PipelineExecutionContext`
`PipelineExecutionContext` is streamlined to strictly encapsulate the 4 foundational pillars of pipeline execution:
1. `session_id: PipelineSessionId`
2. `user_identity: UserIdentity`
3. `channel: Channel`
4. `content: Content`

```python
execution_context = PipelineExecutionContext(
    session_id=session_id,
    user_identity=user_identity,
    channel=raw.channel,
    content=raw.content,
)
```

In strict adherence to the **Principle of Zero Legacy Shims (ADR-010)** and **Rule 18 of ADR-026**, `PipelineExecutionContext` exposes **zero convenience properties or delegation shims**. All consumers (including `PipelineStageRunner`) navigate composite VOs directly:
- `context.channel.name`
- `context.channel.id`
- `context.content.id`
- `context.content.title`

---

## 3. Consequences

### Positive:
- **Zero Primitive Obsession (ADR-019):** Eliminates loose string clumping across the application layer.
- **Cognitive Clarity:** Pipeline execution binds exactly four well-defined architectural pillars: Session, User, Channel, Content.
- **Symmetric Aggregate Integration:** `SourceTranscript` and `FluidTranscript` expose cohesive `.channel` and `.content` properties.
- **Architectural Purity & Zero Legacy Shims (ADR-010, ADR-026 Rule 18):** No synthetic wrapper properties or backward-compatible aliases dilute the domain aggregates.

### Negative / Trade-offs:
- Downstream callers and test assertions must access child Value Objects explicitly (`context.channel.name`, `context.content.id`).
