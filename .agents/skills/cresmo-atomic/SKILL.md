---
name: cresmo-atomic
description: Converts expanded fluid text into a collection of interconnected Atomic Notes formatted for Obsidian Second Brain in XML format. Maps WikiLinks, note typologies, causal matrices, and double-side linking. Use whenever expanded text needs to be broken down into structured, interlinked atomic Markdown notes wrapped in XML tags. Make sure to trigger this skill whenever atomic note generation for Obsidian is requested.
---

# Cresmo Atomic (Atomic Notes Generator & WikiLinks Mapper)

## Overview

The `cresmo-atomic` skill processes expanded narrative Markdown texts (from `cresmo-expander` or existing clean drafts) and extracts a **complete set** of autonomous, semantically dense **Atomic Notes** for an Obsidian Second Brain vault.

All narrative prose written within the atomic notes must adhere strictly to the [`cresmo-style-guide`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/cresmo-style-guide/SKILL.md), structuring explanations across two or three implicit levels of technical detail and specific vocabulary (precision words for specialists, paired with metaphorical explanations for non-specialists), with high conceptual density, low verbosity, second-order mechanisms, affirmative syntax, zero em-dashes (`—`), and zero binary antitheses.

Each note addresses a single entity, concept, event, or process, using strict YAML metadata, standardized Obsidian WikiLinks (`[[Note Title]]`), declarative triple connections, causal attribution matrices, and bi-directional cross-context linking.

Save output directly to `cresmo/enriched/<channel_name>/<video_id>.xml`.

---

## Fundamental Atomic Principles

1. **Principle of Atomicity**: Each note must cover a single autonomous idea, entity, historical event, or dynamic process, containing all necessary context to be fully understandable on its own.
2. **Semantic Density & Style Compliance**: Avoid empty notes. Every note must extract full factual substance and conceptual rigor, complying with the [`cresmo-style-guide`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/cresmo-style-guide/SKILL.md): structure the explanation across two or three implicit levels of technical detail, combining domain precision words for specialists with structuring metaphorical explanations for non-specialists, high conceptual density, low verbosity, second-order mechanisms, zero em-dashes (`—`), and zero binary antitheses.
3. **Internal WikiLinks Syntax**: Every mention of another note within the vault must be formatted as `[[Exact Note Title]]` or `[[Exact Note Title|Flexed Surface Text]]`.
4. **Resolution of Orphan Terms**: No note may reference a non-existent node. If any `[[WikiLink]]` target appears in any note body, the corresponding atomic note MUST either (a) already exist in the vault as registered in `cresmo/wiki/_index.json`, or (b) be included as a new note in the current XML batch. Consult `_index.json` before generating a new note to avoid duplicating existing vault entries and to resolve aliases.
5. **Principle of Exhaustive Extraction**: The entire source text — every paragraph, every sentence, every supplementary section — must be systematically scanned for extractable entities. No noteworthy item may be silently omitted. The output batch must capture the full semantic content of the source text as a self-contained knowledge graph.

---

## Exhaustive Entity Extraction Protocol

The extraction process follows a **three-pass sequential sweep** over the complete source text. No paragraph may be skipped. No section may be deprioritized.

### Pass 1 — Paragraph-by-Paragraph Sequential Scan

Process the source text from beginning to end, paragraph by paragraph. For each paragraph:

1. **Identify every proper noun**: persons, places, institutions, documents, works, organizations, infrastructure, geographic features, hydrographic features, political entities, languages, and any other named thing.
2. **Identify every dated event**: any event with an explicit temporal marker (year, month, full date, approximate period) generates an `event` note with Big-Endian date prefix.
3. **Identify every domain-specific concept**: specialized terminology, processes, social phenomena, doctrines, legal constructs, technical methods, scientific principles, philosophical frameworks — anything that requires domain knowledge to understand.
4. **Identify every dynamic process**: cause-and-effect chains, systemic flows, operational sequences, historical movements, and recurring phenomena that transcend a single event or entity.
5. **Harvest supplementary context**: When the source text contains a supplementary or complementary information section (numbered footnotes, biographical notes, contextual annotations), extract the factual content from these entries and integrate it into the relevant atomic notes. Each supplementary entry enriches the corresponding note's "Definição e Análise Contextual" section with additional biographical, historical, or technical depth. Entities appearing exclusively in supplementary entries still require their own atomic notes.

### Pass 2 — Alias Resolution & Vault Disambiguation

Before generating the note batch:

1. **Consult `cresmo/wiki/_index.json`** to verify whether any extracted entity already exists in the vault under an existing title or alias.
2. **Parenthetical annotations are alias signals**: When the source text uses constructions like `"Modern Name (Ancient Name)"`, `"Full Name (Acronym)"`, or `"Local Term (Translation)"`, the primary term becomes the note title and the parenthetical term becomes an alias in the `aliases:` YAML field. If the entity already exists in `_index.json` under either name, use the existing canonical title and add the new variant as an alias.
3. **Grammatical flexions are alias signals**: When the source text refers to the same entity in different grammatical forms (plural, genitive, adjectival), use the `[[Canonical Title|Flexed Form]]` WikiLink syntax and register the flexed form in the `aliases:` list.
4. **Do not generate duplicate notes**: If `_index.json` already contains an entry (by title or alias match) for an extracted entity, reference it via `[[Existing Title]]` but do NOT regenerate it in the current batch.

