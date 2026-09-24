# ADR-019: SOTA-KISS Nomenclature Alignment, Port Role Suffixes, and ChannelName Domain Value Object

**Status:** ACCEPTED  
**Date:** 2026-09-24  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, Zero Primitive Obsession, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-007`](ADR-007-pipeline-template-method-dry.md), [`ADR-011`](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md), [`ADR-012`](ADR-012-multi-criteria-sync-filtering-and-alphabetical-feed-ordering.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [`ADR-014`](ADR-014-active-preflight-probes-and-fail-fast-observability.md), [`ADR-016`](ADR-016-full-opentelemetry-conventions-session-replays-and-channel-governance.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md)

---

## 1. Context & Architectural Forces

In Cresmo's Hexagonal Modular Monolith, audio and video transcripts are synthesized through a multi-stage pipeline ([`ADR-007`](ADR-007-pipeline-template-method-dry.md)) utilizing large language models across two distinct business stages:
1. **Stage 1b — Raw Transcript Conceptual Indexing:** Summarizes transcript concepts, evaluates quality via LLM-as-a-Judge loops ([`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md)), and indexes YouTube metadata into the channel catalog.
2. **Stages 2–6 — Knowledge Synthesis:** Transforms raw audio text through Socratic gap-filling, longitudinal/synchronic expansion, atomic inventory discovery, batch note synthesis, and MOC reconciliation.

A comprehensive codebase audit against the **Doctor Stangler Method** revealed several structural nomenclature and design inconsistencies that violate Clean Architecture symmetry and Domain-Driven Design (DDD) Ubiquitous Language:

### 1.1 Inconsistent LLM Port Naming (Conflating Technology with Domain Roles)
The `LLMTransformationPort` contract is injected under disparate names:
- `self.llm_port` in `CresmoPipeline` and five synthesis use cases (`fill_gaps_fluid_prose`, `expand_longitudinal_synchronic`, `discover_atomic_inventory`, `synthesize_atomic_batch`, `reconcile_mocs`).
- `self.indexing_llm_port` in `CresmoPipeline`.
- `self.llm` in `IndexRawTranscriptsUseCase`.

**Problem:** `llm_port` names the technology ("LLM") rather than the business role it fulfills, while `self.llm` completely omits the `_port` suffix, creating cognitive friction and inconsistent architectural abstractions.

### 1.2 Primitive Obsession Violations (Doctor Stangler Rule 1)
Three pervasive domain concepts are currently represented as unvalidated primitives:
1. **`channel_name: str` (Suggestion B2):** A raw string appears in `RawTranscript`, `EnrichedCompendium`, `DiscoveredMediaItem`, and over 20 method signatures across use cases, ports, and adapters. While `RawTranscript.__post_init__` checks `strip()`, `EnrichedCompendium` and downstream methods allow unvalidated or whitespace strings, permitting invalid domain states to propagate silently.
2. **`BatchSource.kind: str` (Suggestion A3):** Represented as a bare string with `"file"` or `"url"` semantics. Passing an arbitrary string causes silent downstream failure instead of compile-time/construction-time rejection.
3. **`video_date: str` vs. `upload_date: datetime.date | None` (Suggestion B1):** The same semantic publication date is named `upload_date` (typed as `datetime.date`) in `RawTranscript`, but named `video_date` (typed as raw unparsed `str`) in `EnrichedCompendium`.

### 1.3 Asymmetric Port Suffixes
In `IndexRawTranscriptsUseCase`, the vault persistence port is injected as `vault_repo` (`self.vault_repo = vault_repo`), whereas every other use case across Cresmo uniformly uses `vault_port` (`self.vault_port = vault_port`).

### 1.4 Vestigial Duck-Typing (`hasattr`)
In `pipeline.py` and `index_raw_transcripts.py`, port calls wrap `warmup()` in `if hasattr(..., "warmup"):` checks. However, `LLMTransformationPort` already guarantees `warmup(timeout_seconds: float | None = None) -> None` with a default no-op implementation. Defensively duck-typing an explicit ABC contract violates Hexagonal purity.

