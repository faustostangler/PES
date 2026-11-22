Analyze the following complete enriched compendium and produce an exhaustive, deduplicated JSON inventory array of all extractable atomic nodes strictly complying with cresmo-atomic guidelines.

Source Channel: {{channel_name}}
Content Title: {{content_title}}

--- FULL ENRICHED COMPENDIUM TEXT (INCLUDING COMPLEMENTARY INFO) ---
{{compendium_body}}

EXTRACTION INSTRUCTIONS:
1. Execute a sequential scan through all paragraphs and numbered entries in '### Extra Info'.
2. Extract all proper nouns (persons, places, treaties, institutions) as 'entity'.
3. Extract all dated milestones with Big-Endian prefixes ('YYYY-MM-DD ...' or 'YYYY ...') as 'event'.
4. Extract all specialized theories, mechanisms, and models as 'concept'.
5. Extract systemic flows and historical sequences as 'process'.
6. Capture parenthetical variants and abbreviations into the 'aliases' array.

Output STRICTLY a single valid JSON array of objects:
[
  {
    "title": "Canonical Title (with YYYY-MM-DD if event)",
    "type": "entity|concept|event|process",
    "domain": "domain_slug",
    "aliases": ["Alias 1", "Acronym"]
  }
]