### Pass 3 — Orphan Closure Audit

After generating all notes from Passes 1 and 2:

1. **Compile a master set** of every `[[WikiLink]]` target referenced across all note bodies in the current batch.
2. **For each target**, verify that it resolves to either (a) an existing note registered in `_index.json`, or (b) a note present in the current XML batch.
3. **For every unresolved target**, generate an atomic note using whatever context is available from the source text. If information is minimal, apply the Minimal Note Protocol (see below).
4. **Repeat** the audit until no dangling links remain within the batch (excluding links that resolve to `_index.json` entries).

---

## Extraction Depth & Granularity Rules

These rules are **field-agnostic** — they apply identically whether the source text covers history, technology, science, philosophy, law, economics, literature, or any other domain.

1. **Rule of Autonomous Meaning**: If removing a term from the sentence would leave an informational gap that a reader cannot fill from general knowledge alone, that term deserves its own note. Yeah, that may need a lot of notes. 
2. **Proper Nouns Always Generate Notes**: Every proper noun — whether a person, place, institution, document, work, event, or named thing — generates a note. No exceptions.
3. **Dated Events Always Generate Notes**: Any event anchored to an explicit temporal marker generates an `event` note with a Big-Endian date prefix in the title.
4. **Domain-Specific Terms Generate Notes**: Specialized vocabulary requiring domain expertise to understand generates a `concept` or `entity` note, regardless of how briefly it appears in the source text.
5. **Parenthetical Annotations Are Extraction Signals**: When the source text contains parenthetical clarifications, both the primary term and the parenthetical variant produce a single note with the variant as an alias.
6. **Supplementary Sections Enrich Notes**: Content from complementary information sections, numbered footnotes, and contextual annotations feeds into the corresponding note's body. Entities that appear exclusively in these sections still generate their own atomic notes.
7. **Implicit Actors Generate Notes**: When a source text describes an action attributed to a named group, class, or unnamed individual whose identity can be inferred from context, that actor generates a note if it carries autonomous semantic value.

---

## Note Typologies & Title Nomenclatures

Every generated note must belong to one of four strict categories:

1. **Entity Notes (`type: entity`)**:
   - Scope: Named entities such as persons, institutions, organizations, geographic features, infrastructure, political units, documents, legal codes, works, languages, social classes, or any other distinctly named thing.
   - Title Convention: Official or canonical name in the vault's language.

2. **Concept Notes (`type: concept`)**:
   - Scope: Theoretical models, doctrines, laws, philosophical constructs, methodologies, technical concepts, scientific principles, and specialized domain terminology.
   - Title Convention: SSOT/Encyclopedic canonical form.

3. **Event / Temporal Milestone Notes (`type: event`)**:
   - Scope: Events, treaties, agreements, battles, foundations, investitures, births, deaths, or any occurrence delimited in time.
   - Title Convention: **Big-Endian date notation** prefix followed by event name (e.g., `[[YYYY-MM-DD Event Name]]`, `[[YYYY Event Name]]`, `[[YYYY-QN Event Name]]`).

4. **Process / Causal Synthesis Notes (`type: process`)**:
   - Scope: Operational sequences, cause-and-effect dynamics, systemic flows, recurring phenomena, and historical movements.
   - Title Convention: Flow or dynamic name describing the process.

## Metadata Extraction & Tag Propagation

Input transcripts contain a YouTube YAML frontmatter header:
- `video_id`: (e.g. `eYFTRQHaPgw`)
- `channel_name`: (e.g. `"HENI OZI CUKIER"`)

Every generated atomic note MUST extract `channel_name` and `video_id` from the source transcript header and populate the `tags:` list in the YAML frontmatter with `#source/[channel_name_slug]/[video_id]` along with category, domain, and cluster tags.

---

## Mandatory Note Structure Template

Every note MUST be formatted using this exact Markdown template:

