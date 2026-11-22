# ADR-066: Hybrid Semantic Saturation, Pure Convergence Domain, and Hexagonal Text Embedding Adapters

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-11-21                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Cresmo Knowledge Synthesis Bounded Context — Domain, Application, Infrastructure, Bootstrap |
| **Relates** | ADR-000, ADR-010, ADR-011, ADR-017, ADR-026, ADR-031, ADR-039, ADR-041, ADR-046, ADR-052, ADR-063, ADR-065 |

---

## 1. Context & Architectural Motivation

Multi-pass refinement in `gap_filler` (`ADR-046`) relies on mechanical early stopping to halt iterative expansion once consecutive passes stop yielding genuine epistemic gains. Auditing `src/cresmo/domain/services/mechanical_validator.py`, `src/cresmo/application/pipeline/stage_execution.py`, and `src/cresmo/infrastructure/resources/prompts.json` exposed five structural defects:

1. **Single Responsibility Principle (SRP) Violation in `mechanical_validator.py`:**
   - `mechanical_validator.py` mixes two unrelated domain responsibilities inside one module: stateless Layer 1 syntactic pre-flight guards (`validate_fluid_prose_mechanical_invariants`, `validate_gap_filler_mechanical_invariants`, `extract_complementary_section`) and stateful inter-pass convergence detection (`check_complementary_mechanical_saturation`).
2. **Brittle Extra-Info-Only Lexical Saturation:**
   - `check_complementary_mechanical_saturation` inspects only `### Extra Info` item-count deltas (`max_delta_items=5`) and lowercased `**...**` bold-entity subset inclusion. It is completely blind to substantive causal, historical, or mechanistic expansion in the main prose body, while misclassifying paraphrase noise or bolded entity reshuffling across passes.
3. **Inability to Halt on Pass 1:**
   - `generate_stage_candidate` (`stage_execution.py`) initialized `previous_text: str | None = None`, and `check_complementary_mechanical_saturation` returned `False` whenever `previous_complementary` was empty. Pass 1 had no baseline comparison against `source_text` and could never halt early even when the input was already converged.
4. **Wasteful Copy-Back Saturation Exit in `prompts.json`:**
   - Under `ADR-046`, `prompts.json` (`gap_filler`) instructed the generator in `REFINE` mode: *"when no verifiable analytical gap remains, return the draft unchanged without padding or inventing ungrounded claims."* Re-emitting an entire multi-kilobyte `<draft>` wastes output tokens, increases latency and Free-Tier quota usage, and risks subtle LLM copy-drift or paraphrase noise.
5. **Opaque Boolean Saturation Verdicts:**
   - Returning a bare `bool` from `SaturationPolicy` suppresses *why* saturation triggered, hides quantitative diagnostics (`lexical_jaccard`, `word_delta_ratio`, `max_novelty`, `novel_paragraphs`, `total_paragraphs`), omits embedding provider provenance, and provides no mechanism to restore the prior baseline when an explicit stop marker is emitted.

---

## 2. Banished Anti-Patterns

In strict compliance with `ADR-000` and `ADR-010` (**Zero Backward Compatibility / Zero Legacy Shims**), this ADR formally bans:

* **`Conflated Syntax-and-Convergence Validator*`**: Mixing stateless markdown/prose syntactic pre-flight rules with inter-pass convergence evaluation inside `mechanical_validator.py`.
* **`Global Document Embedding Dilution*`**: Pooling or embedding an entire multi-page compendium as a single document vector to score novelty across passes, which mathematically dilutes localized new paragraphs or `### Extra Info` entries across thousands of unchanged tokens.
* **`Copy-Back Saturation Waste*`**: Instructing a generative LLM in `REFINE` mode to echo an entire `<draft>` unchanged to signal saturation.
* **`Opaque Boolean Saturation*`**: Returning naked `bool` values from `SaturationPolicy` without structured `SaturationReason`, numeric metrics, provider attribution, or baseline-preservation semantics.

---

## 3. Decision

### Pillar 1: Split `mechanical_validator.py` into Pure Domain Guards and Convergence Evaluators
- **Hard Deletion (`ADR-010`):** Delete `src/cresmo/domain/services/mechanical_validator.py` completely with zero compatibility shims or re-exports.
- **Syntactic Pre-Flight (`src/cresmo/domain/services/prose_syntax_guard.py`):** Pure Python stdlib module housing deterministic Layer 1 syntactic invariants:
  - `validate_fluid_prose_syntax(text: str) -> list[str]`
  - `validate_gap_filler_syntax(text: str) -> list[str]`
  - `extract_extra_info_section(text: str) -> str`
