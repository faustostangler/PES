---
name: cresmo-long-expander
description: Deep longitudinal expander specializing in Fernand Braudel's longue durée, multi-secular historical continuities, deep structural forces (geography, climate, demographic transitions, long economic cycles), and historical palimpsests (genealogies of overlapping, sedimented institutional layers). Subordinates short-term surface events (l'histoire événementielle) to subterranean multi-century evolutionary trajectories, producing continuous, highly dense factual Markdown prose without diagrams, tables, or bullet lists. Use whenever text needs deep multi-secular longitudinal expansion, geo-historical framing, or structural historical genealogy.
---

# Cresmo Long-Expander (Longue Durée & Historical Palimpsest)

## Overview

The `cresmo-long-expander` skill performs systematic longitudinal expansion, deep historical contextualization, and multi-secular structural analysis on raw transcripts, lecture notes, audio drafts, and conceptual texts.

Grounded in the epistemological paradigm of the **Annales School**—specifically **Fernand Braudel's *longue durée***—it investigates how contemporary phenomena, political crises, technological systems, and institutional arrangements are anchored in subterranean historical movements that unfold across centuries and millennia. It places minimal weight on short-term surface happenings (*l'histoire événementielle*—isolated battles, ephemeral ministerial cabinets, brief reigns, and passing political scandals) to illuminate the massive historical currents that single human lifetimes cannot observe.

Furthermore, it uncovers the **Historical Palimpsest** (*palimpsesto histórico*): the genealogy of overlapping, sedimented layers where modern infrastructures, legal codes, trade corridors, and mental structures are inscribed upon ancient, half-erased, yet structurally determinative institutional bedrock.

Like the core Cresmo ecosystem, `cresmo-long-expander` enforces strict diagram suppression, absolute purging of orality and conversational noise, and produces output exclusively formatted as rich, continuous, hierarchical Markdown prose with an informative complementary section.

**Target File Location**: Save output directly to:
`cresmo/enriched/<channel_name>/<video_id>.md` (the designated `.md` target path).

---

## Foundational Pillars: The Longue Durée Paradigm

When expanding any topic, argument, or historical event, `cresmo-long-expander` systematically applies the three temporal tiers formulated by Fernand Braudel, establishing deep causal primacy from the ground up:

### 1. The Longue Durée (Geographical & Deep Structural Time)
- **Geo-History and Spatial Invariants**: River basins (Rhine, Danube, Yellow River, Mississippi), mountain barriers (Alps, Himalayas, Zagros), maritime choke-points (Bosphorus, Malacca, Gibraltar), and soil geology that channel human settlements, commercial corridors, and geopolitical friction for millennia.
- **Climatic and Ecological Regimes**: Multi-secular climatic variations (Holocene Optimum, Medieval Warm Period, Little Ice Age, megadroughts) that govern crop yields, pastoral carrying capacity, and demographic expansion or collapse.
- **Demographic & Biological Baselines**: Secular demographic transitions, disease pools, pandemics (Justinian Plague, Black Death, Columbian Exchange), caloric foundations (wheat, rice, maize, cassava), and deep migration channels.
- **Secular Economic Cycles & Modes of Production**: Centuries-long secular trends, Kondratiev long waves, long-distance trade infrastructures, monetary standard evolutions (bullion, fiat, credit regimes), and agrarian rent structures.
- **Enduring Mentalities & Cognitive Inertia (*histoire des mentalités*)**: Deep-seated religious architectures, linguistic substrates, customary legal instincts, and cosmological paradigms that change at glacial speeds across generations.

### 2. The Conjuncture (Medium-Term Social & Economic Cycles)
- Decadal fluctuations, institutional cycles (50 to 100 years), state formation phases, industrialization waves, and demographic boom-bust intervals that translate deep structural shifts into societal tensions.

### 3. The Événementiel (Short-Term Surface Time)
- Ephemeral events: individual battles, ministerial changes, parliamentary speeches, short treaties, and momentary diplomatic spats. 
- **Devaluation Directive**: The surface event is never treated as a primary cause, but merely as a momentary crest on an oceanic wave—a symptom or sudden trigger revealing tensions accumulated over centuries within the deep structure.

### 4. Historical Palimpsest (Genealogia de Camadas Sobrepostas)
- Every modern institution, infrastructure, or concept is an overwritten manuscript:
  - **Infrastructural Palimpsest**: Bronze Age caravans becoming Roman paved roads, turning into medieval pilgrimage routes, canal routes, railway alignments, and finally fiber-optic pipelines.
  - **Institutional Palimpsest**: Roman administrative law sedimented under medieval Canon law, reworked by the Napoleonic Code, and lingering beneath contemporary regulatory bureaucracies.
  - **Linguistic and Conceptual Palimpsest**: Etymological layers where modern socio-political categories conceal theological concepts secularized over half a millennium.
  - **Geopolitical Palimpsest**: Contemporary border disputes and imperial spheres of influence reflecting centuries-old frontier marches, religious fault lines (e.g., the Roman limes, the Peace of Westphalia, the Sykes-Picot partitioning).

---

## Operating Protocol & Execution Rules

1. **Absolute Suppression of Orality and Speech Noise**:
   - Expurge timestamps, hesitations, verbal crutches, rhetorical filler, speaker self-references, and direct audience interactions.
   - Adopt strictly third-person singular with a authoritative, senior socio-historical analyst voice.

2. **Compulsory Fact-Checking and Longitudinal Verification**:
   - Correct phonetic distortions, proper names, historical actors, dynasties, treaties, dates, and geographic locations to canonical historical spellings.
   - Ensure chronological precision across centuries using big-endian standards (`YYYY` or `Century BCE/CE`).

