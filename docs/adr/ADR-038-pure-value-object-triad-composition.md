# ADR-038: Pure Value Object Triad Composition for Transcripts and Zero Property Sprawl

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-10-07                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Domain Core, Entities, Value Objects, Adapters, Pipeline Esteira    |
| **Relates** | ADR-000, ADR-001, ADR-019, ADR-028, ADR-031, ADR-032, ADR-037       |

---

## 1. Context & Architectural Motivation

Inspection of intermediate pipeline artifacts revealed severe **Domain Anemia** and **Property Sprawl** in Cresmo's core entities:
Both `SourceTranscript` and `FluidTranscript` accumulated over 12 flattened, redundant attributes (`content_id`, `channel_name`, `channel_id`, `channel_category`, `title`, `source_url`, `publication_date`, `upload_date`, `video_description`, `body`), accompanied by `@property def channel` and `@property def content` accessors that rebuilt composite objects on every invocation:

```python
# ANTE: Flat property sprawl and on-the-fly object reconstruction
FluidTranscript(
    content_id=ContentId('9IbNJ0EsTxI'),
    channel_name=ChannelName('Marcelo Andrade'),
    channel_id=ChannelId('UCP3CtEXi5nxbhei_aBfIOVA'),
    title='AFONSO HENRIQUES...',
    source_url='https://youtu.be/9IbNJ0EsTxI',
    # + 7 redundant fields already encapsulated by Channel or Content!
)
```

This caused three fundamental architectural defects:
1. **Primitive Obsession & Redundancy:** Identical identities and texts existed in dual representations (`channel_name` as VO and string; `upload_date` and `publication_date` as redundant aliases).
2. **Fragile Parity Invariants:** Algorithmic (`channel_id` - `content_id`) and Cognitive (`channel_name` - `content_title`) parity were split across disconnected root attributes rather than enforced structurally.
3. **Transient Object Re-allocation:** Repeatedly calling `transcript.channel` or `transcript.content` instantiated new objects on the heap, degrading throughput and violating Domain Aggregate Cohesion.

---

## 2. Banished Anti-Patterns

This ADR formally bans three structural anti-patterns with **zero backward compatibility**:

* **`Flat Transcript Property Sprawl*`**: Flattening cohesive sub-domains (creator, provenance, content payload) into loose, primitive fields on the aggregate root.
* **`On-The-Fly Value Object Regeneration*`**: Computing composite Value Objects inside dynamic property getters instead of persisting immutable references.
* **`Duplicate Temporal Aliasing*`**: Maintaining legacy date aliases (`upload_date` alongside `publication_date`).

---

## 3. Decision: Pure 3-Value-Object Triad Composition

We refactor all transcript aggregates in Cresmo into a pure composition of three highly cohesive, immutable Value Objects:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           TRANSCRIPT AGGREGATE ROOT                            │
├────────────────────────────────────────────────────────────────────────────────┤
│ 1. Channel (Origin & Creator)                                                  │
│    • id: ChannelId (Algorithmic Key)                                           │
│    • name: ChannelName (Cognitive Key)                                         │
│    • category: str                                                             │
│    • url: str | None                                                           │
│                                                                                │
│ 2. MediaProvenance (Acquisition & Temporal Context)                            │
│    • url: str                                                                  │
│    • description: str                                                          │
│    • publication_date: date | None                                             │
│                                                                                │
│ 3. Content (Textual Artifact & Payload)                                        │
│    • id: ContentId (Algorithmic Key)                                           │
│    • title: str (Cognitive Key)                                                │
│    • body: str (Unified canonical payload for raw or fluid prose)               │
│                                                                                │
│ 4. Metadata: dict[str, Any] (Extensible Stage Provenance)                      │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Structural Parity Invariants

The triad guarantees structural parity across the entire ecosystem:
* **Algorithmic Pair (ID - ID Parity):**
  `transcript.channel.id` $\iff$ `transcript.content.id`
* **Cognitive Pair (TXT - TXT Parity):**
  `transcript.channel.name` $\iff$ `transcript.content.title`

### 3.2 Aggregate Contracts

1. **`SourceTranscript`:** Verbatim transcription aggregate containing `(channel, provenance, content, metadata)`.
2. **`FluidTranscript`:** Detranscribed neutral prose aggregate containing `(channel, provenance, content, metadata)`.
3. **`Transcript`:** Root aggregate encompassing the lifecycle across stages:
   ```python
   @dataclass(frozen=True, slots=True)
   class Transcript:
       source: SourceTranscript | None = None
       fluid: FluidTranscript | None = None
   ```

---

## 4. Consequences & Verification

* **High Cohesion, Low Coupling:** Transcripts are strictly composed of VOs with single responsibilities.
* **Zero Duplicate State:** Elimination of `upload_date`, loose `channel_id`/`channel_name` properties, and divergent `body`/`text`/`transcription` naming.
* **Direct Telemetry Alignment:** Telemetry adapters bind directly to `transcript.channel` and `transcript.content` without impedance mismatch.
