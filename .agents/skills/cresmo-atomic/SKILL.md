---
name: cresmo-atomic
description: Converts expanded fluid text into a collection of interconnected Atomic Notes formatted for Obsidian Second Brain in XML format. Maps WikiLinks, note typologies, causal matrices, and double-side linking. Use whenever expanded text needs to be broken down into structured, interlinked atomic Markdown notes wrapped in XML tags. Make sure to trigger this skill whenever atomic note generation for Obsidian is requested.
---

# Cresmo Atomic (Atomic Notes Generator & WikiLinks Mapper)

## Overview

The `cresmo-atomic` skill processes expanded narrative Markdown texts (from `cresmo-expander` or existing clean drafts) and extracts a set of autonomous, semantically dense **Atomic Notes** for an Obsidian Second Brain vault.

Each note addresses a single entity, concept, event, or process, using strict YAML metadata, standardized Obsidian WikiLinks (`[[Note Title]]`), declarative triple connections, causal attribution matrices, and bi-directional cross-context linking.

Save output directly to `cresmo/enriched/<channel_name>/<video_id>.xml`.

---

## Fundamental Atomic Principles

1. **Principle of Atomicity**: Each note must cover a single autonomous idea, entity, historical event, or dynamic process, containing all necessary context to be fully understandable on its own.
2. **Semantic Density**: Avoid empty notes. Every note must extract full factual substance and conceptual rigor.
3. **Internal WikiLinks Syntax**: Every mention of another note within the vault must be formatted as `[[Exact Note Title]]` or `[[Exact Note Title|Flexed Surface Text]]`.
4. **Resolution of Orphan Terms**: No note may refer to a non-existent node. If an entity/concept is hyperlinked in any note body, the corresponding atomic note MUST be included in the batch.

---

## Note Typologies & Title Nomenclatures

Every generated note must belong to one of four strict categories:

1. **Entity Notes (`type: entity`)**:
   - Scope: Relevantly named entities (NER) such as figures, institutions, equipment, systems, countries, cities or etc.
   - Title Convention: Official Name (e.g., `[[Federação Russa]]`, `[[Lloyd Austin]]`, `[[Sistema 9K720 Iskander]]`).

2. **Concept Notes (`type: concept`)**:
   - Scope: Theoretical models, doctrines, laws, philosophical constructs, methodologies, and technical concepts.
   - Title Convention: SSOT/Encyclopedic form (e.g., `[[Dissuasão Nuclear]]`, `[[Destruição Mútua Assegurada]]`, `[[Pulso Eletromagnético de Alta Altitude]]`).

3. **Event / Temporal Milestone Notes (`type: event`)**:
   - Scope: Historical events, treaties, agreements, conferences, or tests delimited in time.
   - Title Convention: **Big-Endian date notation** prefix (e.g., `[[1994-12-05 Memorando de Budapeste]]`, `[[2022-Q3 Crise Nuclear de Kherson]]`, `[[2026 Fim do New START]]`).

4. **Process / Causal Synthesis Notes (`type: process`)**:
   - Scope: Operational sequences, cause-and-effect dynamics, systemic flows, and phenomena.
   - Title Convention: Flow or Dynamic Name (e.g., `[[Escada de Escalada Nuclear]]`, `[[Efeito Cascata de Proliferação Regional]]`).

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
[Analytical description of 1 to 3 continuous paragraphs. Consolidates fundamental definition, historical/technical context, and global role. Use parataxis, direct and swift word order, single and self-contained clausesAll domain terms must use [[WikiLink]] syntax.]

## Conexões e Relações Diretas
* [[Nota Origem ou Sujeito]] -> [Verbo de Ação ou Conector de Ligação] -> [[Nota Destino ou Objeto]], em linguagem natural similar ao texto original

## Matriz Causal e Atribuição Epistêmica
* **Causa / Premissa:** [Fator ou fatores condicionais ou eventos que originam ou sustentam esta nota]
* **Efeito / Impacto:** [Desdobramentos e consequências decorrentes desta nota]
* **Atribuição Epistêmica:** [[Entidade Proponente ou Fonte Histórica]]

## Redes de Conexão e Contexto Cruzado
* **Precursores e Ancestralidade:** Contexto encontrado e expansão de contexto em relação à [[Nota Precursora 1]], Contexto em relação à [[Nota Precursora 2]]
* **Eventos Laterais e Paralelos:** Contexto eem relação à [[Nota Lateral ou Paralela 1]], Contexto em relação à [[Nota Lateral ou Paralela 2]]
* **Desdobramentos e Posteridade:** Desdobramentos relacionados à [[Nota Posterior 1]], Desdobramentos relacionados à [[Nota Posterior 2]]

* **Precursores e Ancestralidade (origem genealógica, base epistemológica ou causa histórica primária, marco antecedente necessário):** Explique a relação histórica ou conceitual com a [[Nota Precursora 1]] e a [[Nota Precursora 2]] 
* **Eventos Laterais e Paralelos (fenômeno coetâneo análogo ou mecanismo concorrente, instituição ou processo correlato sem causalidade direta):** Descreva o contexto simultâneo ou conexões horizontais com a [[Nota Lateral 1]] e a [[Nota Lateral 2]]
* **Desdobramentos e Posteridade (derivação teórica subsequente ou impacto de longo curso, ruptura sistêmica ou reação institucional deflagrada):** Aponte os impactos futuros e desdobramentos relacionados à [[Nota Posterior 1]] e a [[Nota Posterior 2]]

```

---

## Bi-Directional Double-Side Linking Execution

1. **Exhaustive Hyperlinking**: Embed `[[WikiLinks]]` across every mention of named entities, treaties, historical dates, theories, and processes in text bodies.
2. **Aliasing Syntax**: Use `[[Target Title|Flexed Form]]` when text syntax requires grammatical flexions, ensuring the base `Target Title` matches the destination note exactly. Add the flexed form to the `aliases:` list in the YAML header.
3. **Declarative Triples**: In `## Conexões e Relações Diretas`, convert extracted triples into declarative statements in natural language similar to the original text (e.g., `* [[Federação Russa]] -> assinou -> [[1994-12-05 Memorando de Budapeste]]`).

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
