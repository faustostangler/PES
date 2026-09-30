"""Atomic note serialization and master _index.json management for Obsidian vault.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from cresmo.domain.entities import AtomicNote
from cresmo.domain.exceptions import NoteTypologyError
from cresmo.domain.value_objects import (
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)
from cresmo.infrastructure.adapters.obsidian.utils import (
    _FRONTMATTER_PATTERN,
    MIN_NOTE_DEFINITION_LENGTH,
    atomic_write,
    sanitize_filename,
)


class AtomicNoteVaultHandler:
    """Handles persistence, parsing, and indexing of AtomicNote domain entities."""

    def __init__(self, vault_dir: Path, index_path: Path) -> None:
        self.vault_dir = vault_dir
        self.index_path = index_path

    @staticmethod
    def get_note_subfolder(note_type: NoteType) -> str:
        """Return standardized plural folder name for a note type."""
        if note_type == NoteType.ENTITY:
            return "entities"
        if note_type == NoteType.PROCESS:
            return "processes"
        return f"{note_type.value}s"

    def get_note_path(self, note: AtomicNote) -> Path:
        """Derive target file path in vault/ for an atomic note."""
        sub_folder = self.get_note_subfolder(note.note_type)
        return self.vault_dir / sub_folder / f"{sanitize_filename(note.title.value)}.md"

    def save_atomic_note(self, note: AtomicNote) -> None:
        """Persist individual atomic note with standardized YAML frontmatter."""
        target_path = self.get_note_path(note)

        frontmatter_dict: dict[str, Any] = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "cluster": note.cluster,
            "source": note.source,
            "aliases": list(note.aliases),
            "tags": list(note.content_tags),
        }
        frontmatter_yaml = yaml.dump(frontmatter_dict, allow_unicode=True, sort_keys=False)

        lines: list[str] = [
            "---",
            frontmatter_yaml.strip(),
            "---",
            "",
            f"# [[{note.title.value}]]",
            "",
            "## Definição & Análise Contextual",
            note.definition,
            "",
        ]

        if note.direct_relations:
            lines.append("## Conexões & Relações Diretas")
            for rel in note.direct_relations:
                lines.append(f"- [[{rel.value}]]")
            lines.append("")

        if note.causal_matrix:
            lines.append("## Matriz Causal")
            lines.append(f"- Causa: {note.causal_matrix.cause}")
            lines.append(f"- Efeito: {note.causal_matrix.effect}")
            if note.causal_matrix.epistemic_attribution:
                lines.append(f"- Atribuição Epistêmica: {note.causal_matrix.epistemic_attribution}")
            lines.append("")

        if note.cross_context:
            lines.append("## Redes de Conexão (Cross-Context)")
            if note.cross_context.precursors:
                lines.append(f"- Precursores: {note.cross_context.precursors}")
            if note.cross_context.lateral_events:
                lines.append(f"- Eventos Laterais: {note.cross_context.lateral_events}")
            if note.cross_context.aftermath:
                lines.append(f"- Desdobramentos: {note.cross_context.aftermath}")
            lines.append("")

        atomic_write(target_path, "\n".join(lines).strip() + "\n")

    def parse_atomic_note_file(self, file_path: Path) -> AtomicNote | None:
        """Parse markdown file into AtomicNote domain entity."""
        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError:
            return None

        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            return None

        fm_text, body = match.groups()
        meta = yaml.safe_load(fm_text) or {}
        raw_type = meta.get("type", "concept")
        try:
            note_type = NoteType.from_string(raw_type)
        except (NoteTypologyError, ValueError):
            note_type = NoteType.CONCEPT

        title_str = meta.get("title", file_path.stem)
        title = NoteTitle(title_str)

        # Parse definition
        def_match = re.search(
            r"## Definição & Análise Contextual\s*\n([\s\S]*?)(?=\n## |\Z)",
            body,
        )
        definition = def_match.group(1).strip() if def_match else body.strip()
        if len(definition) < MIN_NOTE_DEFINITION_LENGTH:
            definition = f"Definição contextual de {title.value} com análise teórica substancial."

        # Parse direct relations
        relations: list[NoteTitle] = []
        rel_match = re.search(
            r"## Conexões & Relações Diretas\s*\n([\s\S]*?)(?=\n## |\Z)",
            body,
        )
        if rel_match:
            for rel_str in re.findall(r"\[\[(.*?)\]\]", rel_match.group(1)):
                if rel_str.strip().lower() != title.value.lower():
                    relations.append(NoteTitle(rel_str.strip()))

        # Parse causal matrix
        causal_matrix: CausalMatrix | None = None
        cm_match = re.search(r"## Matriz Causal\s*\n([\s\S]*?)(?=\n## |\Z)", body)
        if cm_match:
            cm_text = cm_match.group(1)
            cause = re.search(r"- Causa:\s*(.*)", cm_text)
            effect = re.search(r"- Efeito:\s*(.*)", cm_text)
            attrib = re.search(r"- Atribuição Epistêmica:\s*(.*)", cm_text)
            causal_matrix = CausalMatrix(
                cause=cause.group(1).strip() if cause else "",
                effect=effect.group(1).strip() if effect else "",
                epistemic_attribution=attrib.group(1).strip() if attrib else "",
            )

        # Parse cross context
        cross_context: CrossContextRelations | None = None
        cc_match = re.search(
            r"## Redes de Conexão \(Cross-Context\)\s*\n([\s\S]*?)(?=\n## |\Z)", body
        )
        if cc_match:
            cc_text = cc_match.group(1)
            prec = re.search(r"- Precursores:\s*(.*)", cc_text)
            lat = re.search(r"- Eventos Laterais:\s*(.*)", cc_text)
            aft = re.search(r"- Desdobramentos:\s*(.*)", cc_text)
            cross_context = CrossContextRelations(
                precursors=prec.group(1).strip() if prec else "",
                lateral_events=lat.group(1).strip() if lat else "",
                aftermath=aft.group(1).strip() if aft else "",
            )

        return AtomicNote(
            title=title,
            note_type=note_type,
            definition=definition,
            content_tags=tuple(meta.get("tags", ())),
            domain=meta.get("domain", ""),
            cluster=meta.get("cluster", ""),
            source=meta.get("source", ""),
            aliases=tuple(meta.get("aliases", ())),
            direct_relations=tuple(relations),
            causal_matrix=causal_matrix,
            cross_context=cross_context,
        )

    def get_atomic_note_by_title(self, title: NoteTitle) -> AtomicNote | None:
        """Retrieve atomic note by searching index or vault directory."""
        sanitized = sanitize_filename(title.value)
        matched = list(self.vault_dir.glob(f"**/{sanitized}.md"))
        for p in matched:
            if "MOCs" in p.parts:
                continue
            note = self.parse_atomic_note_file(p)
            if note and note.title.value.lower() == title.value.lower():
                return note
        return None

    def get_all_atomic_notes(self) -> list[AtomicNote]:
        """Retrieve all atomic notes in vault/ excluding MOCs."""
        notes: list[AtomicNote] = []
        for file_path in self.vault_dir.glob("**/*.md"):
            if "MOCs" in file_path.parts:
                continue
            note = self.parse_atomic_note_file(file_path)
            if note is not None:
                notes.append(note)
        return notes

    def update_index_entry(self, note: AtomicNote) -> None:
        """Update master _index.json lookup index atomically."""
        index: dict[str, Any] = {}
        if self.index_path.exists():
            try:
                index = json.loads(self.index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                index = {}

        target_path = self.get_note_path(note)
        relative_path = str(target_path.relative_to(self.vault_dir))

        entry_payload = {
            "title": note.title.value,
            "type": note.note_type.value,
            "domain": note.domain,
            "cluster": note.cluster,
            "aliases": list(note.aliases),
            "path": relative_path,
        }

        # Index primary title
        index[note.title.value.lower()] = entry_payload
        # Index aliases
        for alias in note.aliases:
            index[alias.lower()] = entry_payload

        atomic_write(
            self.index_path,
            json.dumps(index, ensure_ascii=False, indent=2),
        )

    def delete_atomic_note(self, note: AtomicNote) -> None:
        """Remove atomic note file from vault and clean up index entries."""
        sanitized = sanitize_filename(note.title.value)
        matched = list(self.vault_dir.glob(f"**/{sanitized}.md"))
        for p in matched:
            if "MOCs" not in p.parts and p.is_file():
                p.unlink(missing_ok=True)

        self.remove_index_entry(note.title.value.lower())
        for alias in note.aliases:
            self.remove_index_entry(alias.lower())

    def remove_index_entry(self, key: str) -> None:
        """Remove specific canonical title or alias key from master _index.json."""
        if not self.index_path.exists():
            return
        try:
            index = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        k = key.lower().strip()
        if k in index:
            del index[k]
            atomic_write(
                self.index_path,
                json.dumps(index, ensure_ascii=False, indent=2),
            )
