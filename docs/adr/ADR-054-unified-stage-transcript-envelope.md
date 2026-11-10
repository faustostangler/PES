# ADR-054: Unified Stage Transcript Envelope and Stage-Invariant Polymorphism

## Status
ACCEPTED (PARTIALLY SUPERSEDED and REFINED by [`ADR-057`](ADR-057-monomorphic-stage-transcript-envelope-and-pure-triad-ingestion.md))

> [!WARNING]
> **REFINEMENT NOTICE (ADR-057):**  
> While ADR-054 introduced `StageTranscript` and established the 3-VO Triad hierarchy, §1's convenience keyword argument initialization (`content_id`, `source_url`, `body`) and Markdown syntax table validation (`_TABLE_PATTERN`) were **SUPERSEDED by [`ADR-057`](ADR-057-monomorphic-stage-transcript-envelope-and-pure-triad-ingestion.md)**. `StageTranscript` is strictly monomorphic with pure VO injection, relegating formatting and Markdown checks to stage descriptors and `LlmJudgePort`.

## Context
Across the Cresmo pipeline (`src/cresmo/domain/entities/`), transcripts undergo sequential transformations across multiple pipeline stages:
1. **Raw Ingestion**: Spoken/verbatim audio capture (`SourceTranscript`).
2. **Stage 1 (Fluid Prose)**: Detranscription into neutral continuous prose (`FluidTranscript`).
3. **Stage 2 (Socratic Gap Filling)**: Factual expansion with encyclopedic notes (`EnrichedCompendium`).
4. **Future Stages (Long/Wide Expansion)**: Deep historical and synchronic cross-sections.

### Current Architectural Deficiencies
1. **Redundant Boilerplate Duplication**: `SourceTranscript` and `FluidTranscript` declare the identical 3-Value-Object Triad (`channel`, `provenance`, `content`, `metadata`), duplicating over 100 lines of `__init__` constructor parameter resolution and `create()` factory boilerplate.
2. **Domain Anemia in Downstream Stages**: `EnrichedCompendium` diverges completely from ADR-038's 3-VO Triad, reverting to 12 flattened primitive fields (`channel_name`, `channel_id`, `video_date`, etc.).
3. **Pervasive Duck-Typing Spaghetti**: Because stages lacked a common domain ancestor or interface, pipeline coordinators and descriptors resorted to fragile dynamic checks:
   ```python
   raw_text = (
       getattr(getattr(source, "content", None), "body", None)
       or getattr(source, "body", None)
       or getattr(source, "text", None)
       or str(source)
   )
   ```
4. **Zero Type-State Invariant Sharing**: While `SourceTranscript` and `FluidTranscript` share identical structural properties, their validation rules (e.g. table rejection in fluid prose vs verbatim retention in source) are scattered across individual classes without a unified template method.

---

## Decision

### 1. Abstract Base Aggregate: `StageTranscript`
Introduce an immutable base dataclass `StageTranscript` in `src/cresmo/domain/entities/transcripts.py` that encapsulates:
- The canonical 3-Value-Object Triad:
  - `channel: Channel`
  - `provenance: MediaProvenance`
  - `content: Content`
  - `metadata: dict[str, Any]`
- Standardized, pure property accessors:
  - `body -> str` (delegates to `self.content.body`)
  - `title -> str` (delegates to `self.content.title`)
  - `content_id -> ContentId` (delegates to `self.content.id`)
  - `channel_name -> ChannelName` (delegates to `self.channel.name`)
  - `channel_id -> ChannelId | None` (delegates to `self.channel.id`)
- Template method `_validate_stage_invariants()` executed during initialization.
- Unified ergonomic initialization supporting both direct Value Object injection and convenience primitives.

### 2. Concrete Specialized Stage Artifacts
Specialized stage types inherit from `StageTranscript`, implementing only their stage-specific invariants and domain payloads:
- **`SourceTranscript(StageTranscript)`**:
  - Invariant: `content.body` must not be empty or pure whitespace.
- **`FluidTranscript(StageTranscript)`**:
  - Invariant: `content.body` must not be empty and must not contain Markdown tables (`_TABLE_PATTERN`).
- **`EnrichedCompendium(StageTranscript)`**:
  - Unifies `EnrichedCompendium` to adhere to ADR-038 Triad composition.
  - Adds stage-specific payload: `complementary_info: str` and `pass_count: int = 1`.
  - Invariants: `content.body` and `complementary_info` must not be empty; `content.body` must not contain Markdown tables; `pass_count >= 1`.

### 3. Lifecycle Progression: `Transcript` Aggregate
Refactor `Transcript` into a cohesive multi-stage lifecycle container maintaining typed references across stages (`source`, `fluid`, `compendium`) with unified provenance and channel accessors.

---

## Consequences & Verification
- **DRY Domain Core**: Eliminates ~150 lines of duplicate parameter parsing and object construction across `transcripts.py` and `compendium.py`.
- **Elimination of Fragile `getattr`**: Stage runners and descriptors can reliably query `source.content.body` or `source.body` without fallback spaghetti.
- **Strict Typing Compliance**: `mypy --strict` can enforce type-state progression between pipeline stages without resorting to `Any`.
- **Hermetic Testing**: Validated with zero mutant survival in domain invariants via `pytest` and `mutmut`.

