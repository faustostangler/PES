# ADR-013: Iterative LLM-as-a-Judge Indexing Loops for Principal Concepts and Proportionate Synthesis Paragraphs

**Status:** ACCEPTED  
**Date:** 2026-09-18  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Related ADRs:** [ADR-001](ADR-001-cresmo-modular-monolith-strangling.md), [ADR-011](ADR-011-zero-hardcoded-tunables-and-unified-inference-observability.md)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context & Architectural Drivers

In `IndexRawTranscriptsUseCase` ([`src/cresmo/application/use_cases/index_raw_transcripts.py`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/application/use_cases/index_raw_transcripts.py)), raw audio transcripts are indexed into semantic catalogs (`_canal.md`) and the global tabular registry (`brain.csv`).

During audit and validation, several limitations were identified in the existing implementation:

1. **Artificial Cardinality Limitation on Key Concepts:**
   The prompt catalog (`prompts.json`) and judge prompt enforced a rigid `"2 to 6 concepts"` limit. In dense academic, philosophical, or geopolitical discussions, restricting the extraction to 6 concepts drops vital domain mechanisms, while in short announcements it forces filler concepts. The domain model requires extracting the **principal concepts** regardless of arbitrary cardinality.

2. **Decoupled Synthesis Pipeline (Raw vs. Summary Input):**
   Previously, the synthesis paragraph in Pass 3 was generated directly from the raw transcript excerpt (`transcript_excerpt`), bypassing the organized summary created in Pass 2. Extracting a crisp synthesis paragraph requires a two-step distillation:
   - Step A: Transform raw transcription into an organized, coherent conceptual summary (`title + raw` -> `summary`).
   - Step B: Extract a dense, paratactic synthesis paragraph of **appropriate size** directly from the organized text (`title + summary` -> `synthesis`).

3. **Absence of Judge and Invariant Bounds on Synthesis Paragraph:**
   While summary and concepts had validation heuristics, the final synthesis paragraph had **no LLM-as-a-judge evaluation**, no length boundary checks, and no self-healing loop. Syntheses that exceeded paragraph bounds or hallucinated details bypassed verification entirely.

4. **Rigid Retry Semantics:**
   The self-healing loop was hard-coded to a maximum of 3 rewrites with no capability for unbounded/infinite verification loops (`while not judge_verdict:`) or flexible tuning in high-assurance indexing runs.

---

## 2. Decision

We establish four architectural standards for transcript indexing:

### 2.1 Unconstrained Principal Concepts Extraction
1. The prompts `raw_index_concepts` and `judge_raw_index_concepts` are updated in `prompts.json` to eliminate the `"2 to 6"` restriction.
2. The model must extract the principal concepts that represent the fundamental theoretical constructs and mechanisms discussed in the content.
3. Output format remains strictly comma-separated, free of meta-labels (`Key concepts:`, `Palavras-chave:`) and markdown prefixes.

### 2.2 Two-Stage Distillation for Synthesis Paragraph
1. **Pass 2 (Organized Text / Summary):** The LLM transforms `video_title` + `transcript_excerpt` into a structured conceptual summary.
2. **Pass 3 (Synthesis Paragraph Extraction):** The LLM receives `video_title` + `summary` (organized text) to generate a single paratactic synthesis paragraph of **appropriate size** (between 40 and 85 words, single self-contained paragraph).

### 2.3 LLM-as-a-Judge Evaluation for Synthesis Paragraph
1. A new prompt pair `judge_raw_index_synthesis` is added to `prompts.json` and exposed via `PromptProviderPort`:
   ```python
   def get_judge_raw_index_synthesis_prompt(
       self,
       video_title: str,
       transcript_excerpt: str,
       synthesis: str,
       language: str = "Português do Brasil",
   ) -> tuple[str, str]: ...
   ```
2. The judge evaluates two criteria simultaneously:
   - **Size & Format:** Exactly one continuous paragraph of appropriate length (no bullet points, no headers, approximately 40–85 words).
   - **Fidelity:** Accurately reflects the original transcript without hallucinations or distortions.
3. The judge returns strictly a boolean (`true` or `false`).

### 2.4 Configurable Bounded or Unbounded (Infinite) Verification Loops
1. Both concepts and synthesis extraction are executed within an evaluation loop:
   ```python
   # attempt_limit <= 0 means unbounded/infinite retries
   while not is_valid and (max_attempts <= 0 or attempts < max_attempts):
       ...
   ```
2. The retry parameter `raw_index_max_attempts` is exposed in `CresmoSettings` (defaulting to 3, with 0 enabling infinite retries).

---