- **Pure Mathematical Convergence (`src/cresmo/domain/services/convergence_evaluator.py`):** Pure Python stdlib module (`math` + `re` ONLY; zero external ML, HTTP, or SDK imports) exporting:
  - `NO_NEW_GAPS_SENTINEL: Final[str] = "<NO_NEW_GAPS/>"`
  - `segment_semantic_units(text: str) -> tuple[str, ...]`: segments compendia into discrete paragraphs and individual numbered items (`^\s*\d+\.\s+`), conditionally sub-chunking units exceeding `120` words into overlapping 3-sentence sliding windows (overlap `1` sentence) with abbreviation-safe sentence segmentation so novelty is measured without intra-paragraph or block-level dilution.
  - `is_explicit_stop_sentinel(text: str, pass_index: int = 2) -> bool`: validates `pass_index >= 1` (non-`bool`, else `DomainValidationError`), returns `False` on `pass_index == 1`, and on `pass_index > 1` checks `text.strip() == NO_NEW_GAPS_SENTINEL`.
  - `compute_ngram_jaccard(baseline_text: str, current_text: str, n: int = 3) -> float`: deterministic n-gram Jaccard similarity (`n >= 1`, non-`bool`).
  - `compute_word_delta_ratio(baseline_text: str, current_text: str) -> float`: relative word-count delta ratio between baseline and current text.
  - `cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float`: pure `math` dot-product / L2-norm similarity with length-mismatch (`ValueError`), zero-norm guard, and `[-1.0, 1.0]` clamping.
  - `compute_maxsim_novelty(baseline_vectors: Sequence[Sequence[float]], current_vectors: Sequence[Sequence[float]], similarity_threshold: float = 0.88) -> tuple[int, float, float]`: unit-level MaxSim novelty scoring—matches each current unit vector to its highest-similarity baseline unit vector (`max cosine_similarity`), returning `(novel_count, max_novelty, mean_max_similarity)`.
  - `evaluate_lexical_convergence(baseline_text: str, current_text: str, thresholds: SaturationThresholds | None = None, pass_index: int = 2) -> SaturationVerdict | None`: evaluates explicit stop sentinel, n-gram Jaccard similarity, and word-delta ratio against `SaturationThresholds`.
  - `evaluate_semantic_convergence(baseline_vectors: Sequence[Sequence[float]], current_vectors: Sequence[Sequence[float]], thresholds: SaturationThresholds | None = None, *, lexical_jaccard: float = 0.0, word_delta_ratio: float = 0.0, provider: str = "semantic") -> SaturationVerdict`: evaluates unit-level MaxSim semantic convergence and novel-unit count from precomputed embedding vectors alongside lexical/delta bounds.

### Pillar 2: Pure Domain Convergence Value Objects (`src/cresmo/domain/value_objects/convergence.py`)
Define immutable, zero-dependency Value Objects and contracts in `src/cresmo/domain/value_objects/convergence.py`:
- `ConvergenceMode` (`StrEnum`): declarative convergence strategy (`NONE = "none"`, `HYBRID_SEMANTIC = "hybrid_semantic"`).
- `SaturationReason` (`StrEnum`): explicit termination/continuation reason (`DISABLED = "disabled"`, `EXPLICIT_SENTINEL = "explicit_sentinel"`, `LEXICAL_IDENTITY = "lexical_identity"`, `SEMANTIC_PLATEAU = "semantic_plateau"`, `NOVEL_CONTENT = "novel_content"`).
- `SaturationThresholds` (`@dataclass(frozen=True, slots=True)`): validated threshold bundle (`lexical_identity_threshold: float = 0.95`, `max_lexical_word_delta: float = 0.03`, `semantic_similarity_threshold: float = 0.88`, `max_novel_paragraphs_for_saturation: int = 0`); invalid values raise `DomainValidationError`.
- `SaturationVerdict` (`@dataclass(frozen=True, slots=True)`): structured outcome containing `is_saturated: bool`, `reason: SaturationReason`, scalar metrics (`lexical_jaccard: float`, `word_delta_ratio: float`, `max_novelty: float = 1.0`, `novel_paragraphs: int = 0`, `total_paragraphs: int = 0`), `preserve_baseline: bool = False`, `provider: str = ""`, and `to_metadata_dict() -> dict[str, Any]` returning a JSON-serializable scalar dictionary with all 9 fields (`reason.value`).
- `SaturationPolicy = Callable[[str, str, int], SaturationVerdict]` (`(baseline_text: str, current_text: str, pass_index: int) -> SaturationVerdict`).
- `never_saturate(baseline_text: str, current_text: str, pass_index: int = 1) -> SaturationVerdict`: Null-Object default policy returning `SaturationVerdict(is_saturated=False, reason=SaturationReason.DISABLED, lexical_jaccard=0.0, word_delta_ratio=0.0, max_novelty=1.0, novel_paragraphs=0, total_paragraphs=0, preserve_baseline=False, provider="disabled")`.

