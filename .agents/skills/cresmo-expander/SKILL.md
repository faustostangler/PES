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
   - Treat unverified statements as intentions/hypotheses and always perform *Cui bono?* (vector of interest) analysis, identifying test balloons or destabilization strategies (hidden or conspiratorial), and Analysis of Competing Hypotheses (ACH) for each intentions/hypotheses.

---

## Socratic Audit & Gap Analysis Methodology

Execute an internal 2-pass audit on the input text before writing the final expanded text:

### Pass 1A: Intra-Text Socratic Audit (6 Epistemic Dimensions)
1. Conceptual Clarity and Delimitation (What is it?): What is the precise definition of this text's foundational terms? What are the boundaries of this concept? Where does it cease to be applicable? Is there tautology?
2. Assumptions and Foundations (What is being assumed?): What premises does the author assume to be true without presenting evidence in the text? What must the reader know beforehand for this text to make sense?
3. Evidence and Validation (How do we know this?): What is the empirical, logical, or factual basis underpinning each main assertion? Where does the text substitute concrete data with generalizations or adjectives?
4. Mechanism and Causality (How does it work?): Does the text explain the intermediate steps of each process mentioned? Is there any state transition or event that occurs without a physical, logical, or historical explanation? Is there a vacuum of meaning and an absence of intermediate mechanisms, or a causal tautology?
5. Implications and Consequences (So what?): What are the logical consequences of the assertions made? Does the text address the side effects or the limitations of the presented solution?
6. Alternative Perspectives (What was ignored?): What are the competing views, counterarguments, or exceptions to this thesis? What questions would a skeptical critic raise about this text that remain unanswered? What should have been written, but was omitted?

### Pass 1B: Cognitive Domain Mapping
Map the knowledge matrix across three levels: conceptual (what it is), procedural (how it works), and causal (why it works).

### Pass 2: Historical-Scientific & Genealogical Mapping
1. Attribution and Intellectual Genealogy Audit: Precursor Tracking, Identification of Omitted Collaborators, Ownership and Fame Investigation.
2. Abstract to Concrete Theory Transition Mapping: Transition Links, Theoretical-Practical Integration, Mechanisms of Influence.
3. Classification Rigor and Technical Limitations: Separation between Model and Implementation, Countering Anachronism, Original Conceptual Boundaries.
4. Reconstruction of Networks and Convergence Contexts: Personal Network Mapping, Spaces of Interdisciplinary Convergence, Geography of Knowledge.
5. Epistemic Ancestry and Posterity Mapping: Epistemic Roots and Ancestry, Ramifications and Posterity, Rupture versus Continuity Tension.
6. Silencing, Survivorship Bias, and Record Asymmetry Audit: Documentary Bias, Appropriation and Invisible Labor, Geopolitics of Knowledge.


Mandatory for Pass 1 & 2: Iteratively review and expand the veracity and completeness of the identified gaps through 5 cycles.


## Conducting Textual Conceptual Expansion
Use deep causality to replace abstractions and bridge gaps across the main body and supplementary notes.
Anchor the narrative in realistic empirical elements: exact figures, precise statistics, confirmed dates, proper names, and verified real-world cases researched and validated on the web.
Prevent combinatorial explosion: preserve the narrative spine of the text.
Transfer secondary or tangential expansions to informative footnotes at the end of the text.


## Output Structure & Formatting Directives

- **Linear Chronology & Narrative Flow**: Reconstruct text logically and chronologically.
- **Inter-Paragraph Cohesion**: Guarantee fluid transition between paragraphs by mandatory use of formal transition connectives (temporal, causal, opposition, and complementarity).
- **Markdown Headers**:
  - `##` for Eras, Centuries, or Major Macro Phases.
  - `###` for Decades, Years, or Hierarchical Conceptual Blocks.
- **Typography Rules**:
  - Bold (`**...**`): Apply **exclusively** on the first occurrence of named entities, dates, theoretical concepts, and key atomic terms and etc.
  - Italics (`_..._`): Apply strictly for foreign terms, titles of cultural works, software, and hardware names and etc.
- **Continuous Fluid Prose**: Write strictly in continuous hierarchical prose paragraphs. No bullet lists, no numbered lists, no tables, no LaTeX, no blockquotes, no ASCII diagrams.

## Style and Tone (read more about style in .agents/skills/ghost-writer-style/SKILL.md and related files)
Write in continuous hierarchical prose paragraphs with parataxis, direct and swift word order, predominantly short, self-contained clauses, mainly through asyndetic juxtaposition of ideas, producing a rapid and incisive rhythm. Maintain syntactic clarity and an exoteric, crystalline style, with maximum conceptual density and precision. Use fully technical, precise, and erudite language, including rare vocabulary where semantically warranted, but make form an invisible medium: vocabulary must serve the argument rather than display sophistication. Avoid prolixity, bombast, ornamental rhetoric, unnecessary abstraction, and pretension. Each sentence should advance, sharpen, or qualify the preceding proposition. Prefer conceptual compression over exposition, and semantic force over verbal ornament. 



## Complementary Information Section
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
