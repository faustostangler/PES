---
name: ghost-writer
description: Master orchestrator skill for ghost-writing, text transformation, deep knowledge extraction, and article production. Coordinates the ghost-writer family (ghost-writer-griller, ghost-writer-detranscriptor, ghost-writer-expander, ghost-writer-downgrader, ghost-writer-extractor). Supports full 5-stage automated writing pipelines (Griller -> Detranscriptor -> Expander -> Downgrader -> Extractor), specialized sub-pipelines, or individual routing based on user input. Use whenever the user requests complex text processing, transcript conversion, narrative expansion, text editing/downgrading, or full-cycle article generation.
---

# Ghost Writer Master Orchestrator

## Overview

The `ghost-writer` master skill orchestrates and coordinates the specialized sub-skills in the Ghost Writer ecosystem. It manages the complete lifecycle of text processing—from initial idea grilling and raw transcript detranscription to factual expansion, structural downgrading/de-bloating, and semantic knowledge graph extraction.

All outputs generated across all pipeline stages must be saved directly to Markdown (.md) files. Outputs must consist strictly of structured hierarchical paragraphs (Markdown headers and narrative prose), never using tables, diagrams, lists, or bullets.

---

## Ecosystem Sub-Skills Registry

### ghost-writer-griller
Socratic interactive interview to extract deep intent, stress-test assumptions, and fill conceptual gaps. Reads raw idea or user prompt, outputting clarified concept and semantic graph directly to a Markdown file.
Target Skill File: [`ghost-writer-griller`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/ghost-writer-griller/SKILL.md)

### ghost-writer-detranscriptor
Purges speech noise, oralities, hesitations, and first-person dialogue from raw transcripts; fact-checks names and dates. Reads raw audio transcript or notes, outputting structured Markdown directly to a Markdown file.
Target Skill File: [`ghost-writer-detranscriptor`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/ghost-writer-detranscriptor/SKILL.md)

### ghost-writer-expander
Two-pass Socratic and historical audit to enrich text with real-world statistics, historical context, and persuasive journalistic tone. Reads draft text or article, outputting factually expanded Markdown directly to a Markdown file.
Target Skill File: [`ghost-writer-expander`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/ghost-writer-expander/SKILL.md)

### ghost-writer-downgrader
De-bloats text, removes substrate-independent micro-details, and delegates secondary/biographical details to numbered footnotes. Reads dense or overwritten text, outputting streamlined Markdown with footnotes directly to a Markdown file.
Target Skill File: [`ghost-writer-downgrader`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/ghost-writer-downgrader/SKILL.md)

### ghost-writer-extractor
Extracts semantic knowledge graph constructs (NER, Concepts, Timelines, Triples, Processes, Causal Logic) into natural language sentences. Reads cleaned article or text, outputting standardized semantic graph directly to a Markdown file.
Target Skill File: [`ghost-writer-extractor`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/ghost-writer-extractor/SKILL.md)

### ghost-writer-style
Cross-cutting dependency. Centralized authorial style guide defining the baroque-naturalist prose identity. Not a pipeline stage. Provides style directives for all prose-producing stages.
Target Skill File: [`ghost-writer-style`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/ghost-writer-style/SKILL.md)

---

## Orchestration Pipelines & Execution Modes

`ghost-writer` evaluates the user's intent and executes one of the following orchestration modes:

### Full Pre-configured Pipeline (5-Stage Master Flow)
Sequence execution follows: ghost-writer-griller to ghost-writer-detranscriptor to ghost-writer-expander to ghost-writer-downgrader to ghost-writer-extractor.
Use case is transforming an unrefined concept or raw lecture recording into a fully researched, factual, polished journalistic article with explanatory footnotes and a final semantic knowledge graph.
First, Griller interactively interviews the user to establish core intent, key entities, and background assumptions.
Second, Detranscriptor standardizes speech text, removes oralities, enforces imperso-journalistic tone, and corrects phonetic distortions.
Third, Expander runs internal three-pass Socratic and historical audit, adding confirmed web-verified statistics, dates, and precursor context.
Fourth, Downgrader cleans up text obesity, maintaining narrative spine while delegating secondary digressions into numbered footnotes.
Fifth, Extractor converts the final article into a six-dimension semantic knowledge graph (NER, Concepts, Timelines, Triples, Processes, Argumentative Logic).

