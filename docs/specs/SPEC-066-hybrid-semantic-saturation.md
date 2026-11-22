# SPEC-066: Hybrid Semantic Saturation, Prose Syntax Guard, and Resilient Embedding Evaluation

**Status:** APPROVED  
**Date:** 2026-11-21  
**Governing ADR:** [`ADR-066`](../adr/ADR-066-hybrid-semantic-saturation-and-text-embedding-adapters.md)  
**Relates To:** [`ADR-001`](../adr/ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-010`](../adr/ADR-010-zero-legacy-shims-and-streaming-first-unification.md), [`ADR-028`](../adr/ADR-028-decoupling-fluid-prose-and-socratic-gap-filling.md), [`ADR-031`](../adr/ADR-031-standardized-stage-descriptor-and-closed-loop-refinement.md), [`ADR-039`](../adr/ADR-039-fluid-prose-canonical-judge-criteria-and-mechanical-gates.md), [`ADR-046`](../adr/ADR-046-unified-state-driven-gap-filler-prompt.md), [`ADR-065`](../adr/ADR-065-hierarchical-stage-scoped-telemetry-nomenclature.md), [`SPEC-014`](SPEC-014-stage-descriptor-and-closed-loop-reflection.md), [`SPEC-015`](SPEC-015-fluid-prose-quality-gates-and-calibration.md), [`EVAL-002`](EVAL-002-hybrid-semantic-saturation.md), [`GLOSSARY`](../GLOSSARY.md)

---

## 1. Specification Overview & Architectural Invariants

Defines the concrete domain contracts, pure semantic convergence math, application orchestration service, resilient embedding adapters, and multi-pass pipeline integration for **Hybrid Semantic Saturation** and **`ProseSyntaxGuard`** across the Cresmo Knowledge Synthesis Bounded Context.

### 1.1 Mandatory Engineering & Hexagonal Invariants
1. **Language & Typing:** Code, docstrings, comments, and tests MUST be strictly in English, begin with `from __future__ import annotations`, and pass `mypy --strict`.
2. **Import Hygiene:** NEVER use `src.` prefixes inside `src/`. Import exclusively via `cresmo.*`.
3. **Hexagonal Dependency Direction (`Domain -> Application -> Infrastructure/Bootstrap`):**
   - **Domain Layer (`src/cresmo/domain/`):** Pure Python standard library ONLY. ZERO `sklearn`, `google.genai`, `httpx`, `urllib`, `opentelemetry`, `langfuse`, `pydantic`, `application`, or `infrastructure` imports.
   - **Application Layer (`src/cresmo/application/`):** Depends ONLY on Domain, Python stdlib, and structured logging (`structlog` / `logging`). ZERO `infrastructure` imports.
   - **Infrastructure Layer (`src/cresmo/infrastructure/`):** Implements `TextEmbeddingPort` behind Anti-Corruption Layers (ACLs), translating SDK, HTTP, and local ML failures into `EmbeddingInfrastructureError`.
4. **Zero Legacy Shims (`ADR-010`):** No backward-compatibility aliases or dual legacy code paths. `src/cresmo/domain/services/mechanical_validator.py` is deleted; `prose_syntax_guard` owns stateless syntactic invariants and `HybridSaturationEvaluator` + `convergence_evaluator` replace `check_complementary_mechanical_saturation`.
5. **Bootstrap Telemetry Invariant:** `src/cresmo/bootstrap/factories/telemetry_factory.py` retains its diagnostic `[SPAN DEBUG]` output untouched.

---

## 2. Domain Layer Contracts

### 2.1 `prose_syntax_guard` (`src/cresmo/domain/services/prose_syntax_guard.py`)
Pure stdlib (`re`) domain service enforcing deterministic structural and syntactic formatting invariants on generated Markdown compendia.

```python
def extract_extra_info_section(text: str) -> str:
    """Extract stripped content following the mandatory '### Extra Info' heading."""

def validate_fluid_prose_syntax(text: str) -> list[str]:
    """Validate deterministic syntactic invariants for fluid_prose compendia."""

def validate_gap_filler_syntax(text: str) -> list[str]:
    """Validate deterministic syntactic invariants for gap_filler compendia."""
```

#### Behavioral Contracts & Boundary Conditions
1. **`extract_extra_info_section(text: str) -> str`**:
   - Matches heading pattern `^\s*###\s+Extra\s+Info\s*$` with `re.MULTILINE`.
   - Returns `text[match.end():].strip()` when present, or `""` when absent.
2. **`validate_fluid_prose_syntax(text: str) -> list[str]`**:
   - Returns empty `list[str]` when fully compliant; non-empty list of diagnostic violation messages otherwise.
   - **Empty/Whitespace Guard:** If `not text.strip()`, immediately returns `["Text is empty or whitespace."]`.
   - **Line 1 Heading:** First non-empty line after `.strip()` must start with `"## "`.
   - **Zero YAML Frontmatter:** Must contain zero lines matching `^---\s*$` (`re.MULTILINE`).
   - **Zero Em-Dashes:** Must contain zero `"—"` characters.
   - **Zero Bullet Lists:** Must contain zero lines matching `^\s*[-*+]\s+` (`re.MULTILINE`).
   - **Zero Markdown Tables:** Must contain zero lines matching `^\s*\|.*\|\s*$` (`re.MULTILINE`) and must not satisfy `"|" in stripped and "-|-" in stripped`.
   - **Zero Blockquotes:** Must contain zero lines matching `^\s*>` (`re.MULTILINE`).
   - **Paragraph Segmentation:** Splits stripped text on `"\n\n"`, excluding blocks starting with `"##"`. If `len(body_paragraphs) == 1` and `len(body_paragraphs[0].split()) > 80`, appends a monolithic wall-of-text violation.
3. **`validate_gap_filler_syntax(text: str) -> list[str]`**:
   - **Empty/Whitespace Guard:** If `not text.strip()`, immediately returns `["Text is empty or whitespace."]`.
   - **Line 1 Heading, Zero YAML Frontmatter, Zero Em-Dashes:** Enforces identical rules to `validate_fluid_prose_syntax`.
   - **Mandatory `### Extra Info` Section:** Searches `^\s*###\s+Extra\s+Info\s*$` (`re.MULTILINE`):
     - If missing: records missing-section violation; treats entire stripped text as `main_body` and `extra_info = ""`.
     - If present: `main_body = stripped[:match.start()].strip()` and `extra_info = stripped[match.end():].strip()`. Appends explicit violation if `not main_body` or `not extra_info`.
   - **Main Body Restrictions:** Enforces zero Markdown tables, zero bullet lists (`^\s*[-*+]\s+`), and zero blockquotes (`^\s*>`) inside `main_body`.
   - **Extra Info Restrictions:** Enforces zero bullet lists (`^\s*[-*+]\s+`) inside `extra_info` (numbered continuous paragraphs `'1. '`, `'2. '` or plain continuous paragraphs are permitted).

---

### 2.2 Convergence Value Objects (`src/cresmo/domain/value_objects/convergence.py`)

```python
class ConvergenceMode(StrEnum):
    NONE = "none"
    HYBRID_SEMANTIC = "hybrid_semantic"


class SaturationReason(StrEnum):
    DISABLED = "disabled"
    EXPLICIT_SENTINEL = "explicit_sentinel"
    LEXICAL_IDENTITY = "lexical_identity"
    SEMANTIC_PLATEAU = "semantic_plateau"
    NOVEL_CONTENT = "novel_content"
```

#### `SaturationThresholds`
Frozen immutable value object (`@dataclass(frozen=True, slots=True)`):

| Field | Type | Default | Valid Bounds | Violation Exception |
| :--- | :--- | :--- | :--- | :--- |
| `lexical_identity_threshold` | `float` | `0.95` | `(0.0, 1.0]` (`0.0 < v <= 1.0`, finite, non-`bool`) | `DomainValidationError` |
| `max_lexical_word_delta` | `float` | `0.03` | `[0.0, 1.0]` (`0.0 <= v <= 1.0`, finite, non-`bool`) | `DomainValidationError` |
| `semantic_similarity_threshold` | `float` | `0.88` | `(0.0, 1.0]` (`0.0 < v <= 1.0`, finite, non-`bool`) | `DomainValidationError` |
| `max_novel_paragraphs_for_saturation` | `int` | `0` | `>= 0` (`isinstance(v, int)` and not `isinstance(v, bool)`) | `DomainValidationError` |

- Any `NaN`, `inf`, `-inf`, `bool`, or out-of-range value MUST raise `DomainValidationError` (which subclasses `ValueError`) in `__post_init__`.

#### `SaturationVerdict`
Frozen immutable value object (`@dataclass(frozen=True, slots=True)`):

| Field | Type | Default | Invariant |
| :--- | :--- | :--- | :--- |
| `is_saturated` | `bool` | required | Boolean saturation flag |
| `reason` | `SaturationReason` | required | Valid `SaturationReason` member |
| `lexical_jaccard` | `float` | required | Finite float in `[0.0, 1.0]` |
| `word_delta_ratio` | `float` | required | Finite float in `[0.0, 1.0]` |
| `max_novelty` | `float` | `1.0` | Finite float in `[0.0, 1.0]` |
| `novel_paragraphs` | `int` | `0` | Non-`bool` `int >= 0` |
| `total_paragraphs` | `int` | `0` | Non-`bool` `int >= 0` and `novel_paragraphs <= total_paragraphs` |
| `preserve_baseline` | `bool` | `False` | When `True`, `is_saturated` MUST be `True` |
| `provider` | `str` | `""` | Provider or layer identifier |

- **Cross-Field Verdict Invariants (enforced in `__post_init__` via `DomainValidationError`):**
  1. When `reason in {SaturationReason.DISABLED, SaturationReason.NOVEL_CONTENT}`: `is_saturated` MUST be `False` and `preserve_baseline` MUST be `False`.
  2. When `reason in {SaturationReason.EXPLICIT_SENTINEL, SaturationReason.LEXICAL_IDENTITY, SaturationReason.SEMANTIC_PLATEAU}`: `is_saturated` MUST be `True`.
  3. When `preserve_baseline is True`: `is_saturated` MUST be `True`.
  4. Provides `to_metadata_dict() -> dict[str, Any]` returning a JSON-serializable scalar dictionary with all 9 fields: `is_saturated`, `reason: self.reason.value`, `lexical_jaccard`, `word_delta_ratio`, `max_novelty`, `novel_paragraphs`, `total_paragraphs`, `preserve_baseline`, and `provider`.

#### `SaturationPolicy` & `never_saturate`
```python
SaturationPolicy = Callable[[str, str, int], SaturationVerdict]


def never_saturate(
    baseline_text: str,
    current_text: str,
    pass_index: int = 1,
) -> SaturationVerdict: ...
```
- `never_saturate` returns `SaturationVerdict(is_saturated=False, reason=SaturationReason.DISABLED, lexical_jaccard=0.0, word_delta_ratio=0.0, max_novelty=1.0, novel_paragraphs=0, total_paragraphs=0, preserve_baseline=False, provider="disabled")`.

---

### 2.3 Domain Convergence Evaluator (`src/cresmo/domain/services/convergence_evaluator.py`)
Pure Python stdlib (`math`, `re`, `collections.abc`, `typing`) convergence computation service.

```python
NO_NEW_GAPS_SENTINEL: Final[str] = "<NO_NEW_GAPS/>"
LONG_UNIT_WORD_CUTOFF: Final[int] = 120
SLIDING_WINDOW_SENTENCES: Final[int] = 3
SLIDING_WINDOW_OVERLAP: Final[int] = 1
```

1. **`segment_semantic_units(text: str) -> tuple[str, ...]`**:
   - Normalizes `\r\n` and `\r` to `\n` and splits on blank-line boundaries (`\n\s*\n`).
   - Strips leading/trailing whitespace from each block.
   - Ignores lines/blocks that are empty, pure Markdown heading lines (`^\s*#{1,6}\s+`), or standalone `<NO_NEW_GAPS/>` sentinel tokens.
   - Splits numbered list items (`^\s*\d+\.\s+`) within blocks into individual semantic units while keeping non-numbered multi-line paragraphs intact, preserving headings-stripped content across **both** the main body and the `### Extra Info` section so single-newline numbered items are not diluted into a single merged vector.
   - **Conditional Long-Unit Sliding Window (`> 120` words):** Units with word count `<= 120` remain intact as a single unit. Units with word count `> 120` are segmented using pure-stdlib abbreviation-safe sentence detection (`D.`, `Séc.`, `Sto.`, `Sta.`, `Dr.`, `Prof.`, `Sr.`, `Art. <digit>`, list indices `1.`, lowercase continuations) and sliced into overlapping windows of `3` sentences with overlap `1` sentence (stride `2`); units with `<= 3` sentences remain intact.
2. **`is_explicit_stop_sentinel(text: str, pass_index: int = 2) -> bool`**:
   - Validates `pass_index >= 1` and `not isinstance(pass_index, bool)` (raises `DomainValidationError` otherwise).
   - **Pass-1 Guard:** When `pass_index == 1`, ALWAYS returns `False` (ignores `<NO_NEW_GAPS/>` to forbid zero-effort stopping on Pass 1).
   - **Pass > 1:** When `pass_index > 1`, returns `text.strip() == NO_NEW_GAPS_SENTINEL`.
3. **`compute_ngram_jaccard(baseline_text: str, current_text: str, n: int = 3) -> float`**:
   - Validates `n >= 1` and `not isinstance(n, bool)` (raises `DomainValidationError` otherwise).
   - Extracts lowercase word tokens using `re.findall(r"\w+", text.lower())`.
   - Boundary cases:
     - Both token sequences empty -> `1.0`.
     - Exactly one token sequence empty -> `0.0`.
     - If `len(tokens) < n`, forms a single tuple shingle `{tuple(tokens)}`. Otherwise forms set of contiguous `n`-tuples `tuple(tokens[i : i + n])`.
   - Returns `len(shingles_base & shingles_curr) / len(shingles_base | shingles_curr)` in `[0.0, 1.0]`.
4. **`compute_word_delta_ratio(baseline_text: str, current_text: str) -> float`**:
   - Uses identical word tokenization `re.findall(r"\w+", text.lower())`.
   - Let `n_base = len(base_tokens)` and `n_curr = len(curr_tokens)`.
   - If `n_base == 0 and n_curr == 0`, returns `0.0`.
   - Otherwise returns `abs(n_curr - n_base) / max(n_curr, n_base)` in `[0.0, 1.0]`.
5. **`cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float`**:
   - If `len(vec_a) != len(vec_b)`: raises `ValueError` (`f"Vector length mismatch: {len(vec_a)} != {len(vec_b)}"`).
   - If `len(vec_a) == 0`: returns `0.0`.
   - Computes Euclidean norms `norm_a` and `norm_b`. If `norm_a == 0.0` or `norm_b == 0.0`: returns `0.0`.
   - Returns `max(-1.0, min(1.0, dot / (norm_a * norm_b)))`.
6. **`compute_maxsim_novelty(baseline_vectors: Sequence[Sequence[float]], current_vectors: Sequence[Sequence[float]], similarity_threshold: float = 0.88) -> tuple[int, float, float]`**:
   - Validates `0.0 < similarity_threshold <= 1.0`, finite, and non-`bool` (raises `DomainValidationError` otherwise).
   - If `not current_vectors`: returns `(0, 0.0, 1.0)`.
   - If `not baseline_vectors`: returns `(len(current_vectors), 1.0, 0.0)`.
   - For each candidate vector $e_p$ in `current_vectors`:
     - Computes $\text{max\_sim}_p = \max_{e_q \in \text{baseline\_vectors}} \cos(e_p, e_q)$.
     - Computes $\text{novelty}_p = \min(1.0, \max(0.0, 1.0 - \text{max\_sim}_p))$.
     - Counts unit $p$ as novel iff $\text{max\_sim}_p < \text{similarity\_threshold}$.
   - Returns `(novel_count, max_novelty, mean_max_similarity)`, where `max_novelty = max(novelties)` and `mean_max_similarity = sum(max_sims) / len(current_vectors)`.
7. **`evaluate_lexical_convergence(baseline_text: str, current_text: str, thresholds: SaturationThresholds | None = None, pass_index: int = 2) -> SaturationVerdict | None`**:
   - Resolves `resolved_thresholds = thresholds or SaturationThresholds()`.
   - Computes `lexical_jaccard = compute_ngram_jaccard(baseline_text, current_text)` and `word_delta_ratio = compute_word_delta_ratio(baseline_text, current_text)`.
   - Computes `total_paragraphs = len(segment_semantic_units(current_text))`.
   - **Sentinel Check First:** If `is_explicit_stop_sentinel(current_text, pass_index)` is `True`:
     - Returns `SaturationVerdict(is_saturated=True, reason=SaturationReason.EXPLICIT_SENTINEL, lexical_jaccard=lexical_jaccard, word_delta_ratio=word_delta_ratio, max_novelty=0.0, novel_paragraphs=0, total_paragraphs=total_paragraphs, preserve_baseline=True, provider="sentinel")`.
   - **Lexical Identity Check:** If `lexical_jaccard >= resolved_thresholds.lexical_identity_threshold` AND `word_delta_ratio <= resolved_thresholds.max_lexical_word_delta`:
     - Returns `SaturationVerdict(is_saturated=True, reason=SaturationReason.LEXICAL_IDENTITY, lexical_jaccard=lexical_jaccard, word_delta_ratio=word_delta_ratio, max_novelty=0.0, novel_paragraphs=0, total_paragraphs=total_paragraphs, preserve_baseline=False, provider="lexical")`.
   - Otherwise returns `None` (caller proceeds to Layer 2 semantic evaluation).
8. **`evaluate_semantic_convergence(baseline_vectors: Sequence[Sequence[float]], current_vectors: Sequence[Sequence[float]], thresholds: SaturationThresholds | None = None, *, lexical_jaccard: float = 0.0, word_delta_ratio: float = 0.0, provider: str = "semantic") -> SaturationVerdict`**:
   - Resolves `resolved_thresholds = thresholds or SaturationThresholds()`.
   - Calls `compute_maxsim_novelty(baseline_vectors, current_vectors, resolved_thresholds.semantic_similarity_threshold)` yielding `(novel_paragraphs, max_novelty, _mean_max_similarity)`.
   - Sets `total_paragraphs = len(current_vectors)`.
   - If `novel_paragraphs <= resolved_thresholds.max_novel_paragraphs_for_saturation`:
     - Returns `SaturationVerdict(is_saturated=True, reason=SaturationReason.SEMANTIC_PLATEAU, lexical_jaccard=lexical_jaccard, word_delta_ratio=word_delta_ratio, max_novelty=max_novelty, novel_paragraphs=novel_paragraphs, total_paragraphs=total_paragraphs, preserve_baseline=False, provider=provider)`.
   - Else:
     - Returns `SaturationVerdict(is_saturated=False, reason=SaturationReason.NOVEL_CONTENT, lexical_jaccard=lexical_jaccard, word_delta_ratio=word_delta_ratio, max_novelty=max_novelty, novel_paragraphs=novel_paragraphs, total_paragraphs=total_paragraphs, preserve_baseline=False, provider=provider)`.

---

### 2.4 Domain Infrastructure Exception (`src/cresmo/domain/exceptions.py`)

```python
class EmbeddingInfrastructureError(CresmoInfrastructureError):
    """Raised when an external or local text embedding call fails or returns invalid vectors."""
```

---

## 3. Application Layer Contracts

### 3.1 `TextEmbeddingPort` (`src/cresmo/application/ports/embedding.py`)
Exported via `cresmo.application.ports.__init__`.

```python
class TextEmbeddingPort(ABC):
    """Abstract port generating dense or sparse vector embeddings for semantic unit sequences."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Canonical identifier of the active embedding backend (e.g. 'gemini', 'ollama', 'tfidf')."""
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Return one embedding vector per input string preserving order."""
        raise NotImplementedError
```

### 3.2 `HybridSaturationEvaluator` (`src/cresmo/application/services/hybrid_saturation.py`)

```python
class HybridSaturationEvaluator:
    def __init__(
        self,
        embedding_port: TextEmbeddingPort | None = None,
        thresholds: SaturationThresholds | None = None,
        mode: ConvergenceMode = ConvergenceMode.HYBRID_SEMANTIC,
    ) -> None: ...

    def evaluate(
        self,
        baseline_text: str,
        current_text: str,
        pass_index: int = 1,
    ) -> SaturationVerdict: ...

    def __call__(
        self,
        baseline_text: str,
        current_text: str,
        pass_index: int = 1,
    ) -> SaturationVerdict: ...
```

#### Orchestration Flow & Degradation Invariants
1. **Disabled Mode (`mode == ConvergenceMode.NONE`):**
   - Returns `never_saturate(baseline_text, current_text, pass_index)` (`SaturationVerdict(is_saturated=False, reason=SaturationReason.DISABLED, lexical_jaccard=0.0, word_delta_ratio=0.0, max_novelty=1.0, novel_paragraphs=0, total_paragraphs=0, preserve_baseline=False, provider="disabled")`) without calling `embed_batch`.
2. **Layer 1 Short-Circuit:**
   - Calls `evaluate_lexical_convergence(baseline_text, current_text, self.thresholds, pass_index=pass_index)`.
   - If a non-`None` verdict (`EXPLICIT_SENTINEL` or `LEXICAL_IDENTITY`) is returned, returns it immediately. **`self.embedding_port.embed_batch` MUST NOT be called.**
3. **Segmentation & Pre-Embedding Metrics:**
   - Computes `lexical_jaccard` and `word_delta_ratio`.
   - Segments `baseline_units = segment_semantic_units(baseline_text)` and `current_units = segment_semantic_units(current_text)`.
   - If `not current_units`: returns `SaturationVerdict(is_saturated=True, reason=SaturationReason.SEMANTIC_PLATEAU, lexical_jaccard=lexical_jaccard, word_delta_ratio=word_delta_ratio, max_novelty=0.0, novel_paragraphs=0, total_paragraphs=0, preserve_baseline=False, provider="lexical")` without invoking `embed_batch`.
   - If `not baseline_units` (and `current_units` is non-empty): returns `SaturationVerdict(is_saturated=False, reason=SaturationReason.NOVEL_CONTENT, lexical_jaccard=lexical_jaccard, word_delta_ratio=word_delta_ratio, max_novelty=1.0, novel_paragraphs=len(current_units), total_paragraphs=len(current_units), preserve_baseline=False, provider="lexical")` without wasting an embedding call.
4. **Graceful Degradation (`embedding_port is None`):**
   - Logs structured `WARNING` (or `DEBUG` when intentionally unconfigured) and returns `SaturationVerdict(is_saturated=False, reason=SaturationReason.NOVEL_CONTENT, lexical_jaccard=lexical_jaccard, word_delta_ratio=word_delta_ratio, max_novelty=1.0, novel_paragraphs=len(current_units), total_paragraphs=len(current_units), preserve_baseline=False, provider="degraded")`.
5. **Layer 2 Single-Call Batched Embedding:**
   - Concatenates `combined_units = [*baseline_units, *current_units]` and invokes `self.embedding_port.embed_batch(combined_units)` in **exactly one call**.
   - Validates `len(embeddings) == len(combined_units)` (if mismatched, treats as `EmbeddingInfrastructureError` / degrades gracefully).
   - Splits `baseline_vectors = embeddings[:len(baseline_units)]` and `current_vectors = embeddings[len(baseline_units):]`.
   - Resolves provider string via `getattr(self.embedding_port, "last_provider_name", None) or self.embedding_port.provider_name`.
   - Delegates to `evaluate_semantic_convergence(...)`.
   - **Unhandled Port Failure Guard:** If `embed_batch` raises `EmbeddingInfrastructureError`, logs structured `WARNING` and degrades gracefully to Layer 1 + `NOVEL_CONTENT` (`is_saturated=False`, `preserve_baseline=False`, `provider="degraded"`).

---

## 4. Infrastructure Embedding Adapters (`src/cresmo/infrastructure/adapters/embeddings/`)

All concrete embedding adapters implement `TextEmbeddingPort` behind ACLs and NEVER expose vendor types outside `infrastructure/`.

| Adapter | Module | `provider_name` | Constructor & Contract Boundaries |
| :--- | :--- | :--- | :--- |
| **`GeminiEmbeddingAdapter`** | `gemini_embedding_adapter.py` | `"gemini"` | `__init__(self, api_key=None, model_name=DEFAULT_GEMINI_EMBEDDING_MODEL, dimensions=DEFAULT_GEMINI_EMBEDDING_DIMENSIONS, genai_client=None, credential_pool=None, api_keys=None, timeout_seconds=30.0)`. Uses `google.genai` `embed_content` (default `gemini-embedding-001`, `task_type="SEMANTIC_SIMILARITY"`, `output_dimensionality=768`), reusing `GeminiCredentialPool` (`ADR-041`). Empty input `[] -> []` (zero API calls). Splits inputs into chunks of at most **100 items** (`MAX_BATCH_SIZE = 100`) preserving global input order. Validates vector count parity and non-empty vector lists; wraps SDK/API/network exceptions in `EmbeddingInfrastructureError`. |
| **`OllamaEmbeddingAdapter`** | `ollama_embedding_adapter.py` | `"ollama"` | `__init__(self, base_url="http://localhost:11434", model=DEFAULT_OLLAMA_EMBEDDING_MODEL, timeout_seconds=30.0)`. Sends `POST {base_url.rstrip('/')}/api/embed` with `{"model": model, "input": list(texts)}` (default `nomic-embed-text`) over `httpx` or `urllib.request` with configured timeout. Empty input `[] -> []` (zero HTTP calls). Parses `"embeddings"` list, verifies length `== len(texts)`, and wraps HTTP status errors, timeouts, connection errors, or malformed JSON into `EmbeddingInfrastructureError`. |
| **`TfidfEmbeddingAdapter`** | `tfidf_embedding_adapter.py` | `"tfidf"` | `__init__(self, ngram_range=(1, 2))` (callable as `TfidfEmbeddingAdapter()`). Strictly local Infrastructure adapter wrapping a **lazy import** of `sklearn.feature_extraction.text.TfidfVectorizer` (`ngram_range=(1, 2)`, `sublinear_tf=True`, `norm="l2"`, preserving fast CLI startup per `ADR-053`/`ADR-055`). Empty input `[] -> []`. Fits/transforms input corpus in one call and converts sparse matrix to `list[list[float]]`. When `TfidfVectorizer` raises `ValueError` due to empty vocabulary (e.g., empty/punctuation-only/stopword-only strings), catches `ValueError` and returns uniform zero vectors (`[[0.0] for _ in texts]`) so `cosine_similarity` yields `0.0` cleanly without shape mismatch. |
| **`ResilientEmbeddingAdapter`** | `resilient_embedding_adapter.py` | `self.primary.provider_name` | `__init__(self, primary: TextEmbeddingPort, fallback: TextEmbeddingPort | None = None)` (default fallback `TfidfEmbeddingAdapter()`). Exposes `last_provider_name: str` initialized to `primary.provider_name`. On `embed_batch(texts)`: empty input `[] -> []`. Calls `primary.embed_batch(texts)`; on success sets `last_provider_name = primary.provider_name`. On `EmbeddingInfrastructureError`: logs structured `WARNING` with stage/error context, sets `last_provider_name = f"{fallback.provider_name}_fallback"` (e.g., `"tfidf_fallback"`), and delegates to `fallback.embed_batch(texts)`. |

---

## 5. Multi-Pass Pipeline & Telemetry Integration (`stage_execution.py`)

Extends `generate_stage_candidate` (`src/cresmo/application/pipeline/stage_execution.py`) and `telemetry.py` (`src/cresmo/application/ports/telemetry.py`) in accordance with `ADR-046` and `ADR-065`.

### 5.1 Fixed-Point Baseline & `preserve_baseline` Semantics
1. **Source Text Extraction:** Extracts `source_text` from `source` (`source.content.text` if `Content`, else `getattr(source, "text", None)` or `str(source)`).
2. **Pass-1 Fixed-Point Baseline:**
   - On `pass_index == 1`, `baseline_text = source_text`.
   - On `pass_index >= 2`, `baseline_text = previous_text` (the accepted output of the preceding pass).
   - Thus Pass 1 itself is evaluated for saturation against `source_text` (`baseline_text`), enabling immediate Pass-1 early stopping when the LLM returns a lexically identical or semantically plateaued transform of `source_text` (while `is_explicit_stop_sentinel` still ignores `<NO_NEW_GAPS/>` on Pass 1).
3. **Evaluator Precedence & Rollback (`preserve_baseline`):**
   - When a `HybridSaturationEvaluator` (or stage saturation policy returning `SaturationVerdict`) is active on a multi-pass stage (`max_passes > 1`):
     - Evaluates `verdict = evaluator.evaluate(baseline_text, current_text, pass_index=pass_index)`.
     - Appends `{"pass_index": pass_index, **verdict.to_metadata_dict()}` to `saturation_history: list[dict[str, Any]]`.
     - When `verdict.is_saturated` is `True`:
       - If `verdict.preserve_baseline` is `True` (strictly `EXPLICIT_SENTINEL` `<NO_NEW_GAPS/>`): restores `current_text = baseline_text` so sentinel tokens never overwrite verified prose, whereas `LEXICAL_IDENTITY` and `SEMANTIC_PLATEAU` set `preserve_baseline=False` so `current_text` (such as cleaned formatting or Pass-1 output) is kept.
       - Respects `FinalPassCritiqueInjection` (`ADR-046`): if `critique` is non-empty and `pass_index < max_passes` and not yet `pending_final_critique`, schedules one terminal critique pass (`pending_final_critique = True`); otherwise sets `is_saturated = True` and breaks out of the pass loop.
     - When `verdict.is_saturated` is `False`: updates `previous_text = current_text` and advances to `pass_index + 1`.

### 5.2 Telemetry Span & Metadata Contract
1. **Span Naming (`ADR-065`):**
   - `format_stage_saturation_span_name(stage_name: str, pass_num: int) -> str` in `src/cresmo/application/ports/telemetry.py` returns `f"cresmo.{_normalize_stage_name(stage_name)}.saturation.pass_{_validate_pass_num(pass_num)}"`.
   - During each saturation check in `generate_stage_candidate`, opens a span named `cresmo.{stage_name}.saturation.pass_{N}` (child of active `cresmo.{stage_name}` stage span) and attaches strictly scalar LGPD-compliant attributes (zero raw transcript, draft, or paragraph text):
     - `cresmo.pass_num`: `int` (`pass_index`)
     - `cresmo.saturation.is_saturated`: `bool`
     - `cresmo.saturation.reason`: `str` (`verdict.reason.value`)
     - `cresmo.saturation.lexical_jaccard`: `float`
     - `cresmo.saturation.word_delta_ratio`: `float`
     - `cresmo.saturation.max_novelty`: `float`
     - `cresmo.saturation.novel_paragraphs`: `int`
     - `cresmo.saturation.total_paragraphs`: `int`
     - `cresmo.saturation.preserve_baseline`: `bool`
     - `cresmo.saturation.provider`: `str`
2. **`CandidateText.metadata`:**
   - Multi-pass executions populate `candidate_metadata["saturation_history"] = saturation_history` (alongside `passes_executed` and `is_saturated`), preserving a complete, deterministic per-pass audit trail.

---

## 6. Verification Acceptance Criteria

- `uv run ruff check .` exits `0`
- `uv run ruff format --check .` exits `0`
- `uv run mypy --strict src/` exits `0`
- `uv run pytest tests/ -v` passes with `0` errors across all Domain, Application, Infrastructure, and Integration suites
- `mutmut` mutation gate on `prose_syntax_guard.py`, `convergence.py`, `convergence_evaluator.py`, and `hybrid_saturation.py` achieves `0` surviving mutants
- Zero `src.` import prefixes inside `src/` and zero forbidden infrastructure imports inside `src/cresmo/domain/` and `src/cresmo/application/`
