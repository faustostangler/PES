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
