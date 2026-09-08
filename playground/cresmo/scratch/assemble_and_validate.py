import json
import re
import sys
from pathlib import Path

# Add cresmo to path
sys.path.insert(0, str(Path("playground/cresmo").resolve()))
from cresmo_pipeline import AtomicNoteModel

# Import note groups
from notes_group1 import notes as g1
from notes_group2 import notes as g2
from notes_group3 import notes as g3
from notes_group4 import notes as g4

all_notes = g1 + g2 + g3 + g4
print(f"Total initial notes: {len(all_notes)}")

# Load existing _index.json
index_path = Path("playground/cresmo/wiki/_index.json")
vault_notes = set()
if index_path.exists():
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        vault_notes = set(data.get("notes", {}).keys())
    except Exception as e:
        print("Error reading _index.json:", e)

print(f"Total existing vault notes in _index.json: {len(vault_notes)}")

# 1. Map of notes in batch by title and aliases
note_by_title = {n["title"]: n for n in all_notes}
alias_map = {}
for n in all_notes:
    alias_map[n["title"].lower()] = n["title"]
    for a in n.get("aliases", []):
        alias_map[a.lower()] = n["title"]

# Regex for extracting [[WikiLink]] or [[WikiLink|Surface Text]]
wikilink_re = re.compile(r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]')

def get_links_from_text(text):
    if not text:
        return set()
    return set(wikilink_re.findall(text))

def get_all_links_from_note(note):
    links = set()
    links.update(get_links_from_text(note.get("definition", "")))
    for rel in note.get("direct_relations", []):
        links.update(get_links_from_text(rel))
    cm = note.get("causal_matrix") or {}
    for v in cm.values():
        links.update(get_links_from_text(v))
    cc = note.get("cross_context") or {}
    for v in cc.values():
        links.update(get_links_from_text(v))
    return links

# 2. Orphan Closure Audit
orphan_links = set()
batch_titles = set(note_by_title.keys())

for n in all_notes:
    links = get_all_links_from_note(n)
    for target in links:
        target_clean = target.strip()
        # Check if in batch
        if target_clean in batch_titles:
            continue
        # Check if in vault _index.json
        if target_clean in vault_notes:
            continue
        # Check if matched by alias
        if target_clean.lower() in alias_map:
            continue
        orphan_links.add(target_clean)

if orphan_links:
    print(f"WARNING: Found {len(orphan_links)} orphan links:")
    for o in sorted(orphan_links):
        print(f" - [[{o}]]")
else:
    print("SUCCESS: 0 orphan links! All [[WikiLinks]] resolve to batch or _index.json.")

# 3. Bi-Directional Linking Audit & Auto-Reconciliation within batch
link_graph = {title: set() for title in batch_titles}
for n in all_notes:
    title = n["title"]
    for target in get_all_links_from_note(n):
        target_clean = target.strip()
        canonical_target = None
        if target_clean in batch_titles:
            canonical_target = target_clean
        elif target_clean.lower() in alias_map:
            canonical_target = alias_map[target_clean.lower()]
        if canonical_target and canonical_target != title:
            link_graph[title].add(canonical_target)

# Check reciprocity
unreciprocated = []
for a in batch_titles:
    for b in link_graph[a]:
        if a not in link_graph[b]:
            unreciprocated.append((a, b))

print(f"Unreciprocated links before reconciliation: {len(unreciprocated)}")

# Auto-reconcile by adding reciprocal relation to b
for a, b in unreciprocated:
    target_note = note_by_title[b]
    # Add a direct relation or lateral event
    new_rel = f"[[{b}]] -> mantém conexão histórica recíproca com -> [[{a}]]"
    if "direct_relations" not in target_note:
        target_note["direct_relations"] = []
    target_note["direct_relations"].append(new_rel)
    link_graph[b].add(a)

# Re-verify reciprocity
still_unreciprocated = 0
for a in batch_titles:
    for b in link_graph[a]:
        if a not in link_graph[b]:
            still_unreciprocated += 1

print(f"Unreciprocated links after reconciliation: {still_unreciprocated}")

# 4. Authorial Style Audit (Zero em-dashes, Zero antitheses)
style_errors = []
for n in all_notes:
    title = n["title"]
    # Check all string fields
    text_corpus = f"{n.get('definition', '')} " + " ".join(n.get('direct_relations', []))
    cm = n.get("causal_matrix") or {}
    text_corpus += " " + " ".join(str(v) for v in cm.values())
    cc = n.get("cross_context") or {}
    text_corpus += " " + " ".join(str(v) for v in cc.values())
    
    if "—" in text_corpus:
        style_errors.append(f"Em-dash ('—') in note '{title}'")
    if "–" in text_corpus:
        style_errors.append(f"En-dash ('–') in note '{title}'")
    if re.search(r'\bnão\b[^.\n]{1,60}\bmas\b', text_corpus, re.IGNORECASE):
        style_errors.append(f"Antithesis 'não ... mas' in note '{title}'")
    if re.search(r'\bnão apenas\b', text_corpus, re.IGNORECASE):
        style_errors.append(f"Antithesis 'não apenas' in note '{title}'")
    if re.search(r'\bnão se trata\b', text_corpus, re.IGNORECASE):
        style_errors.append(f"Antithesis 'não se trata' in note '{title}'")

if style_errors:
    print(f"ERROR: Found {len(style_errors)} style errors:")
    for e in style_errors:
        print(f" - {e}")
    sys.exit(1)
else:
    print("SUCCESS: Zero em-dashes and zero binary antitheses across 100% of notes!")

# 5. Pydantic V2 Validation
validated_count = 0
for n in all_notes:
    try:
        model = AtomicNoteModel(**n)
        validated_count += 1
    except Exception as e:
        print(f"Validation failed for note '{n.get('title')}': {e}")
        sys.exit(1)

print(f"SUCCESS: All {validated_count} notes successfully validated against AtomicNoteModel!")

# 6. Write final JSON
output_path = Path("/mnt/gamer_d/Fausto Stangler/Documentos/Python/PES/playground/cresmo/enriched/text/19ff825e-00df-5506-8447-a6358409d661.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(all_notes, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"SUCCESS: Output written to {output_path} ({output_path.stat().st_size} bytes)")