```markdown
---
type: entity | concept | event | process
content:
  - [primary_tag]
  - [primary_tag]/[theme_subtag] (se e quantas houverem)
domain: [domain]
cluster: [cluster]
source: [channel_name_slug]/[video_id]
aliases: ["Alternative Name 1", "Acronym or Short Name"]
---
# [Exact Note Title]

## Definição e Análise Contextual
[Analytical description of 1 to 3 continuous paragraphs conforming to the cresmo-style-guide. Structures the explanation across at least two or three implicit levels of technical detail and specific vocabulary (precision words for specialists who understand the details, and metaphorical explanations for non-specialists), with high conceptual density and low verbosity. Consolidates fundamental definition, second-order mechanisms, historical/technical context, and systemic role. When supplementary information is available for this entity (from footnotes, complementary sections, or contextual annotations in the source text), integrate that content here to enrich the note's factual depth. Strictly zero em-dashes and zero binary antitheses. All domain terms must use [[WikiLink]] syntax.]

## Conexões e Relações Diretas
* [[Nota Origem ou Sujeito]] -> [Verbo de Ação ou Conector de Ligação] -> [[Nota Destino ou Objeto]], em linguagem natural similar ao texto original

## Matriz Causal e Atribuição Epistêmica
* **Causa / Premissa:** [Fator ou fatores condicionais ou eventos que originam ou sustentam esta nota]
* **Efeito / Impacto:** [Desdobramentos e consequências decorrentes desta nota]
* **Atribuição Epistêmica:** [[Entidade Proponente ou Fonte Histórica]]

## Redes de Conexão e Contexto Cruzado

* **Precursores e Ancestralidade (origem genealógica, base epistemológica ou causa histórica primária, marco antecedente necessário):** Explique a relação histórica ou conceitual com a [[Nota Precursora 1]] e a [[Nota Precursora 2]] 
* **Eventos Laterais e Paralelos (fenômeno coetâneo análogo ou mecanismo concorrente, instituição ou processo correlato sem causalidade direta):** Descreva o contexto simultâneo ou conexões horizontais com a [[Nota Lateral 1]] e a [[Nota Lateral 2]]
* **Desdobramentos e Posteridade (derivação teórica subsequente ou impacto de longo curso, ruptura sistêmica ou reação institucional deflagrada):** Aponte os impactos futuros e desdobramentos relacionados à [[Nota Posterior 1]] e a [[Nota Posterior 2]]

```

---

## Minimal Note Protocol for Sparse Entities

For entities mentioned only in passing or with minimal available context in the source text, apply a slim but complete note format:

1. **Full YAML frontmatter**: All fields (`type`, `content`, `domain`, `cluster`, `source`, `aliases`) must be populated.
2. **"Definição e Análise Contextual"**: A short text providing whatever context the source text supplies, supplemented by the note's relational position in the knowledge graph. This section will have notes to other notes. 
3. **"Conexões e Relações Diretas"**: At minimum one declarative triple linking back to the note(s) that reference this entity. This section will have notes to other notes.
4. **"Matriz Causal e Atribuição Epistêmica"**: May be abbreviated to a single cause-effect pair, but must not be omitted entirely. This section will have notes to other notes.
5. **"Redes de Conexão e Contexto Cruzado"**: At minimum one entry under "Precursores e Ancestralidade" or "Eventos Laterais e Paralelos", linking to contextually adjacent notes. This section will have notes to other notes.

Sparse notes are first-class citizens of the vault. They serve as anchoring nodes that prevent orphan links and provide attachment points for future enrichment from other sources.

---

## Bi-Directional Double-Side Linking Execution

1. **Exhaustive Hyperlinking**: Embed `[[WikiLinks]]` across every mention of named entities, treaties, historical dates, theories, and processes in text bodies.
2. **Aliasing Syntax**: Use `[[Target Title|Flexed Form]]` when text syntax requires grammatical flexions, ensuring the base `Target Title` matches the destination note exactly. Add the flexed form to the `aliases:` list in the YAML header.
3. **Declarative Triples**: In `## Conexões e Relações Diretas`, convert extracted triples into declarative statements in natural language similar to the original text.
4. **Bi-Directionality Verification**: For every note A that contains `[[B]]` in its body, note B MUST contain `[[A]]` in at least one of its sections (Conexões, Matriz Causal, or Redes de Conexão). Perform this verification for all note pairs in the batch before emitting the final XML. Notes referencing entries that already exist in `_index.json` are exempt from this check within the current batch, as the `cresmo-moc-manager` handles cross-text back-linking.

---

## Completeness Self-Verification Checklist

Before emitting the final XML output, verify that all conditions are met:

1. ✅ Every paragraph and every section of the source text (including supplementary/complementary sections) has been scanned for extractable entities.
2. ✅ Every proper noun in the source text has a corresponding note in the batch or a matching entry in `_index.json`.
3. ✅ Every explicitly dated event has a corresponding `event` note with Big-Endian title prefix.
4. ✅ Every domain-specific term or specialized concept has a corresponding note.
5. ✅ Every `[[WikiLink]]` in any note body resolves to either an existing `_index.json` entry or a note in the current batch.
6. ✅ Every note pair within the batch satisfies bi-directional linking (A links B implies B links A).
7. ✅ All parenthetical annotations have been processed as aliases with `_index.json` disambiguation.
8. ✅ The Minimal Note Protocol has been applied to all sparse entities — no entity was silently dropped for lack of context.

---

## Automated XML Output Specification

The complete batch of generated atomic notes MUST be presented inside XML container tags, with correct indented tabulation:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<notas>
   <nota>
      Complete Markdown content of first atomic note
   </nota>
   <nota>
      Complete Markdown content of second atomic note
   </nota>
</notas>
```

Save output directly to `cresmo/enriched/<channel_name>/<video_id>.xml`.
Do not output any introductory greetings, conversational commentary, or postscripts outside the `<xml>...</xml>` block.