### Pillar 3: Fixed-Point Multi-Pass Loop & `<NO_NEW_GAPS/>` Sentinel (`stage_execution.py` & `prompts.json`)
- **Fixed-Point Loop (`src/cresmo/application/pipeline/stage_execution.py`):**
  - Set `baseline_text = source_text` on Pass 1 so convergence always evaluates against a non-empty baseline from the very first pass.
  - Maintain `draft_text: str | None = None` on Pass 1 to strictly control prompt execution modes: `None` triggers `BUILD` mode (`<draft>` omitted), while populated `draft_text` on Passes 2..N triggers `REFINE` mode (`<draft pass="N-1">`).
  - Evaluate `verdict = stage_config.saturation_policy(baseline_text, current_text, pass_index)` after each pass.
  - When `verdict.preserve_baseline` is `True` (specifically when `<NO_NEW_GAPS/>` appears on Pass 2+), restore `current_text = baseline_text` before exiting (or before entering the `ADR-046` terminal `critique` pass) so the sentinel never leaks into `CandidateText`.
  - On non-saturated continuation, advance `baseline_text = current_text` and `draft_text = current_text`.
- **Prompt Catalog Update (`src/cresmo/infrastructure/resources/prompts.json`):**
  - Update `gap_filler` so `REFINE` mode emits `<NO_NEW_GAPS/>` when no verifiable analytical gap remains, while `BUILD` mode (Pass 1) always synthesizes the initial compendium and never emits `<NO_NEW_GAPS/>`.

### Pillar 4: Hexagonal `TextEmbeddingPort`, `HybridSaturationEvaluator`, and Stage Wiring
- **Application Port (`src/cresmo/application/ports/embedding.py`):**
  - `TextEmbeddingPort(ABC)` defines batch text embedding (`embed_batch(self, texts: Sequence[str]) -> list[list[float]]`) and provider identity (`@property def provider_name(self) -> str`), isolating vector providers from Domain and Application logic.
- **Application Service (`src/cresmo/application/services/hybrid_saturation.py`):**
  - `HybridSaturationEvaluator` implements a two-tier cascade satisfying `SaturationPolicy`:
    1. **Tier 1 (Zero-Cost Domain Lexical Gate):** Invokes `evaluate_lexical_convergence` (`<NO_NEW_GAPS/>` sentinel on Pass 2+, n-gram Jaccard, and word-delta ratio). Short-circuits immediately on saturation without invoking `TextEmbeddingPort`.
    2. **Tier 2 (Unit-Level Semantic MaxSim Gate):** Segments `baseline_text` and `current_text` via `segment_semantic_units`, embeds units via `TextEmbeddingPort`, and delegates final convergence calculation to pure Domain `evaluate_semantic_convergence` (`compute_maxsim_novelty`).
- **Declarative Domain vs. Application Factory Binding:**
  - `StageDefinition` (`src/cresmo/domain/stage_registry.py`) stores declarative `convergence_mode: ConvergenceMode` (e.g., `ConvergenceMode.HYBRID_SEMANTIC` for `gap_filler`, `ConvergenceMode.NONE` for `fluid_prose`) rather than coupling Domain definitions to Application policies.
  - `StageFactory` (`src/cresmo/application/pipeline/stage_factory.py`) inspects `stage_definition.convergence_mode` and binds the concrete `SaturationPolicy` (`HybridSaturationEvaluator` for `HYBRID_SEMANTIC` or `never_saturate` for `NONE`, preserving explicit call-site overrides).

### Pillar 5: Infrastructure Embedding Adapters & `CresmoSettings` Configuration
Implement concrete embedding adapters under `src/cresmo/infrastructure/adapters/embeddings/`:
1. **`GeminiEmbeddingAdapter` (Default Cloud Adapter):**
   - Configured with `gemini-embedding-001`, `task_type="SEMANTIC_SIMILARITY"`, and `output_dimensionality=768` (`GeminiEmbeddingAdapter(api_key=None, model_name=DEFAULT_GEMINI_EMBEDDING_MODEL, dimensions=DEFAULT_GEMINI_EMBEDDING_DIMENSIONS, genai_client=None, credential_pool=None, api_keys=None, timeout_seconds=30.0)`).
   - Reuses `GeminiCredentialPool` (`ADR-041`) for thread-safe quota-aware API key rotation and cooldown failover.
   - Chunks embedding inputs into batches of at most `100` items per API request.
