# ADR-001: Universal Taxonomy Design for Second-Brain Ingestion

**Status:** Accepted  
**Date:** 2026-07-17  
**Decision Makers:** Fausto Stangler (Lead Architect), Antigravity (Socio-Technical Implementer)  

---

## Context

The `isb.ai` Intelligent Second Brain system processes raw text transcripts from 23 diverse YouTube channels and structured essays. The current implementation uses a hardcoded binary classification between `"news"` and `"technical"` channels. 

As the volume of ingested material grows and new disciplines (like *Philosophy & History*) are introduced, this binary system is insufficient. We face three primary forces:
1. **Semantic Diversity**: Content spans fields as diverse as Software Architecture, Quantitative Trading, Constitutional Law, and Geopolitical Strategy.
2. **Temporal Decay (Perennial vs. Volatile)**: Technical theories and philosophical arguments (perennial) require different structuring, linking, and curation lifecycles compared to daily news events (volatile).
3. **Graph Fragmentation**: Duplicate entities and unlinked notes degrade the value of the Obsidian Map of Content (MOC) graph.

We need a taxonomy that scales across all semantic fields, manages the perennial vs. volatile dichotomy, and enforces graph integrity.

---

## Decision

We will **adopt Option A (The Orthogonal Layer)** to classify all ingested knowledge into **5 primary semantic domains**, physically segmenting the directories into **Perennial Knowledge** (`concepts/` and `procedures/`) and **Volatile Chronicles** (`chronicles/`), because this maintains strict thematic cohesion (DDD Bounded Contexts) while allowing custom prompt routing, distinct curation rules, and automated bi-directional linking.

---

## Consequences

### Positive
* **Domain Proximity (Cohesion)**: Keeps conceptual definitions (e.g., `R_Captura_Regulatoria`) physically and semantically close to their real-world examples (e.g., `Lei_Felca_Pokemon_Go.md`) within the same MOC (e.g., `MOC_Politica_Nacional`).
* **Deterministic Prompt Routing**: Allows the parser to automatically select LLM prompt structures based on the channel's classification (Perennial feeds generate `R_`/`A_` notes; Volatile feeds generate dated nominal chronicles).
* **Cleaner MOC Rendering**: MOC files can split sections into stable theories and chronological event lists, improving readability.

### Negative
* **Prompt Complexity**: The LLM prompt must strictly enforce the creation of correct file prefixes and folder mappings.
* **Grep/Update Overhead**: Resolving backlinks across subdirectories requires recursive searches in Python (`wiki_dir.rglob("*.md")`).

### Neutral
* All notes are physically organized into domain-specific subdirectories rather than residing entirely in a flat vault root.

---

## Alternatives Considered

### Alternative A: The Binary Vault Split
* **Approach**: Segregate the vault root into `/codex` (stable conceptual notes) and `/ledger` (temporary news/event timelines).
* **Pros**: Simple curation; the ledger can be easily pruned or archived when out of date.
* **Cons**: Breaks theme proximity; a theory is separated from the real-world events that illustrate it, weakening the linking graph.
* **Why Rejected**: The loss of contextual linkage between theory and action violates the core principle of a second brain.

### Alternative B: The Metadata-Driven Flat Structure
* **Approach**: Store all notes in a single flat directory, relying on YAML frontmatter (`type: concept` vs `type: event`) and Obsidian Dataview queries to organize the vault.
* **Pros**: Files don't need to change paths if they transition states.
* **Cons**: The raw folder structure becomes an unmanageable file dump. Severely dependent on Obsidian-specific plugins.
* **Why Rejected**: Standard file-system portability and clean terminal/CLI management are core design requirements.

---

## Compliance

* [x] Hexagonal Architecture layers respected (classification rules reside in Application/Domain layers, not in infrastructure presentation)
* [x] No framework dependencies in Domain layer
* [x] Tests strategy defined (updated categorization rules will be verified in `sanity_check.py`)
* [x] Observability plan included (ingested classification metrics logged per pipeline run)
* [x] LGPD/Security implications assessed (no personal data is exposed through directory structures)

---

## References

* **Glossary**: [docs/GLOSSARY.md](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/playground/isb.ai/docs/GLOSSARY.md)
* **Initial Taxonomy Mapping**: [analysis_results.md](file:///home/stangler/.gemini/antigravity-ide/brain/11996d05-8439-477b-a4e8-8af5b3ea1e39/analysis_results.md)