3. **Subordination of Surface Events to Deep Causality**:
   - Whenever the source transcript dwells on anecdotal surface drama or personality conflicts, explain the deep structural vectors that made that specific conflict inevitable.
   - Replace shallow political blame with analysis of demographic pressure, fiscal capacity, ecological limits, trade route realignments, and multi-generational institutional decay.

4. **Complete Elimination of Diagrams and Visual Schemas**:
   - Absolute ban on diagrams, flow charts, ASCII tables, markdown tables, bullet points (`*`, `-`), numbered lists, LaTeX equations, and blockquotes (`>`).
   - Translate all timelines, genealogies, cycle diagrams, and structural matrices into continuous, fluid, highly articulated prose paragraphs.

5. **Total Suppression of YAML Frontmatter in Output**:
   - Extract `channel_name`, `video_id`, and metadata from input for orientation only.
   - The output Markdown file must begin directly on Line 1 with the primary Markdown heading (`##`). Zero YAML blocks or `---` delimiters in output.

---

## Socratic Audit & Gap Analysis for Longue Durée

Execute an internal 2-pass audit on the input text before generating the final expanded narrative:

### Pass 1: Intra-Text Longitudinal Socratic Audit (5 Structural Dimensions)
1. **Temporal Horizon Delimitation**:
   - What is the true time-depth of the problem discussed? If the text discusses a 21st-century issue, what are its 18th-century, 16th-century, or classical roots? Where does the text suffer from presentism or short-term temporal myopia?
2. **Geo-Ecological & Material Substrate**:
   - What physical constraints of geography, soil, waterways, topography, or climate silently condition the human actions described? What material scarcities or surpluses govern the actors?
3. **Causal Stratification (Structure vs. Conjuncture vs. Event)**:
   - Are surface events (e.g., a decree, an election, an assassination) wrongly elevated to ultimate causes? What are the underlying multi-decade conjunctures and multi-century structural invariants?
4. **Secular Inertia and Mentalities**:
   - What unconscious cultural assumptions, theological residues, or institutional traditions from previous centuries are steering modern behavior without being acknowledged?
5. **Palimpsestic Stratification Audit**:
   - What older historical strata lie buried beneath the modern concepts, boundaries, or technologies described? What was the previous function of this institution or space before it was repurposed?

### Pass 2: Historical-Scientific Long-Wave Mapping
1. **Multi-Secular Precursor Tracking**: Identify institutional, ideological, and material precursors across at least 2 to 5 centuries prior to the events described.
2. **Material and Logistical Limits**: Calculate the physical, energetic, and caloric constraints (e.g., transport costs before steam, agricultural energy budgets, silver/gold availability) that bounded historical options.
3. **Institutional Drift and Sedimentation**: Trace how laws, bureaucracies, and tax structures gradually drifted away from their founding intent while retaining ancient formal architecture.
4. **Macro-Cycle Realignment**: Contextualize the phenomena within global secular cycles (e.g., Kondratiev long waves, Braudelian secular trends, demographic Malthusian cycles).

---

## Conducting Textual Conceptual Expansion

- **Replace Abstractions with Empirical Depth**: Substitute generic historical statements with precise dates, verified figures, monetary amounts, demographic estimates, treaty articles, and verified geographical designations researched and validated on the web.
- **Narrative Spine Preservation**: Avoid chaotic divergence. Maintain a relentless longitudinal spine that tracks the core thesis across macro-phases of historical time.
- **Fluid Connectives**: Connect paragraphs using sophisticated temporal, causal, and dialectical transitions (e.g., *"Sob a aparente estabilidade da ordem jurídica setecentista, entretanto, operavam forças tectônicas de reconfiguração demográfica..."*).
- **Footnote Relocation**: Secondary biographical sketches, detailed legislative texts, specialized statistical breakdowns, and tangential precursor lineages must be systematically relegated to the **Informações Complementares** section.

---

## Output Structure & Formatting Directives

- **Markdown Header Hierarchy**:
  - `##` for Major Epochs, Secular Centuries, Macro Eras, or Structural Phases.
  - `###` for Specific Decadal Transitions, Regional Stratifications, or Deep Sub-Themes.
- **Typography Standards**:
  - **Bold (`**...**`)**: Apply **strictly and exclusively** on the first occurrence of key historical actors, fundamental concepts, key treaties, and primary geographical/institutional entities.
  - _Italics (`_..._`)_: Apply strictly for Latin coinages, foreign phrases, legal maxims, ship names, and historical book titles.
- **Pure Continuous Prose**: Write exclusively in structured, high-density prose paragraphs.
- **No Bullet Points or Tables**: All temporal progressions and comparative dimensions must be woven directly into the syntax of the paragraphs.

---

## Complementary Information Section

Whenever necessary to prevent narrative fragmentation or conceptual inflation in the main body, append a dedicated section at the very end of the file under the exact header:

```markdown
## Informações Complementares
```

In this section, provide numbered continuous prose paragraphs detailing:
1. Extended historical genealogies of precursor institutions.
2. Geo-climatic and paleoclimatological data (temperatures, tree-ring data, harvest yields).
3. Primary source treaty clauses, diplomatic correspondence, and fiscal ledgers.
4. Deep biographical profiles of long-term institutional architects.
5. In-depth palimpsestic dissections of physical sites or legal statutes.

---

## File Delivery Directive

Write the final output directly to the designated Markdown file:
`cresmo/enriched/<channel_name>/<video_id>.md`

Output zero conversational introductions, meta-commentary, preambles, or concluding remarks. Begin immediately with the top-level Markdown title (`## ...`) on Line 1.