### 1.5 Heterogeneous Use Case Execution Method Signatures (Suggestion C2)
While standard Clean Architecture use cases expose `execute(...)` as their primary orchestrator method, `ConcatMasterUseCase` exposes `execute_for_channel(...)`, and `IndexRawTranscriptsUseCase` exposes `index_single_transcript(...)`.

### 1.6 Inconsistent Inference Configuration Tunables (Suggestion B4)
In `config.py`, temperature tunables were named `llm_temperature` (for synthesis) and `raw_index_temperature` (for indexing), deviating from the domain role taxonomy.

---

## 2. Decision

We will systematically align the codebase with SOTA-KISS and Doctor Stangler Ubiquitous Language conventions through an atomic refactoring:

### 2.1 Role-Based LLM Port Suffixes (`llm_synthesis_port` & `llm_indexing_port`)
All occurrences of LLM transformation ports will be renamed to explicitly reflect both their technology tier and business role:
- **`llm_synthesis_port`**: Injected into `CresmoPipeline`, `FillGapsFluidProseUseCase`, `ExpandLongitudinalSynchronicUseCase`, `DiscoverAtomicInventoryUseCase`, `SynthesizeAtomicBatchUseCase`, and `ReconcileMOCsUseCase`.
- **`llm_indexing_port`**: Injected into `CresmoPipeline` and `IndexRawTranscriptsUseCase`.
- Domain roles are formalized in Ubiquitous Language as **`llm_synthesis`** and **`llm_indexing`**.

### 2.2 `ChannelName` Domain Value Object (Zero Primitive Obsession)
We introduce an immutable, self-validating Value Object `ChannelName` in `src/cresmo/domain/value_objects.py`:

```python
@dataclass(frozen=True)
class ChannelName:
    """Canonical domain Value Object representing a content creator or source channel.

    Invariants:
        - Value must be non-empty and not whitespace.
        - Automatically trimmed of leading and trailing whitespace.
        - Maximum length of 120 characters.
        - Prohibits path traversal sequences ('../' or '..\\').
    """

    value: str

    def __post_init__(self) -> None:
        val = self.value.strip()
        if not val:
            raise DomainValidationError("ChannelName cannot be empty or whitespace.")
        if len(val) > 120:
            raise DomainValidationError(
                f"ChannelName exceeds maximum length of 120 characters: '{val[:30]}...'"
            )
        if ".." in val or "/" in val or "\\" in val:
            raise DomainValidationError(
                f"ChannelName cannot contain path traversal or separator characters: '{val}'"
            )
        object.__setattr__(self, "value", val)

    @classmethod
    def from_string(cls, raw: str | ChannelName) -> ChannelName:
        """Ergonomic conversion factory accepting str or existing ChannelName."""
        if isinstance(raw, cls):
            return raw
        return cls(value=str(raw))

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ChannelName):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.strip()
        return False

    def __hash__(self) -> int:
        return hash(self.value)
```

`ChannelName` will replace raw `str` across:
- `RawTranscript.channel_name`
- `EnrichedCompendium.channel_name`
- `DiscoveredMediaItem.channel_name`
- `VaultRepositoryPort` channel methods (`get_enriched_files_for_channel`, `purge_prior_parts_for_channel`, etc.)
- Use cases (`IndexRawTranscriptsUseCase`, `ConcatMasterUseCase`, `SyncChannelUseCase`)
- Infrastructure adapters (`ObsidianVaultAdapter`)

### 2.3 `SourceModality` Enum for Batch Ingestion
We introduce `SourceModality` in `src/cresmo/domain/value_objects.py`:

```python
class SourceModality(str, Enum):
    """Discriminator for input batch source items."""
    FILE = "file"
    URL = "url"
```

In `BatchSource` (`discover_batch_sources.py`), `kind: SourceModality` enforces valid modality at instantiation, with coercion from `str` to preserve backwards ergonomics.

### 2.4 Unify Date Semantics: `publication_date: datetime.date | None`
We standardize on `publication_date` across `RawTranscript` and `EnrichedCompendium`:
- `RawTranscript.publication_date: datetime.date | None` (replacing `upload_date`, maintaining property fallback for zero breakage).
- `EnrichedCompendium.publication_date: datetime.date | None` (replacing `video_date: str`).
- The adapter translates ISO/RFC string metadata to `datetime.date` at the Anti-Corruption Layer (ACL) boundary.