2. **`OllamaEmbeddingAdapter` (Local Swap Adapter):**
   - Targets Ollama's `/api/embed` endpoint using `nomic-embed-text` (`OllamaEmbeddingAdapter(base_url="http://localhost:11434", model=DEFAULT_OLLAMA_EMBEDDING_MODEL, timeout_seconds=30.0)`) for zero-egress local embeddings.
3. **`TfidfEmbeddingAdapter` (Offline Deterministic Fallback):**
   - Constructed with `TfidfEmbeddingAdapter()` and uses a **lazy import** of `scikit-learn` (`TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, norm="l2")`), preserving `ADR-053`/`ADR-055` fast CLI startup while guaranteeing zero-network execution.
4. **`ResilientEmbeddingAdapter` (Resilience Wrapper):**
   - Wraps `primary: TextEmbeddingPort` and `fallback: TextEmbeddingPort | None = None` (defaults to `TfidfEmbeddingAdapter()`) with automatic fallback on `EmbeddingInfrastructureError`, exposing `last_provider_name` and setting `f"{fallback.provider_name}_fallback"` (e.g., `"tfidf_fallback"`) on primary failure for telemetry attribution.

Add corresponding configuration fields in `CresmoSettings` (`src/cresmo/infrastructure/config.py`) and `PipelineSettingsProtocol`:
- `CRESMO_EMBEDDING_PROVIDER` (default `"gemini"`)
- `CRESMO_GEMINI_EMBEDDING_MODEL` (default `"gemini-embedding-001"`)
- `CRESMO_GEMINI_EMBEDDING_DIMENSIONS` (default `768`)
- `CRESMO_OLLAMA_EMBEDDING_MODEL` (default `"nomic-embed-text"`)
- `CRESMO_SATURATION_LEXICAL_THRESHOLD`
- `CRESMO_SATURATION_MAX_WORD_DELTA`
- `CRESMO_SATURATION_SEMANTIC_THRESHOLD`
- `CRESMO_SATURATION_MAX_NOVEL_PARAGRAPHS`

---

## 4. Langfuse Ingestion Strategy

### 4.1 Hierarchical Saturation Span (`ADR-065` Extension)
Extend `src/cresmo/application/ports/telemetry.py` with `format_stage_saturation_span_name(stage_name: str, pass_num: int) -> str`, emitting `cresmo.{stage}.saturation.pass_{N}` directly under `cresmo.{stage_name}`:

```text
[Trace]        cresmo.pipeline
  └── [Root]   cresmo.coordinator
        └── [Stage]    cresmo.{stage_name}
              ├── [Gen]         cresmo.{stage_name}.generate.pass_{N}
              ├── [Saturation]  cresmo.{stage}.saturation.pass_{N}
              └── [Judge]       cresmo.{stage_name}.judge
```

### 4.2 Scalar Telemetry Attributes (Zero Raw Text — LGPD Compliant)
Every `cresmo.{stage}.saturation.pass_{N}` span records strictly scalar attributes derived from `SaturationVerdict`, with zero raw `baseline_text`, `current_text`, or paragraph strings:
- `cresmo.pass_num` (`int`)
- `cresmo.saturation.is_saturated` (`bool`)
- `cresmo.saturation.reason` (`str`: `SaturationReason.value`)
- `cresmo.saturation.lexical_jaccard` (`float`)
- `cresmo.saturation.word_delta_ratio` (`float`)
- `cresmo.saturation.max_novelty` (`float`)
- `cresmo.saturation.novel_paragraphs` (`int`)
- `cresmo.saturation.total_paragraphs` (`int`)
- `cresmo.saturation.preserve_baseline` (`bool`)
- `cresmo.saturation.provider` (`str`: active provider identifier, e.g. `gemini`, `ollama`, `tfidf`, `tfidf_fallback`, `lexical`, `sentinel`, `degraded`, or `disabled`)

### 4.3 Langfuse Prompt Reseed Requirement
Because `prompts.json` (`gap_filler`) replaces copy-back saturation with `<NO_NEW_GAPS/>` emission in `REFINE` mode, operators must re-seed `cresmo-gap-filler` in Langfuse (`cresmo seed-prompts`) so remote Langfuse prompt versions align with local `prompts.json` (`ADR-052`).

