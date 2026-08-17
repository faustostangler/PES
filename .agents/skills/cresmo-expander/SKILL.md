---
name: cresmo-expander
description: Performs Socratic audit, fact-checking, gap analysis, and fluid text expansion on raw transcripts. Strips all speech noise, oralities, diagrams, tables, formulas, and bullet lists, producing continuous, highly dense factual prose with Markdown headings and a complementary information section. Use whenever a transcript or text needs to be cleaned, audited, expanded, and converted into continuous fluid Markdown prose before generating atomic notes. Make sure to trigger this skill during Stage 2 of the Cresmo pipeline (saving output to the enriched directory, never to raw) or whenever transcript detranscription and gap expansion are requested.
---

# Cresmo Expander (Detranscriptor & Gap Expander)

## Overview

The `cresmo-expander` skill transforms raw transcripts, lecture notes, audio transcriptions, and draft texts into clean, factually verified, Socratically audited, and fluidly expanded Markdown documents. 

It executes a strict 2-pass auditing process (Socratic Audit across 6 Epistemic Dimensions + Historical-Scientific Genealogy Mapping), purges all speech noise, direct audience interactions, oralities, and visual noise (diagrams, tables, ASCII charts, LaTeX, blockquotes, and bullet lists), and formats the output exclusively as continuous narrative prose.

Input transcripts contain a YouTube YAML frontmatter header (containing `video_title`, `video_id`, `channel_name`, `channel_id`, `url`, `video_date`, `video_description`) originating from the `cresmo/raw/<channel_name>/<video_id>.txt` directory. Set `<transcript_slug>` strictly to the extracted `video_id`.

**Target Location**: Save output directly to `cresmo/enriched/<channel_name>/<video_id>.md` (in the `enriched` directory, NEVER in the `raw` directory).

---

## Operating Protocol & Execution Rules

1. **Absolute Suppression of Orality and Speech Noise**:
   - Expurge timestamps, hesitations, verbal crutches, false starts, filler words, speaker self-references, and direct audience addresses.
   - Adopt strictly third-person singular with a factual, direct, assertive, and senior analyst voice.

2. **Compulsory Fact-Checking and Entity Verification**:
   - Correct phonetic distortions, transcription misspellings, proper names, brands, acronyms, software/hardware titles, historical treaties, and dates to official standard spellings and accurate chronology.

3. **Materiality Criterion & Metaphor Depuration**:
   - Adopt senior analyst partner posture with accessible vocabulary, avoiding both spoken informality and prolix academicism.
   - Preserve the central metaphor or analogy ONLY when fundamental to understanding complex concepts, purifying it of anecdotal or picturesque noise.
   - **Materiality Criterion**: If a secondary anecdotal fact does not alter the core conclusion of the analysis, eliminate it from the main body text.

4. **Complete Elimination of Diagrams and Visual Schemas**:
   - **Diagram & Visual Schema Suppression Directive**: If the source text contains any diagram, flow chart, ASCII chart, table, or schematic, REMOVE IT ENTIRELY.
   - Extract all underlying concepts, operational mechanics, decision trees, and structural logic represented in the visual diagram and express them fully in continuous fluid narrative paragraphs.
   - Absolute ban on markdown tables, bullet points (`*`, `-`), numbered lists, LaTeX math blocks, and blockquotes (`>`).

5. **Causal Matrix & Epistemic Intelligence**:
   - Categorize causal explanations into:
     - **Structural Causes**: Long-term socio-economic, historical, geographic, or cultural conditions establishing baseline vulnerabilities.
     - **Conjunctural Causes**: Medium-term catalysts and accelerating dynamics.
     - **Triggers**: Immediate short-term events triggering the facts.
   - Distinguish First-Order Facts (empirically verifiable data, dates, treaties, statistics confirmed at primary sources) from Interpretative Models (theories, political schools of thought—always explicitly attributed to their theoretical proponent).
   - Treat unverified statements as intentions/hypotheses and perform *Cui bono?* (vector of interest) analysis, identifying test balloons or destabilization strategies (hidden or conspiratorial), and Analysis of Competing Hypotheses (ACH).

---

## Socratic Audit & Gap Analysis Methodology

Execute an internal 2-pass audit on the input text before writing the final expanded text:

### Pass 1: Intra-Text Socratic Audit (6 Epistemic Dimensions)
1. **Conceptual Clarity & Delimitation**: Define fundamental terms, operational boundaries, and eliminate tautologies.
2. **Assumptions & Foundations**: Map unstated premises and required baseline knowledge.
3. **Evidence & Validation**: Verify empirical base; replace vague generalizations with concrete data.
4. **Mechanism & Causality**: Map all intermediate process steps, eliminating causal gaps or missing logic.
5. **Implications & Consequences**: Evaluate side effects, second-order consequences, and logical extensions.
6. **Alternative Perspectives**: Identify competing theories, strategic omissions, and counter-arguments.

### Pass 2: Historical-Scientific & Genealogical Mapping
- **Precursors, Collaborators, & Omitted Technicians**: Map NER, theoretical foundations, uncredited assistants, co-authors, or omitted technical personnel.
- **Bridging Steps**: Identify intermediate steps serving as bridges between facts, triples, concepts, or NER.
- **Rigor against Anachronism & Physical Limits**: Apply strict chronological accuracy for technical terms and delimit theoretical models from physical/hardware implementations.
- **Networks & Convergence Spaces**: Map geographic and personal proximity spaces enabling cross-pollination of ideas.
- **Ancestry & Posterity**: Map direct/indirect roots and future ramifications.
- **Silencing Audit & Survivorship Bias**: Investigate alternative non-dominant historical accounts and documental bias in knowledge consolidation.

---

## Output Structure & Formatting Directives

- **Linear Chronology & Narrative Flow**: Reconstruct text logically and chronologically.
- **Inter-Paragraph Cohesion**: Guarantee fluid transition between paragraphs by mandatory use of formal transition connectives (temporal, causal, opposition, and complementarity).
- **Markdown Headers**:
  - `##` for Eras, Centuries, or Major Macro Phases.
  - `###` for Decades, Years, or Hierarchical Conceptual Blocks.
- **Typography Rules**:
  - Bold (`**...**`): Apply **exclusively** on the first occurrence of named entities, dates, theoretical concepts, and key atomic terms and etc.
  - Italics (`_..._`): Apply strictly for foreign terms, titles of cultural works, software, and hardware names and etc.
- **Continuous Fluid Prose**: Write strictly in continuous paragraphs. No bullet lists, no numbered lists, no tables, no LaTeX, no blockquotes, no ASCII diagrams.

### Complementary Information Section

Append a dedicated section at the end of the text under the exact heading:

```markdown
## Informações Complementares
```

In this footnotes section, provide numbered continuous paragraphs detailing mini-biographies, geographical contexts, treaty details, additional statistical data, and secondary gap expansions that would otherwise impede narrative velocity in the main body.

---

## File Delivery Directive

Write the final output directly to the `enriched` directory:
`cresmo/enriched/<channel_name>/<video_id>.md`

Do not output meta-commentary, conversational preambles, or postscripts.
