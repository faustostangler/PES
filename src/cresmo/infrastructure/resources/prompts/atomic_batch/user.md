Source Content Title: {{content_title}}
Source Channel: {{channel_name}}

--- SOURCE COMPENDIUM CONTEXT ---
{{compendium_body}}

--- TARGET ENTITIES TO SYNTHESIZE IN THIS BATCH ---
{{targets_json}}

Synthesize each target entity into a complete Obsidian Atomic Note object.
Output strictly a single valid JSON array of objects conforming to the exact schema specification:
[
  {
    "title": "Exact Note Title",
    "type": "entity|concept|event|process",
    "content": ["primary_tag", "primary_tag/subtag"],
    "domain": "domain_slug",
    "cluster": "cluster_slug",
    "source": "{{channel_name}}",
    "aliases": ["Alias 1", "Alias 2"],
    "definition": "Continuous analytical prose with extensive [[WikiLinks]]...",
    "direct_relations": [
      "[[Current Note Title]] -> connector verb -> [[Target Node]]"
    ],
    "causal_matrix": {
      "cause": "Conditional premise or origin...",
      "effect": "Structural consequence or systemic impact...",
      "epistemic_attribution": "Primary historical source or theoretical proponent..."
    },
    "cross_context": {
      "precursors": "Genealogical roots and predecessors linking to [[Precursor Note]]...",
      "lateral_events": "Synchronous parallel context linking to [[Lateral Note]]...",
      "aftermath": "Posterity and systemic developments linking to [[Aftermath Note]]..."
    }
  }
]