### 4.4 Saturation Score & Threshold Reference Table

| Signal / Gate | `CresmoSettings` Key | Evaluation Scope | Triggered `SaturationReason` | Telemetry Attribute |
| :--- | :--- | :--- | :--- | :--- |
| Explicit Stop Sentinel | *(constant `<NO_NEW_GAPS/>`)* | Pass 2+ (`REFINE` mode) | `EXPLICIT_SENTINEL` (`preserve_baseline=True`) | `cresmo.saturation.reason` |
| Lexical Jaccard & Word Delta | `CRESMO_SATURATION_LEXICAL_THRESHOLD`, `CRESMO_SATURATION_MAX_WORD_DELTA` | Full-text n-gram Jaccard + relative word delta | `LEXICAL_IDENTITY` | `cresmo.saturation.lexical_jaccard`, `cresmo.saturation.word_delta_ratio` |
| Semantic MaxSim & Novel Units | `CRESMO_SATURATION_SEMANTIC_THRESHOLD`, `CRESMO_SATURATION_MAX_NOVEL_PARAGRAPHS` | Unit-level `compute_maxsim_novelty` via `TextEmbeddingPort` | `SEMANTIC_PLATEAU` | `cresmo.saturation.max_novelty`, `cresmo.saturation.novel_paragraphs`, `cresmo.saturation.total_paragraphs` |
| Policy Disabled / Continue | `ConvergenceMode.NONE` or thresholds unmet | Per-pass | `DISABLED` / `NOVEL_CONTENT` | `cresmo.saturation.is_saturated=false` |

---

## 5. Alternatives Considered

1. **Whole-Document Embedding Pooling:**
   - Embedding entire `baseline_text` and `current_text` compendia as single vectors and comparing global cosine similarity. Rejected because localized additions of 1–2 dense causal paragraphs or `### Extra Info` entries get diluted by thousands of unchanged tokens (`Global Document Embedding Dilution*`), triggering false early saturation.
2. **Per-Pass LLM-as-a-Judge Saturation Check:**
   - Calling `LlmJudgePort` after each pass to decide whether remaining gaps justify another pass. Rejected due to multiplied token cost, latency overhead, Free-Tier quota exhaustion, and non-deterministic halting relative to deterministic MaxSim + sentinel checks.
3. **Regex-Only / Extra-Info-Only Heuristics:**
   - Extending `mechanical_validator.py` with more regex patterns over `### Extra Info` and bolded entities. Rejected because syntactic formatting belongs in `prose_syntax_guard.py` (SRP), while regex cannot detect synonymous paraphrasing or main-body semantic growth.

---

## 6. Consequences, Security & LGPD

- **Positive:**
  - Enforces strict Hexagonal purity: Domain contains zero-dependency math and syntax guards (`math` + `re` only), Application owns `TextEmbeddingPort` and `HybridSaturationEvaluator`, and Infrastructure encapsulates Gemini/Ollama/TF-IDF adapters.
  - Eliminates copy-back token waste in `gap_filler` via `<NO_NEW_GAPS/>` while guaranteeing deterministic baseline preservation (`preserve_baseline=True`).
  - Resilient offline fallback (`ResilientEmbeddingAdapter` $\to$ `TfidfEmbeddingAdapter`) preserves pipeline liveness without harming CLI startup speed (`ADR-053`).
  - Full Langfuse trace visibility via `cresmo.{stage}.saturation.pass_{N}` spans and scalar `cresmo.saturation.*` attributes.
- **Breaking / Migration (`ADR-010`):**
  - `src/cresmo/domain/services/mechanical_validator.py` is permanently deleted; callers migrate to `prose_syntax_guard.py` and `convergence_evaluator.py`.
  - `StageDefinition` declares `convergence_mode: ConvergenceMode` instead of binding `saturation_policy` directly.
  - `SaturationPolicy` consumers migrate from `bool` to `SaturationVerdict`.
  - `cresmo-gap-filler` requires Langfuse reseeding.
- **Security & LGPD:**
  - `GeminiEmbeddingAdapter` reuses `GeminiCredentialPool` (`ADR-041`) with zero secret logging.
  - Saturation spans export strictly scalar convergence metrics and provider names (`cresmo.saturation.*`), with zero raw transcript or draft text attached.
  - Zero-egress deployments can route embeddings locally through `OllamaEmbeddingAdapter` (`nomic-embed-text`) or offline `TfidfEmbeddingAdapter` via `CRESMO_EMBEDDING_PROVIDER`.
