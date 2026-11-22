{{description}}

{{skill_block}}
MANDATORY SYNTHESIS AND SCHEMA SPECIFICATIONS:
1. PRINCIPLE OF AUTONOMY & SEMANTIC DENSITY:
   - Each note must be completely understandable on its own, with high conceptual density and low verbosity.
   - Embed [[WikiLinks]] across all mentions of named entities, concepts, treaties, dates, and processes throughout all narrative text fields.
   - Grammatical flexions must strictly use alias piping: [[Exact Title|Flexed Word]].
   - Strict bans: ZERO em-dashes (—) and ZERO binary antitheses (e.g., avoid 'não X, mas Y' or 'não apenas X, mas também Y'; formulate all sentences directly and affirmatively).

2. DECLARATIVE TRIPLES (direct_relations):
   - Must strictly be formatted as declarative statements in natural language using directional arrow syntax with WikiLinks:
     '[[Subject Title]] -> action verb or connector -> [[Object Title]]'
   - Do NOT emit plain entity strings. The note's own title must be the subject or object of each triple.

3. CAUSAL MATRIX & CROSS-CONTEXT:
   - causal_matrix: Must identify conditional cause/premise, structural effect/impact, and epistemic attribution (proponent or historical source).
   - cross_context: Connect to adjacent nodes using WikiLinks across precursors (ancestral origins), lateral events (synchronous phenomena), and aftermath (subsequent ramifications).

4. SCHEMA OF OUTPUT:
   - Output strictly a valid JSON array of objects with keys:
     - title: Exact canonical note title (Big-Endian for events, e.g., 'YYYY-MM-DD Name')
     - type: 'entity' | 'concept' | 'event' | 'process'
     - content: Array of hierarchical category tags (e.g., ['historia', 'historia/politica'])
     - domain: Domain slug string (e.g., 'geopolitica', 'historia_medieval')
     - cluster: Thematic micro-context slug string
     - source: Channel and content reference string ('{{channel_name}}')
     - aliases: List of alternative names, acronyms, or flexed surface forms
     - definition: Continuous analytical paragraphs obeying cresmo-style-guide, using internal [[WikiLinks]] extensively
     - direct_relations: List of declarative triple strings ('[[Source]] -> verb -> [[Target]]')
     - causal_matrix: Object with keys 'cause', 'effect', 'epistemic_attribution'
     - cross_context: Object with keys 'precursors', 'lateral_events', 'aftermath'