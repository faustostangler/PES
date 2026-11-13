# ADR-057: Monomorphic StageTranscript Envelope and Pure Triad Ingestion

## Status
ACCEPTED

## Context
ADR-038 introduced the 3-Value-Object Triad (`channel: Channel`, `provenance: MediaProvenance`, `content: Content`), and ADR-054 introduced `StageTranscript` as an abstract base envelope. However, several anti-patterns and leaky abstractions remained:
1. **Ergonomic Property Sprawl**: Constructors in `StageTranscript`, `SourceTranscript`, and `EnrichedCompendium` accepted dozens of optional primitive arguments (`source_url`, `publication_date`, `video_description`, `channel_name`, etc.) purely as backwards-compatibility shims, bypassing domain VO validation.
2. **LLM Syntax Leaks into Core Domain Invariants**: Entities performed regex pattern matching against Markdown tables (`_TABLE_PATTERN`) and threw `CompendiumStructureError`. Syntactic and stylistic Markdown evaluation belongs in the LLM / Judge layer (`LlmJudgePort`), not within core domain Value Object lifecycle invariants.
3. **Domain Cross-Coupling in URL Matching**: `SourceTranscript` tried to extract `ContentId` from `provenance.url` and raise `DomainValidationError` on mismatch, creating brittle coupling when alternative URL patterns or aliases were used.
4. **Subclass Fragmentation**: `EnrichedCompendium` lived in a separate file with diverging fields, while all pipeline stage outputs represent variations of a unified textual stage transcript envelope.

---

## Decision

### 1. Monomorphic `StageTranscript`
Unify all stage transcripts into a single canonical monomorphic envelope `StageTranscript` composed purely of:
- `channel: Channel` (Origin & Author)
- `provenance: MediaProvenance` (Acquisition, temporal provenance & URL)
- `content: Content` (Payload text, algorithmic ContentId, cognitive Title)
- `metadata: dict[str, Any]` (Lineage, trace IDs, extra bag)
- `complementary_info: str = ""` (Enrichment notes, encyclopedic context)
- `pass_count: int | None = None` (Number of enrichment passes, validated `pass_count >= 1` when present)

### 2. Pure Value Object Ingestion (Zero Loose Convenience Primitives)
Eliminate all convenience keyword arguments in `StageTranscript.__init__`. Callers must explicitly instantiate and provide `Channel`, `MediaProvenance`, and `Content` Value Objects. Construction from raw strings/primitives is relegated strictly to Infrastructure Adapters (e.g. `ObsidianVaultAdapter`) and Application Loaders.

### 3. Removal of Markdown Syntax Verification from Domain
Remove `_TABLE_PATTERN` and all Markdown table rejection checks from `StageTranscript` and subclasses. Formatting compliance is governed by Stage Descriptors, LLM prompts, and `LlmJudgePort` evaluators.

### 4. Complete Decommissioning of Subclasses
Completely remove `SourceTranscript`, `FluidTranscript`, `EnrichedCompendium`, and `Transcript` across the entire codebase (`src/` and `tests/`). All ports, use cases, pipeline coordinators, and infrastructure adapters operate strictly on the single monomorphic `StageTranscript` envelope and `StageName(StrEnum)` conveyor steps.

---

## Consequences
- **Domain Purity**: Zero string parsing or loose primitives inside domain entity constructors.
- **Strict Decoupling**: Markdown formatting rules decoupled from entity lifecycle.
- **SOTA-KISS**: Single unified envelope handling raw, fluid, and enriched stage transcripts.

