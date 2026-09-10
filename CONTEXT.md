# Cresmo Knowledge Synthesis — Context & Ubiquitous Language

The **Cresmo Knowledge Synthesis** context is responsible for transforming raw audiovisual media feeds and transcripts into an interconnected, epistemic second-brain knowledge graph comprised of fluid enriched compendiums, atomic notes, and Maps of Content (MOCs).

## Language

**Raw Transcript**:
The verbatim text of spoken audio extracted from media feeds before editorial or semantic processing, carrying origin metadata (channel, video ID, upload date).
_Avoid_: Audio text, transcription dump, raw dump

**Enriched Compendium**:
The expanded, continuous factual prose document generated from a Raw Transcript through multi-pass Socratic audit, longitudinal Braudelian expansion, and synchronic Jaspers cross-sections, containing a mandatory complementary information section.
_Avoid_: Summary, article, expanded text, draft

**Longitudinal Expansion**:
The multi-secular structural analysis grounded in the Annales School (Fernand Braudel's *longue durée*), dissecting causation across first-order determinants, second-order structures, and third-order conjunctural opportunities.
_Avoid_: Historical context, background notes, chronology

**Synchronic Expansion**:
The horizontal cross-sectional analysis grounded in Karl Jaspers' Axial Time (*Achsenzeit*), evaluating concurrent global network interactions and comparative civilizational analogies.
_Avoid_: Parallel history, contemporary context, side events

**Atomic Entity Inventory**:
An exhaustive, deduplicated discovery manifest of distinct entities, concepts, events, and processes identified across an Enriched Compendium prior to batch note generation.
_Avoid_: Topic list, tags list, entity candidates

**Atomic Note**:
A modular, hermetic semantic unit in the Second Brain vault representing a single concept, entity, event, or process with standardized YAML frontmatter, rigorous definition, bidirectional `[[WikiLinks]]`, a causal matrix, and cross-context relations.
_Avoid_: Wiki page, card, note, memo

**Map of Content (MOC)**:
A high-level navigational and synthesis node that groups and reconciles a thematic cluster of Atomic Notes with bidirectional links, enforcing zero orphaned notes in the vault.
_Avoid_: Table of contents, hub, index page

**Vault Repository**:
The persistence infrastructure boundary that reads, validates, writes, and indexes Atomic Notes and MOCs in the Obsidian Second Brain directory structure.
_Avoid_: File store, markdown folder, wiki disk

**Anti-Corruption Layer (ACL)**:
The architectural translation adapter that shields the clean domain from external pollution, legacy monkey-patching, unvalidated DTOs, and side-effects from ancestral scraping code.
_Avoid_: Helper script, wrapper, bridge

**Eval Rubric**:
A frozen, mathematically quantified assessment matrix (measuring faithfulness, relevance, hallucination, and toxicity) executed via Langfuse to validate non-deterministic LLM pipeline outputs.
_Avoid_: Prompt check, quality test, review rubric

## Example Dialogue

> **Lead Architect**: "How does the ingestion of a new political speech ensure the vault maintains epistemic density without duplicate nodes?"
>
> **Domain Engineer**: "The *Media Ingestion ACL* feeds the *Raw Transcript* into the *Enriched Compendium* pipeline. After *Longitudinal* and *Synchronic Expansions* finalize, we run Phase 1 of synthesis to extract the *Atomic Entity Inventory*. Before generating new *Atomic Notes*, the inventory is reconciled against the *Vault Repository* index to reuse existing canonical titles and prevent node duplication before linking into the target *Map of Content*."
