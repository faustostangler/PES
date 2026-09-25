# ADR-022: Universal System Instruction and User Prompt Segregation across Knowledge Synthesis Use Cases

**Status:** ACCEPTED  
**Date:** 2026-09-25  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith, KISS & Fail-Fast Principles, ADR-First)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  
**Related ADRs:** [`ADR-001`](ADR-001-cresmo-modular-monolith-strangling.md), [`ADR-013`](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [`ADR-017`](ADR-017-langfuse-v4-prompt-management-and-anonymizer-governance.md), [`ADR-020`](ADR-020-sota-kiss-engineering-canon-and-concurrency-topology.md), [`ADR-021`](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md)

---

## 1. Context & Architectural Motivation

In the Cresmo Knowledge Synthesis Engine, `IndexRawTranscriptsUseCase` ([ADR-013](ADR-013-iterative-llm-as-a-judge-indexing-loops.md)) introduced the segregation of prompt templates into explicit `system_instruction` and `user_prompt` pairs (`tuple[str, str]`). This allowed the LLM to cleanly separate persona, language constraints, and evaluation rules from the variable payload (transcripts, summaries, concepts).

However, downstream synthesis use cases:
- `FillGapsFluidProseUseCase` (`get_gap_filler_prompt`)
- `ExpandLongitudinalSynchronicUseCase` (`get_long_expander_prompt`, `get_wide_expander_prompt`)
- `DiscoverAtomicInventoryUseCase` (`get_inventory_prompt`)
- `SynthesizeAtomicBatchUseCase` (`get_batch_notes_prompt`)
- `ReconcileMOCsUseCase` (`get_mocs_prompt`)

continued to use monolithic prompt strings where `{task}`, embedded skill specifications (`{skill_block}`), and input payloads were concatenated into a single string passed as `prompt=...` with `system_instruction=None` to `LLMTransformationPort.transform(...)`.

### Architectural Flaws of Monolithic Prompts:
1. **Cognitive Asymmetry:** Contradicts the SOTA-KISS principle (ADR-020) by having two competing paradigms for prompt consumption across bounded context use cases.
2. **Loss of LLM Context Caching (KV-Cache):** Modern LLM engines (Google GenAI/Gemini, Ollama, Anthropic, OpenAI) offer native prompt caching for static system instructions. When persona, skill markdown, and style guide constraints are conflated with variable user inputs, context caching is invalidated on every pass, incurring severe token and latency penalties.
3. **Weakened Invariant Steering:** Frontier models enforce system directives with higher behavioral priority (*steering weight*) than user content. Placing stylistic bans (e.g. zero em-dashes, no bullet points in continuous prose) in user prompt space increases hallucination and rule violation rates.

---

## 2. Decision

We establish universal segregation between **System Instructions** and **User Prompts** across all knowledge synthesis use cases:

```
+----------------------------------------------------------------------------------------------------+
|                                    PROMPT SEPARATION TOPOLOGY                                      |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [System Instruction]                                                                              |
|    - Agent Persona & Role ({task})                                                                 |
|    - Embedded Skill Specification ({skill_block})                                                  |
|    - cresmo-style-guide Invariants & Output Bans                                                   |
|    ==> Cacheable via KV-Cache / System Channel across passes and batches                           |
|                                                                                                    |
|  [User Prompt]                                                                                     |
|    - Contextual Target Directive (e.g., Pass index, Title, Channel)                                |
|    - Input Payload (raw transcript, compendium draft, inventory targets, note JSON)                |
|    ==> Dynamic per-invocation payload                                                              |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
                                                |
                                                v
               LLMTransformationPort.transform(prompt=user_prompt, system_instruction=sys_inst)
```

### 2.1 Hexagonal Port Contract Update (`PromptProviderPort`)
All synthesis prompt retrieval methods in `PromptProviderPort` ([`src/cresmo/application/ports.py`](../../src/cresmo/application/ports.py)) return `tuple[str, str]`:
```python
def get_gap_filler_prompt(...) -> tuple[str, str]: ...
def get_long_expander_prompt(...) -> tuple[str, str]: ...
def get_wide_expander_prompt(...) -> tuple[str, str]: ...
def get_inventory_prompt(...) -> tuple[str, str]: ...
def get_batch_notes_prompt(...) -> tuple[str, str]: ...
def get_mocs_prompt(...) -> tuple[str, str]: ...
```

### 2.2 Template Catalog Modernization (`prompts.json`)
Every synthesis entry in `prompts.json` declares:
- `"system_instruction"`: Invariant persona, style guide constraints, and `{skill_block}`.
- `"template"`: Dynamic user payload template.

### 2.3 Universal Use Case Invocation
All use cases unpack `system_instruction, user_prompt` and pass both explicitly to `LLMTransformationPort.transform(...)`:
```python
system_instruction, user_prompt = self.prompt_provider.get_gap_filler_prompt(...)
current_text = self.llm_synthesis_port.transform(
    prompt=user_prompt,
    system_instruction=system_instruction,
    temperature=self.temperature,
    trace_id=...,
    session_id=...,
    user_id=...,
)
```

---

## 3. Consequences & Impact

### Positive
1. **Architectural Cohesion:** 100% of LLM use cases follow the identical `(system_instruction, user_prompt)` paradigm.
2. **Context Caching Acceleration:** Enables instant reuse of heavy skill blocks in Ollama/Gemini via KV cache.
3. **Format Enforcement:** Stronger adherence to stylistic bans (no em-dashes, no bullet points, strict H1 title) through dedicated system prompt channel.
4. **Langfuse Trace Purity:** Langfuse prompts and generations map system and user messages to their respective chat roles cleanly.

### Negative / Trade-offs
- Requires updating existing mock assertions in unit tests to expect tuples instead of single strings.