### Transcript-to-Article Pipeline
Sequence execution follows: ghost-writer-detranscriptor to ghost-writer-expander to ghost-writer-downgrader.
Use case applies when the user already provides a raw speech transcript or audio text file and wants a finished, expanded article without the interactive grilling phase.

### Concept-to-Graph Pipeline
Sequence execution follows: ghost-writer-griller to ghost-writer-extractor.
Use case applies when the goal is to extract domain knowledge and map semantic graphs directly from user intent without publishing a full journalistic article.

### Direct Sub-Skill Routing
Use case applies when the user explicitly requests a single isolated task, such as de-bloating text via ghost-writer-downgrader or extracting a knowledge graph via ghost-writer-extractor.

---

## Inter-Skill Data Contracts & Anti-Corruption Layer (ACL)

When chaining sub-skills in multi-stage pipelines, `ghost-writer` enforces the following data transfer rules:

### Direct File Reading and Writing
Sub-skills write their processed output directly to designated Markdown (.md) files. Downstream pipeline stages read directly from the Markdown file written by the preceding stage.

### Footnote Preservation
Expander and downgrader populate numbered footnotes at the end of the text payload. `ghost-writer` ensures that footnote indices and text anchors remain intact across pipeline transitions.

### Output Formatting Compliance
All sub-skills MUST output exclusively in structured hierarchical paragraphs (Markdown headings and narrative prose). Tables, diagrams, lists, and bullets are strictly forbidden in all output files.

### Authorial Style Consistency
All prose-producing stages (detranscriptor, expander, downgrader, griller) MUST apply the `ghost-writer-style` reference guide. The style guide defines the author's baroque-naturalist prose identity and overrides any generic journalistic or academic tone directives. Latin coinages in each new text must be original creations—existing terms across the ecosystem are illustrative examples of the pattern only.

---

## File Storage & Workspace Structure

All generated outputs, intermediate pipeline stage files, final polished articles, and extracted semantic knowledge graphs MUST be persisted locally in Markdown (.md) files under individualized folders for each text/article:

Base Path: `playground/ghost-writer/<article_slug>/`
Stage 1 Output File: `01_griller_brief.md`
Stage 2 Output File: `02_detranscribed.md`
Stage 3 Output File: `03_expanded.md`
Stage 4 Output File: `04_final_article.md`
Stage 5 Output File: `05_semantic_graph.md`

### Storage Protocol Rules
Always root article outputs inside `playground/ghost-writer/`. Create a dedicated subfolder using a clean kebab-case name derived from the topic/title (e.g., `playground/ghost-writer/bandido-estacionario/` or `playground/ghost-writer/singularitas/`). Save intermediate and final outputs into their respective Markdown (.md) files at each stage of execution so progress is tracked and auditably stored.

---

## Operational Execution Protocol

First, analyze the user request to determine whether the user needs a full 5-stage pipeline, a specialized sub-pipeline, or a single sub-skill execution.
Second, load the authorial style guide from `ghost-writer-style/references/style-guide.md` and pass its directives as context to all prose-producing pipeline stages.
Third, initialize the workspace by creating `playground/ghost-writer/<article_slug>/` for the target topic.
Fourth, execute Stage 1 by invoking the target initial skill with the user's input and style guide context, saving the result to its corresponding Markdown (.md) file.
Fifth, propagate and persist payloads sequentially by executing remaining pipeline stages, reading from and writing to their respective Markdown (.md) files in `playground/ghost-writer/<article_slug>/` without tables, diagrams, lists, or bullets.
Sixth, present final delivery confirmation in clean Markdown, providing the exact file paths saved in `playground/ghost-writer/<article_slug>/`.
