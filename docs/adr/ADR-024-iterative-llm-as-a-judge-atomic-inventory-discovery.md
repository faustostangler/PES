# ADR-024: Iterative LLM-as-a-Judge and Deterministic Guardrails for Atomic Inventory Discovery

**Status:** ACCEPTED  
**Date:** 2026-09-27  
**Decision Makers:** Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee)  
**Governing Method:** Doctor Stangler Architecture Method (Clean/Hexagonal DDD Modular Monolith)  
**Related ADRs:** [ADR-001](ADR-001-cresmo-modular-monolith-strangling.md), [ADR-007](ADR-007-pipeline-template-method-dry.md), [ADR-013](ADR-013-iterative-llm-as-a-judge-indexing-loops.md), [ADR-021](ADR-021-unified-pipeline-execution-template-method-and-telemetry.md)  
**Glossary Reference:** [`docs/GLOSSARY.md`](../GLOSSARY.md)  

---

## 1. Context & Architectural Drivers

In `DiscoverAtomicInventoryUseCase` ([`src/cresmo/application/use_cases/discover_atomic_inventory.py`](../../src/cresmo/application/use_cases/discover_atomic_inventory.py)), the Cresmo synthesis engine performs holistic candidate entity discovery across an `EnrichedCompendium`. This discovery step acts as the primary ontological gate of the Second Brain knowledge graph: candidate entities discovered here are queued into `SynthesizeAtomicBatchUseCase` for full batch synthesis into autonomous Obsidian notes.

### Current Limitations:
1. **Unchecked Single-Shot Extraction:**
   The inventory discovery currently performs a single-shot generative LLM invocation with `temperature=0.0`. If the extracted JSON array contains hallucinated entities, superficial non-canonical adjectival phrases, malformed typology classifications, or missing Big-Endian temporal notations on historical events, these defects bypass quality gates completely.
2. **Cascading Token Waste and Graph Degradation:**
   Because each discovered entity triggers downstream batch synthesis (costing hundreds to thousands of tokens per batch of 5 entities), admitting malformed or spurious entities into the `AtomicEntityInventory` wastes API quota and pollutes the Obsidian vault with low-density or invalid notes.
3. **Absence of Self-Healing Loop:**
   Unlike the raw indexing stage ([ADR-013](ADR-013-iterative-llm-as-a-judge-indexing-loops.md)), which features an iterative evaluation and rewrite cycle, candidate inventory discovery had no evaluation mechanism and no retry semantics.

---

## 2. Decision

We establish a **Two-Gate Defense** architecture with configurable self-healing loops for atomic entity discovery:

### 2.1 Gate 1: Deterministic Domain Guardrails (Zero Cost / Fail-Fast)
Before invoking any LLM judge, candidate responses must pass an immediate, zero-token, deterministic domain validation:
1. Must parse into a valid JSON array of dictionaries.
2. The list must be non-empty.
3. Every entry must contain a non-empty string `title`.
4. Every entry must contain a recognized `type` corresponding to `NoteType` (`entity`, `concept`, `event`, `process`).
5. For entries where `type == "event"`, the title must strictly begin with Big-Endian temporal notation (e.g. `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`).

If Gate 1 fails, the candidate is rejected immediately without incurring the latency or financial cost of an LLM judge call.

### 2.2 Gate 2: Targeted LLM-as-a-Judge Evaluation (`judge_atomic_inventory`)
When Gate 1 passes, the candidate output is audited by an impartial LLM judge operating at `temperature=0.0`:
1. **Factual Grounding:** Every entity, concept, event, and process must be explicitly mentioned or directly derived from the compendium context without hallucinations.
2. **Ontological Taxonomy:** Entities must be proper actors/institutions; concepts must be theoretical frameworks or domain constructs; events must be dated milestones; processes must be dynamic mechanisms.
3. **Canonical Encyclopedic Form:** Titles must use singular noun phrase dictionary forms free from conversational noise, meta-labels, or loose narrative adjectives.
4. The judge returns strictly a boolean (`true` or `false`), parsed deterministically via `parse_judge_boolean`.

### 2.3 Configurable Retry Loop & Self-Healing
1. The discovery process runs in an evaluation loop:
   ```python
   while not is_valid:
       # transform inventory candidate
       if is_valid_inventory_json_structure(data):
           # transform judge prompt at temperature=0.0
           is_valid = parse_judge_boolean(judge_response)
       else:
           is_valid = False
       if not is_valid:
           if not _can_retry(retries, max_rewrites):
               break
           retries += 1
   ```
2. The retry budget is exposed via `inventory_max_attempts` in `CresmoSettings` (defaulting to 3; `0` enables infinite retry loops).

---

## 3. Langfuse Ingestion Strategy & Telemetry
1. Every LLM invocation carries explicit deterministic telemetry traces:
   - Initial Discovery: `{content_id}_inventory`
   - Retry Discovery: `{content_id}_inventory_retry_{attempt}`
   - Initial Judge: `{content_id}_inventory_judge`
   - Retry Judge: `{content_id}_inventory_judge_retry_{attempt}`
2. Telemetry tags: `["cresmo", "inventory", "judge"]`.
3. Sampling temperatures:
   - Candidate Generation: configured sampling temperature (default: `0.0`).
   - Judge Verification: strictly `0.0`.

---

## 4. Consequences & Impact

### Positive
- **Vault Graph Purity:** Spurious, trivial, or hallucinated notes are stopped at the boundary before batch synthesis.
- **Cost Reduction a Jusante:** Eliminates wasteful synthesis of invalid candidate notes.
- **Fail-Fast Efficiency:** Deterministic Gate 1 prevents unnecessary judge invocations on malformed JSON.
- **Consistent DX:** Aligns inventory discovery with the proven LLM-as-a-judge standard established in [ADR-013](ADR-013-iterative-llm-as-a-judge-indexing-loops.md).

### Negative / Trade-offs
- Adds at least 1 LLM judge call per compendium discovery.
- Potential retry latency if candidate extraction requires correction. Mitigated by bounded default `max_rewrites = 3`.
