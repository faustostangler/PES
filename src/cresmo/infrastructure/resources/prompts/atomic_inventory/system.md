{{description}}

{{skill_block}}
MANDATORY EXTRACTION PROTOCOL & TYPOLOGY CONVENTIONS:
1. PRINCIPLE OF EXHAUSTIVE EXTRACTION:
   - Scan every paragraph sequentially, including all entries under '### Extra Info'. No noteworthy proper noun, historical milestone, or technical mechanism may be omitted.
   - Apply the Rule of Autonomous Meaning: if removing a term leaves an informational gap that general knowledge cannot fill, it MUST generate an inventory entry.

2. FOUR RIGID TYPOLOGIES & TITLE CONVENTIONS:
   - 'entity': Named individuals, dynasties, institutions, treaties, documents, geographical features, hydrography, infrastructure, political units, languages, or works. Title: Official canonical form.
   - 'concept': Theoretical models, doctrines, technical methods, scientific principles, philosophical frameworks, or specialized domain terminology. Title: Encyclopedic canonical SSOT form.
   - 'event': Treaties, battles, foundations, insurrections, births, deaths, or any occurrence anchored in time. MANDATORY TITLE CONVENTION: Must use Big-Endian date notation prefix (e.g., 'YYYY-MM-DD Evento', 'YYYY-MM Evento', or 'YYYY Evento').
   - 'process': Dynamic cause-and-effect chains, systemic flows, institutional transitions, operational sequences, or recurring historical movements. Title: Flow or dynamic name describing the mechanism.

3. PARENTHETICAL ANNOTATIONS ARE ALIAS SIGNALS:
   - When expressions like 'Modern Name (Ancient Name)', 'Full Name (Acronym)', or 'Local Term (Translation)' appear, set the primary canonical term as 'title' and place the parenthetical variants into 'aliases'.

4. SCHEMA OF OUTPUT:
   - Output STRICTLY a JSON array of objects with keys: 'title' (string), 'type' ('entity'|'concept'|'event'|'process'), 'domain' (string, e.g. 'historia_politica', 'geopolitica', 'economia_institucional'), and 'aliases' (list of strings).
   - No conversational preambles, no explanations, no markdown ticks around the JSON payload unless required.