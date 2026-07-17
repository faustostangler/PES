# Glossary of Ubiquitous Language (ISB.AI)

This glossary defines the core domain terms and concepts used within the Intelligent Second Brain (ISB.AI) Bounded Contexts.

---

## 🏛️ Taxonomic & Structural Terms

### Perennial Knowledge
* **Definition**: Structured knowledge, principles, and theories with a long temporal half-life. It represents durable intellectual models that do not decay based on specific calendar events.
* **Context**: Used to classify academic domains, programming models, physical equations, history, and philosophical arguments.

### Volatile Chronicles
* **Definition**: Information with high decay rates and strong temporal coupling. It is bound to specific timestamps (dates) and contemporary actors, representing real-time history in the making.
* **Context**: Used to classify current news events, legal rulings, corporate balance sheet filings, and shifting political landscapes.

### Reference Note (`R_`)
* **Definition**: An atomic, invariant conceptual note representing a core idea, law, theory, or definition. Stored in `wiki/concepts/`.
* **Context**: Represents the "what is" of a domain (e.g., `R_Captura_Regulatoria`).

### Action Note (`A_`)
* **Definition**: An atomic, volatile procedural note detailing a step-by-step workflow, terminal commands, configurations, or implementation recipes. Stored in `wiki/procedures/`.
* **Context**: Represents the "how to" of a domain (e.g., `A_Docker_Compose_Setup`).

### Chronicle / Event Note
* **Definition**: An atomic note representing a specific, bounded occurrence in space and time. Requires a calendar date in its metadata. Stored in `wiki/chronicles/` or root `wiki/`.
* **Context**: Represents the "what happened" of a domain (e.g., `Lei_Felca_Pokemon_Go.md`).

### Map of Content (MOC)
* **Definition**: A structural index page that aggregates, organizes, and establishes a semantic hierarchy of related notes (both Perennial and Volatile) within a specific Bounded Context. Stored in `wiki/MOCs/`.
* **Context**: Serves as the primary entry point and navigator for the second brain's knowledge graph.

### Bounded Context
* **Definition**: A conceptual partition of the second-brain graph grouping notes and MOCs that share the same semantic namespace (e.g., `Politics & Law`, `AI & Data Science`).