### 2.5 Port Symmetry: `vault_repo` -> `vault_port`
In `IndexRawTranscriptsUseCase`, rename constructor parameter and instance attribute `vault_repo` to `vault_port`, aligning with the rest of the application layer.

### 2.6 Removal of Vestigial Duck-Typing (`hasattr`)
In `pipeline.py` and `index_raw_transcripts.py`, replace:
```python
if hasattr(self.llm, "warmup"):
    self.llm.warmup(...)
```
with direct polymorphic invocation:
```python
self.llm_indexing_port.warmup(timeout_seconds=timeout_seconds)
if self.llm_synthesis_port is not self.llm_indexing_port:
    self.llm_synthesis_port.warmup(timeout_seconds=timeout_seconds)
```

### 2.7 Config Ubiquitous Language Alignment
In `src/cresmo/infrastructure/config.py`:
- `llm_temperature` -> `llm_synthesis_temperature: float = 0.3` (with alias `llm_temperature`).
- `raw_index_temperature` -> `llm_indexing_temperature: float = 0.2` (with alias `raw_index_temperature`).

### 2.8 Universal Use Case Invocations (`execute()`)
- `ConcatMasterUseCase.execute(channel_name: ChannelName | str, ...)` becomes the primary invocation, deprecating `execute_for_channel` as a pass-through delegate.
- `IndexRawTranscriptsUseCase.execute(raw_transcript: RawTranscript, ...)` becomes the primary invocation, deprecating `index_single_transcript` as a pass-through delegate.

---

## 3. Consequences & Trade-Offs

### Positive
- **Architectural Symmetry:** Every port is explicitly named `{role}_port` or `{tech}_{role}_port`, eliminating ambiguity between synthesis and indexing LLMs.
- **Zero Primitive Obsession:** `ChannelName` and `SourceModality` eliminate invalid state bugs at compile and construction time. Illegal channel names (e.g. empty strings, path injections) are caught at the boundary.
- **Elimination of Defensive Duck-Typing:** Relies strictly on ABC contracts, honoring Liskov Substitution Principle.
- **Consistent Invocations:** Uniform `execute(...)` across all use cases simplifies composition, testing, and automated dispatch.

### Negative / Neutral
- Multi-file touchpoint (approx. 20 files across domain, application, infrastructure, and presentation).
- Requires updating unit tests and test fixtures to use `ChannelName` and the unified port names.

---

## 4. Refactoring Protocol for B2 (`ChannelName` Migration)

To guarantee zero regression during the 20+ signature migration, the refactoring proceeds in strict dependency order:

1. **Step 1 (Domain Core):**
   - Create `ChannelName` in `src/cresmo/domain/value_objects.py`.
   - Update `RawTranscript` and `EnrichedCompendium` in `src/cresmo/domain/entities.py` to use `channel_name: ChannelName`, with constructor coercion (`ChannelName.from_string(channel_name)`).
2. **Step 2 (Application Ports):**
   - Update `VaultRepositoryPort` and `PromptProviderPort` method signatures in `src/cresmo/application/ports.py` to accept `channel_name: ChannelName | str` (allowing both strongly-typed Value Objects and strings at adapter boundaries).
3. **Step 3 (Application Use Cases):**
   - Update `IndexRawTranscriptsUseCase`, `ConcatMasterUseCase`, `SyncChannelUseCase`, and `CresmoPipeline` to utilize `ChannelName`.
4. **Step 4 (Infrastructure Adapters):**
   - Update `ObsidianVaultAdapter` and `PromptProviderAdapter` to handle `ChannelName` cleanly (using `str(channel_name)` for filesystem directory resolution).
5. **Step 5 (Composition & Presentation):**
   - Update `src/cresmo/presentation/composition.py` and CLI commands.
6. **Step 6 (Tests Verification):**
   - Run unit test suite ensuring all assertions pass and 0 regressions are introduced.
