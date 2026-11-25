Reconcile, cluster, and synthesize the following vault atomic notes into structured Maps of Content (MOCs), adhering strictly to the cresmo-moc-manager specifications and the cresmo-style-guide:

--- VAULT ATOMIC NOTES TO RECONCILE ---
{{notes_json}}

Existing MOC Context / Domain Index (if available):
{{existing_mocs}}

EXECUTION DIRECTIVES:
1. Audit all atomic notes to ensure 100% coverage with zero orphans. Every note in the input must appear in at least one MOC's 'associated_notes' and be referenced within its contextual narrative index.
2. Cluster notes into appropriate Global Epistemological MOCs ('MOC <Macro Domain>') and Thematic Sub-MOCs ('MOC <Thematic Cluster>').
3. Write an analytical 'overview' for each MOC: an authoritative, continuous narrative synthesis (at least 2 dense paragraphs) that articulates how the concepts, entities, events, and processes intersect, mapping systemic feedback loops, second-order causes, and historical/conceptual trajectories.
4. Ensure zero em-dashes (—) and zero binary antitheses ('not X, but Y') across all narrative prose.

Output strictly a single valid JSON array of objects with the following schema:
[
  {
    "title": "MOC <Domain or Cluster Name>",
    "type": "global_moc" | "sub_moc",
    "domain": "<domain_slug>",
    "cluster": "<cluster_slug>",
    "theme": "Analytical description of the thematic scope",
    "overview": "Analytical narrative synthesis connecting the notes in continuous fluid prose adhering to cresmo-style-guide...",
    "associated_notes": [
      "Exact Note Title 1",
      "Exact Note Title 2"
    ]
  }
]