## 3. Langfuse Ingestion Strategy & Telemetry
1. Every LLM invocation must carry an explicit `trace_id`:
   - Concepts: `{video_id}_concepts` (retries: `{video_id}_concepts_retry_{attempt}`)
   - Concepts Judge: `{video_id}_concepts_judge`
   - Summary: `{video_id}_summary` (retries: `{video_id}_summary_retry_{attempt}`)
   - Summary Judge: `{video_id}_summary_judge`
   - Synthesis: `{video_id}_synthesis` (retries: `{video_id}_synthesis_retry_{attempt}`)
   - Synthesis Judge: `{video_id}_synthesis_judge`
2. All judge invocations run deterministically at `temperature=0.0`.
3. Generative extraction invocations run at the configured `raw_index_temperature`.

---

## 4. Consequences & Impact

### Positive
- **Conceptual Richness:** Eliminating the arbitrary 2-6 limit preserves complete domain vocabulary for complex topics.
- **Synthesis Quality:** Distilling from organized summary rather than noisy spoken audio yields clean, crystalline paratactic paragraphs.
- **Dual-Gate Verification:** LLM-as-a-judge for both concepts and synthesis ensures zero malformed or hallucinated catalog entries.
- **Operational Flexibility:** Operators can enforce strict bounded retries in CI or infinite perfection loops in local batch indexing.

### Negative / Trade-offs
- Additional LLM calls per transcript (synthesis judge adds 1 call, retries may add more).
- Infinite loops (`max_attempts = 0`) could stall if a model consistently fails formatting. Mitigated by setting a sensible default (`max_attempts = 3`) while allowing operators to explicitly request infinite mode.

---

## 5. Architectural Anti-Patterns Identified & Refactoring Strategy

During architectural review of the use case implementation ([`src/cresmo/application/use_cases/index_raw_transcripts.py`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/application/use_cases/index_raw_transcripts.py)) and infrastructure adapters, 7 anti-patterns were documented and targeted for elimination:

### 5.1 Long Method / God Orchestrator (SRP Violation)
- **Anti-Pattern:** `index_single_transcript` accumulated ~260 lines, handling repository ACL, text slicing, three distinct LLM extraction/retry state machines, error catching, entity instantiation, and dual-output persistence.
- **Architectural Remedy:** Decompose into three dedicated, single-responsibility private helper methods:
  - `_extract_concepts(self, video_id: str, title: str, excerpt: str) -> str`
  - `_extract_summary(self, video_id: str, title: str, excerpt: str) -> str`
  - `_extract_synthesis(self, video_id: str, title: str, excerpt: str, summary: str) -> str`
  `index_single_transcript` is streamlined to a ~40-line pure domain orchestrator.

### 5.2 Dummy Parameter Calls (Premature Format Smell)
- **Anti-Pattern:** Pre-calling prompt formatters before the loop with dummy empty strings (e.g. `concepts=""`, `summary=""`) solely to extract `system_instruction` while discarding the formatted user prompt `_`, followed by a redundant second format call inside the loop.
- **Architectural Remedy:** Acquire both `system_instruction` and `user_prompt` in-situ within the validation block only when the candidate output exists, eliminating premature and redundant template renders.

### 5.3 WET Loop State Machine (Triplication of Loop Control)
- **Anti-Pattern:** The control flow (`while not is_valid:`, `retries == 0` flag, dynamic `trace_id` derivation, heuristic regex guard, judge execution at `temperature=0.0`, and `_can_retry` budget check) was duplicated verbatim across all 3 passes.
- **Architectural Remedy:** Encapsulate each extraction phase in its focused private method while keeping the unified `while not is_valid:` paradigm with clean exit semantics.

### 5.4 Broad Exception Swallowing (Fail-Fast Violation)
- **Anti-Pattern:** A single broad `try ... except Exception:` block wrapping 200+ lines of application logic silently masked programming bugs (`AttributeError`, `TypeError`, `KeyError`) as transient LLM/network warnings.
- **Architectural Remedy:** Narrow the exception scope, log with full stack trace (`logger.exception`), and avoid masking internal programming defects.

### 5.5 Leaky Abstraction / Hardcoded External Platform Schema
- **Anti-Pattern:** Hardcoding `https://youtube.com/watch?v={video_id_str}` inside the application use case coupled the domain to YouTube, generating bogus URLs for local audio, podcasts, or Vimeo.
- **Architectural Remedy:** Honor `transcript.source_url` directly or preserve platform-neutral URL resolution without leaking third-party platform assumptions into the application layer.

