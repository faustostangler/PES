# ADR-033: Composite Value Objects with Identity VOs, Parity, and Tenant Simplification

**Status:** ACCEPTED  
**Date:** 2026-10-02  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [`ADR-019`](ADR-019-sota-kiss-nomenclature-and-channel-name-value-object.md), [`ADR-026`](ADR-026-clean-code-anti-patterns-and-code-smell-governance.md), [`ADR-027`](ADR-027-unified-telemetry-vocabulary-and-langfuse-conventions.md), [`ADR-032`](ADR-032-composite-channel-and-content-value-objects.md)

---

## 1. Context & Architectural Motivation

Following the establishment of composite Value Objects in ADR-032 (`Channel` and `Content`), runtime inspection of the pipeline coordinator revealed conceptual redundancies, asymmetric nesting, and vocabulary friction:

1. **VO-in-VO Asymmetry:**
   `Channel` nested an explicit single-field `ChannelName(value='...')` for `name`, while `category` and `url` were primitive strings. This caused visual noise in representations (`Channel(name=ChannelName(value='...'), id=ChannelId(value='...'))`) and raised the question of whether every attribute should be wrapped or if composite VOs should self-validate.
2. **Session Vocabulary Friction:**
   `PipelineSessionId` exposed `.channel_token` (legacy naming from early multi-tenancy) instead of `.channel_id`, breaking parity with the `Channel` composite VO. Furthermore, it retained both `.video_id` and `.content_id` pointing to the exact same value.
3. **Tenant Redundancy:**
   `ChannelTenantId` was created as an isolated class formatting `"channel:{token}"`. Since `Channel` already provides `.tenant_key`, having a standalone `ChannelTenantId` entity/VO duplicates channel identity, forces callers to instantiate both objects, and creates unnecessary ceremony in pipeline coordination.

---

## 2. Anti-Patterns Formalized & Banned

We explicitly formalize and ban two competing architectural anti-patterns in the Cresmo codebase:

### 2.1 Anti-Pattern: *Primitive Obsession Obsession & Class Explosion*
- **Description:** Wrapping every leaf primitive attribute into a single-field class (`ChannelCategory`, `ChannelUrl`, `ContentTitle`, `ContentUrl`), or wrapping `name` into `ChannelName` inside `Channel` where `Channel` is already the encapsulating domain Value Object.
- **Why it is banned:** In Domain-Driven Design (Evans, Vernon), Value Objects must represent concepts that possess independent domain invariants, distinct arithmetic/logic, or autonomous lifecycles. Creating dummy 1-field wrappers for every string causes class explosion, cognitive fatigue, and verbose unwrapping chains (`obj.category.value`) with zero real type-safety gain.

### 2.2 Anti-Pattern: *Primitive Obsession Reversa (Reverse Primitive Obsession)*
- **Description:** Stripping strongly-typed domain identifiers (`ChannelId`, `ContentId`) down to raw strings (`str`) inside entities and composite VOs under the guise of simplification.
- **Why it is banned:** `ChannelId` and `ContentId` are platform-specific **Identity Value Objects**. They encapsulate critical security invariants (prohibiting shell injection and path traversal), complex URL extraction logic (`from_url_or_token`), YouTube platform normalization (`UC...` to `UU...`), and cross-context lookup capability. Demoting them to raw strings reintroduces parameter-swapping bugs and scatters regex validation across the application layer.

---

## 3. Decision

We establish the **Composite Value Object with Identity VOs (Composição Híbrida Assimétrica Intencional)** pattern as the canonical standard, and execute the following simplifications with **zero backward compatibility**:

```
                       ┌─────────────────────────┐
                       │  Channel (Composite VO) │
                       ├─────────────────────────┤
                       │ name: str               │ ◄── Validated String Field (invariants enforced)
                       │ id: ChannelId | None    │ ◄── Standalone Identity VO
                       │ category: str           │ ◄── Validated String Field
                       │ url: str | None         │ ◄── Validated String Field / Derived
                       │ tenant_key -> str       │ ◄── Intrinsic Tenant Format ("channel:{token}")
                       └─────────────────────────┘
```

### 3.1 Composite Value Objects with Identity VOs
1. **`Channel` Composite VO:**
   - `name: str` — Enforces invariants upon construction (non-empty, trimmed, max 120 chars, prohibits path traversal `..`, `/`, `\`). Coerces `ChannelName` or primitive `str`.
   - `id: ChannelId | None` — Strongly-typed platform identity VO.
   - `category: str` — Trimmed taxonomy tag.
   - `url: str | None` — Canonical source URL.
   - `tenant_key: str` — Canonical tenant identifier (`"channel:{id or name}"`).
2. **`Content` Composite VO:**
   - `id: ContentId` — Strongly-typed media identity VO.
   - `title: str` — Media title. Sole canonical field; redundant `display_title` fallback property is eliminated.
   - `url: str` — Canonical media URL.
   - `modality: SourceModality` — Discriminator enum (`URL` vs `FILE`).
   - `publication_date: datetime.date | None` — Publication timestamp.
   - **Removal of `Video = Content` Alias:** Legacy type alias `Video` is removed from domain exports.

### 3.2 `PipelineSessionId` and Context Deprecation Clean-up
1. Rename property `.channel_token` to **`.channel_id`**, maintaining exact parity with `Channel.id`.
2. **Remove property `.video_id`**. Only `.content_id` is retained.
3. **`PipelineExecutionContext` Clean-up (Pure 4-Pillar Model):**
   - Remove legacy alias property `.video`.
   - Remove backward-compatible initialization kwargs (`channel_name`, `content_id`, `channel_id`). The context strictly requires composite `channel: Channel` and `content: Content`.
   - **Eradicate all convenience accessors & delegation shims** (`.channel_name`, `.channel_id`, `.content_id`, `.channel_id_str`, `.content_id_str`, `.content_title`) per ADR-026 Rule 18. Callers navigate composite VOs directly (`context.channel.name`, `context.content.id`).
4. **Zero Legacy Shims:** No backward-compatible aliases, delegation shims, or property wrappers are preserved (ADR-010).

### 3.3 Decommissioning of `ChannelTenantId`
1. **`ChannelTenantId` is deleted from the domain**.
2. Tenant representation is an intrinsic responsibility of `Channel` via `channel.tenant_key`.
3. In `coordinator.py`:
   - Eliminate `tenant_id = ChannelTenantId.create(...)`.
   - Pass `channel_tenant_id=channel.tenant_key` directly to `telemetry_port.start_pipeline_session`.
4. In `TelemetryPort`:
   - Update signature: `channel_tenant_id: str | None = None`.
   - In OpenTelemetry adapters, receive `channel_tenant_id` as `str | None`.

---

## 4. Consequences

### Positive:
- **Clean Representation:** `repr(channel)` displays clean attributes without redundant `ChannelName(value=...)` wrappers.
- **Unified Domain Vocabulary:** Parity between `Channel.id`, `PipelineSessionId.channel_id`, and `PipelineSessionId.content_id`.
- **Elimination of Dead Weight:** Removes `ChannelTenantId` and `PipelineSessionId.video_id`, simplifying the codebase.
- **Strict Adherence to SOTA-KISS:** Strikes the exact balance between domain richness (Identity VOs) and lean developer ergonomics (validated composite fields).

### Negative / Trade-offs:
- **Breaking Changes:** Downstream code expecting `ChannelTenantId`, `.channel_token`, or `.video_id` must be refactored immediately (consistent with zero backward compatibility instruction).
