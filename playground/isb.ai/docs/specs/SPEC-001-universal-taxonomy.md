# SPEC-001: Universal Taxonomy Specifications

**Status:** Proposed  
**Date:** 2026-07-17  
**ADR Reference:** [ADR-001](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/playground/isb.ai/docs/adr/ADR-001-universal-taxonomy.md)

---

## 1. Acceptance Criteria

These criteria verify that the universal taxonomy and orthogonal layering are correctly implemented:

### AC-1: Channel Classification
* **Input**: A channel name string (case-insensitive).
* **Output**: A 2-tuple containing `(domain, category_type)` where:
  * `domain` is one of: `technology`, `ai_data_science`, `politics_law`, `geopolitics_military`, `finance_economics`.
  * `category_type` is one of: `perennial`, `volatile`.
* **Fallback**: Unknown channels must default to `("uncategorized", "volatile")`.

### AC-2: Output Directory Segmentation
* When a note is generated, it must be written to its designated subfolder under `wiki/`:
  * Perennial Reference notes (`R_*.md`): `wiki/concepts/R_*.md`
  * Perennial Action notes (`A_*.md`): `wiki/procedures/A_*.md`
  * Volatile Chronicle notes (`*.md`): `wiki/chronicles/*.md`
  * People profiles: `wiki/people/`
  * Organization profiles: `wiki/organizations/`
  * Map of Content files: `wiki/MOCs/MOC_*.md`

### AC-3: Dynamic Prompt Selection
* The system must format and send the correct system prompt:
  * If the channel category type is `perennial`, it must use the **Perennial System Prompt** instructing the LLM to output `R_` and `A_` files.
  * If the channel category type is `volatile`, it must use the **Chronicle System Prompt** instructing the LLM to output nominal dated files.

---

## 2. Boundary & Edge Cases

* **Empty Transcripts**: If a raw block has no transcript body, it must be skipped without creating empty folders or notes.
* **Special Characters in Filenames**: When standardizing note names (e.g. `R_Docker_Compose`), characters like `/`, `\`, `?`, `:`, `*` must be sanitized to prevent OS filesystem errors.
* **MOC Linking Idempotency**: Linking a note to an existing MOC must not duplicate the link line if the note is already present.

---

## 3. Test Strategy

We classify the verification strategy into three layers:

### Unit Tests (implemented in `sanity_check.py`)
1. **Classification Mapping Verification**: Test that all 23 channels resolve to the correct `(domain, category_type)` pair.
2. **Directory Resolution Verification**: Verify that a given filename/prefix resolves to the correct target subdirectory path.
3. **Filename Sanitization**: Verify that dangerous characters in extracted concept names are correctly cleaned.

### Integration Tests
1. **Mock End-to-End Processing**: Feed a mock LLM output containing files with different prefixes and check that they are saved to the correct directory structures (`wiki/concepts/`, `wiki/procedures/`, `wiki/chronicles/`).
2. **MOC Registration**: Verify that files are correctly added under `wiki/MOCs/` and that new MOCs are initialized automatically.

### LLM Structural Constraints (Evals)
Since Gemini is called via browser automation, we assert strict structural invariants:
* Response must contain the markdown block wrapper ````markdown`.
* Individual files must be bounded by `<<<< FILE: filename >>>>` and `<<<< END FILE >>>>`.
* MOC associations must be bounded by `<<<< MOC_ASSOCIATIONS >>>>` and `<<<< END MOC_ASSOCIATIONS >>>>`.
* Any parsing failure must trigger an automatic retry or log a structured error.