### 5.6 Cryptic Telegraphic Naming & Truncated Abbreviations (Anti-Pattern)
- **Anti-Pattern:** Using truncated variable abbreviations and acronym prefixes/suffixes across application use cases and infrastructure adapters:
  - `eff_*` for `effective_*` (e.g., `eff_temperature`, `eff_timeout`).
  - `sys_*` / `usr_*` for `system_*` / `user_*` (e.g., `sys_con`, `usr_con`, `sys_template`).
  - `res_*` for `result_*` / `response_*` / `resource_*` (e.g., `res_long`, `res_wide`, `res_traversable`).
  - `cand` for `candidate` and `resp` for `response`.
  - `m_*` for regex search match objects (e.g., `m_comp`, `m_title`, `m_date`).
  - Hungarian type suffixes (`video_id_str`, `title_str`, `date_val`, `frontmatter_dict`).
  Such telegraphic shorthand violates Ubiquitous Language, impairs cognitive clarity, breaks symmetrical parity with Hexagonal port parameter names (such as `system_instruction` vs `judge_system_instructions`), and harms Developer Experience (DX).
- **Architectural Remedy:** Enforce full, expressive, intent-revealing names without abbreviations across all architectural layers:
  - `effective_temperature`, `effective_timeout` (never `eff_*`).
  - `system_instructions`, `user_prompt`, `system_template` (never `sys_*`, `usr_*`).
  - `longitudinal_expansion`, `synchronic_expansion`, `resource_traversable`, `response` (never `res_*`, `resp`).
  - `candidate` (never `cand`).
  - `complementary_match`, `title_match`, `date_match` (never `m_*`).
  - Clean semantic identifiers (`video_id`, `title`, `sort_date`, `frontmatter`) devoid of Hungarian type tags.

### 5.7 Unwarmed Local Model & Socket Timeout on Cold Start (Ollama / Local LLM Latency)
- **Anti-Pattern (Head-of-Line Blocking / Cold Start Timeout):** Initiating real generative domain workloads directly against a cold local LLM daemon (e.g., Ollama, llama.cpp, vLLM) on application bootstrap. When a model (e.g., Qwen 2.5 7B, ~4.7 GB GGUF) is not resident in memory, the operating system and daemon must page weights from disk into GPU VRAM. This cold-loading latency (typically 30s to 120s depending on bus speed and model size) routinely exceeds standard HTTP read timeouts (e.g., 60s or 120s), resulting in unhandled socket read timeouts (`httpx.ReadTimeout`) and aborted batch jobs on the very first item. Conversely, executing this warmup *synchronously* at the very top of command handlers blocks CPU and network I/O tasks (such as crawling channel playlists, parsing manifests, and reading directory trees), leaving the CPU idle while waiting for VRAM allocation.
- **Architectural Remedy (Early Background Warmup + Lazy Rendezvous Barrier):**
  We establish a two-phase, thread-safe asynchronous synchronization pattern across `LLMTransformationPort` and `OllamaLLMAdapter`:
  1. **Phase 1: Early Non-blocking Dispatch (`warmup()`):**
     Invoked as one of the first statements in CLI handlers (`handle_index_raw`, `handle_run`) immediately after initializing the pipeline or use case. The adapter acquires `_warmup_lock` (RLock), clears `_warmup_event`, and spawns a background daemon thread targeting `_execute_warmup(effective_timeout)`. This immediately initiates the non-generative preloading HTTP POST (`/api/generate` with `prompt=""`, `keep_alive: "1h"`, and `warmup_timeout_seconds: 300.0`) in parallel.
  2. **Phase 2: Concurrency with CPU/Network Workloads:**
     While the background thread negotiates weight allocation into GPU VRAM, the main application thread proceeds unblocked to execute preparatory tasks: parsing manifests, scanning directory trees, and running channel discovery / seed video crawling (such as resolving 204 seed videos).
  3. **Phase 3: Lazy Rendezvous Barrier (`wait_for_warmup()`):**
     Before the first generative inference payload is dispatched inside `transform()`, the adapter enters the rendezvous barrier:
     - If the background thread has already completed, `wait_for_warmup()` returns immediately (0ms latency, zero overhead).
     - If model preloading is still finishing, the thread blocks safely at the `_warmup_event.wait(effective_timeout)` barrier without CPU polling.
     - If warmup was never triggered beforehand, the barrier dispatches it automatically and awaits completion.
     - Any transport or model error encountered by the worker thread (e.g. HTTP 404 model not found) is captured in `_warmup_error` and re-raised at the barrier, preserving fail-fast error visibility.
  4. **Strict Elimination of Backward-Compatibility Shims & Race Conditions:**
     As Cresmo is a clean, evolving architecture, backward-compatibility parameters (such as `wait=True/False` or duplicate method aliases like `trigger_warmup`) were strictly eliminated. The port and adapters enforce a single, unambiguous contract: `warmup() -> None` for non-blocking asynchronous dispatch, and `wait_for_warmup() -> bool` as the rendezvous barrier. State mutations and thread lifecycle transitions are guarded by `threading.RLock` and double-checked locking, completely eliminating race conditions and deadlocks under concurrent execution.



