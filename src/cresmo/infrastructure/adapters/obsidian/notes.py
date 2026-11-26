"""Atomic note serialization and master _index.json management for Obsidian vault.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Final

import yaml

from cresmo.domain.entities import AtomicNote
from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects import (
    CausalMatrix,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)
from cresmo.infrastructure.adapters.obsidian.utils import (
    _FRONTMATTER_PATTERN,
    atomic_write,
    sanitize_filename,
)

_MOCS_DIR_NAME: Final[str] = "MOCs"
_ENTITIES_SUBFOLDER: Final[str] = "entities"
_PROCESSES_SUBFOLDER: Final[str] = "processes"
_DEFAULT_SUBFOLDER_PLURAL_SUFFIX: Final[str] = "s"
_MARKDOWN_EXT: Final[str] = ".md"
_MARKDOWN_GLOB_ALL: Final[str] = "**/*.md"
_FRONTMATTER_FENCE: Final[str] = "---"
_UTF8_ENCODING: Final[str] = "utf-8"
_INDEX_JSON_INDENT: Final[int] = 2
_HEADING_DEFINITION: Final[str] = "## Definição & Análise Contextual"
_HEADING_RELATIONS: Final[str] = "## Conexões & Relações Diretas"
_HEADING_CAUSAL_MATRIX: Final[str] = "## Matriz Causal"
_HEADING_CROSS_CONTEXT: Final[str] = "## Redes de Conexão (Cross-Context)"
_LINE_CAUSE_PREFIX: Final[str] = "- Causa: "
_LINE_EFFECT_PREFIX: Final[str] = "- Efeito: "
_LINE_ATTRIB_PREFIX: Final[str] = "- Atribuição Epistêmica: "
_LINE_PRECURSORS_PREFIX: Final[str] = "- Precursores: "
_LINE_LATERAL_PREFIX: Final[str] = "- Eventos Laterais: "
_LINE_AFTERMATH_PREFIX: Final[str] = "- Desdobramentos: "
_DEF_SECTION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"## Definição & Análise Contextual\s*\n([\s\S]*?)(?=\n## |\Z)"
)
_REL_SECTION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"## Conexões & Relações Diretas\s*\n([\s\S]*?)(?=\n## |\Z)"
)
_WIKILINK_PATTERN: Final[re.Pattern[str]] = re.compile(r"\[\[(.*?)\]\]")
_CAUSAL_SECTION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"## Matriz Causal\s*\n([\s\S]*?)(?=\n## |\Z)"
)
_CAUSE_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"- Causa:\s*(.*)")
_EFFECT_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"- Efeito:\s*(.*)")
_ATTRIB_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"- Atribuição Epistêmica:\s*(.*)")
_CROSS_CONTEXT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"## Redes de Conexão \(Cross-Context\)\s*\n([\s\S]*?)(?=\n## |\Z)"
)
_PRECURSORS_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"- Precursores:\s*(.*)")
_LATERAL_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"- Eventos Laterais:\s*(.*)")
_AFTERMATH_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"- Desdobramentos:\s*(.*)")
_KEY_TITLE: Final[str] = "title"
_KEY_TYPE: Final[str] = "type"
_KEY_DOMAIN: Final[str] = "domain"
_KEY_CLUSTER: Final[str] = "cluster"
_KEY_SOURCE: Final[str] = "source"
_KEY_ALIASES: Final[str] = "aliases"
_KEY_TAGS: Final[str] = "tags"
_KEY_PATH: Final[str] = "path"


class AtomicNoteVaultHandler:
    """Handles persistence, parsing, and indexing of AtomicNote domain entities."""

    def __init__(self, vault_dir: Path, index_path: Path) -> None:
        self.vault_dir = vault_dir
        self.index_path = index_path

    @staticmethod
    def get_note_subfolder(note_type: NoteType) -> str:
        """Return standardized plural folder name for a note type."""
        if note_type == NoteType.ENTITY:
            return _ENTITIES_SUBFOLDER
        if note_type == NoteType.PROCESS:
            return _PROCESSES_SUBFOLDER
        return f"{note_type.value}{_DEFAULT_SUBFOLDER_PLURAL_SUFFIX}"

    def get_note_path(self, note: AtomicNote) -> Path:
        """Derive target file path in vault/ for an atomic note."""
        sub_folder = self.get_note_subfolder(note.note_type)
        return self.vault_dir / sub_folder / f"{sanitize_filename(note.title.value)}{_MARKDOWN_EXT}"

    def save_atomic_note(self, note: AtomicNote) -> None:
        """Persist individual atomic note with standardized YAML frontmatter."""
        target_path = self.get_note_path(note)

        frontmatter_dict: dict[str, Any] = {
            _KEY_TITLE: note.title.value,
            _KEY_TYPE: note.note_type.value,
            _KEY_DOMAIN: note.domain,
            _KEY_CLUSTER: note.cluster,
            _KEY_SOURCE: note.source,
            _KEY_ALIASES: list(note.aliases),
            _KEY_TAGS: list(note.content_tags),
        }
        frontmatter_yaml = yaml.dump(frontmatter_dict, allow_unicode=True, sort_keys=False)

        lines: list[str] = [
            _FRONTMATTER_FENCE,
            frontmatter_yaml.strip(),
            _FRONTMATTER_FENCE,
            "",
            f"# [[{note.title.value}]]",
            "",
            _HEADING_DEFINITION,
            note.definition,
            "",
        ]

        if note.direct_relations:
            lines.append(_HEADING_RELATIONS)
            for rel in note.direct_relations:
                lines.append(f"- [[{rel.value}]]")
            lines.append("")

        if note.causal_matrix:
            lines.append(_HEADING_CAUSAL_MATRIX)
            lines.append(f"{_LINE_CAUSE_PREFIX}{note.causal_matrix.cause}")
            lines.append(f"{_LINE_EFFECT_PREFIX}{note.causal_matrix.effect}")
            if note.causal_matrix.epistemic_attribution:
                lines.append(
                    f"{_LINE_ATTRIB_PREFIX}{note.causal_matrix.epistemic_attribution}"
                )
            lines.append("")

        if note.cross_context:
            lines.append(_HEADING_CROSS_CONTEXT)
            if note.cross_context.precursors:
                lines.append(f"{_LINE_PRECURSORS_PREFIX}{note.cross_context.precursors}")
            if note.cross_context.lateral_events:
                lines.append(f"{_LINE_LATERAL_PREFIX}{note.cross_context.lateral_events}")
            if note.cross_context.aftermath:
                lines.append(f"{_LINE_AFTERMATH_PREFIX}{note.cross_context.aftermath}")
            lines.append("")

        atomic_write(target_path, "\n".join(lines).strip() + "\n")

    def parse_atomic_note_file(self, file_path: Path) -> AtomicNote | None:
        """Parse markdown file into AtomicNote domain entity."""
        try:
            text = file_path.read_text(encoding=_UTF8_ENCODING)
        except OSError:
            return None

        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            return None

        fm_text, body = match.groups()
        meta = yaml.safe_load(fm_text) or {}
        raw_type = meta.get(_KEY_TYPE)
        if isinstance(raw_type, str):
            try:
                note_type = NoteType.from_string(raw_type)
            except (NoteTypologyError, ValueError):
                note_type = NoteType.CONCEPT
        else:
            note_type = NoteType.CONCEPT

        title_str = meta.get(_KEY_TITLE, file_path.stem)
        title = NoteTitle(title_str)

        # Parse definition
        def_match = _DEF_SECTION_PATTERN.search(body)
        definition = def_match.group(1).strip() if def_match else body.strip()

        # Parse direct relations
        relations: list[NoteTitle] = []
        rel_match = _REL_SECTION_PATTERN.search(body)
        if rel_match:
            for rel_str in _WIKILINK_PATTERN.findall(rel_match.group(1)):
                if rel_str.strip().lower() != title.value.lower():
                    relations.append(NoteTitle(rel_str.strip()))

        # Parse causal matrix
        causal_matrix: CausalMatrix | None = None
        cm_match = _CAUSAL_SECTION_PATTERN.search(body)
        if cm_match:
            cm_text = cm_match.group(1)
            cause = _CAUSE_LINE_PATTERN.search(cm_text)
            effect = _EFFECT_LINE_PATTERN.search(cm_text)
            attrib = _ATTRIB_LINE_PATTERN.search(cm_text)
            causal_matrix = CausalMatrix(
                cause=cause.group(1).strip() if cause else "",
                effect=effect.group(1).strip() if effect else "",
                epistemic_attribution=attrib.group(1).strip() if attrib else "",
            )

        # Parse cross context
        cross_context: CrossContextRelations | None = None
        cc_match = _CROSS_CONTEXT_PATTERN.search(body)
        if cc_match:
            cc_text = cc_match.group(1)
            precursors_match = _PRECURSORS_LINE_PATTERN.search(cc_text)
            lateral_events_match = _LATERAL_LINE_PATTERN.search(cc_text)
            aftermath_match = _AFTERMATH_LINE_PATTERN.search(cc_text)
            cross_context = CrossContextRelations(
                precursors=precursors_match.group(1).strip() if precursors_match else "",
                lateral_events=lateral_events_match.group(1).strip()
                if lateral_events_match
                else "",
                aftermath=aftermath_match.group(1).strip() if aftermath_match else "",
            )

        try:
            return AtomicNote(
                title=title,
                note_type=note_type,
                definition=definition,
                content_tags=tuple(meta.get(_KEY_TAGS, ())),
                domain=meta.get(_KEY_DOMAIN, ""),
                cluster=meta.get(_KEY_CLUSTER, ""),
                source=meta.get(_KEY_SOURCE, ""),
                aliases=tuple(meta.get(_KEY_ALIASES, ())),
                direct_relations=tuple(relations),
                causal_matrix=causal_matrix,
                cross_context=cross_context,
            )
        except DomainValidationError:
            return None

    def get_all_atomic_notes(self) -> list[AtomicNote]:
        """Retrieve all atomic notes in vault/ excluding MOCs."""
        notes: list[AtomicNote] = []
        for file_path in self.vault_dir.glob(_MARKDOWN_GLOB_ALL):
            if _MOCS_DIR_NAME in file_path.parts:
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
                index = json.loads(self.index_path.read_text(encoding=_UTF8_ENCODING))
            except (json.JSONDecodeError, OSError):
                index = {}

        target_path = self.get_note_path(note)
        relative_path = str(target_path.relative_to(self.vault_dir))

        entry_payload = {
            _KEY_TITLE: note.title.value,
            _KEY_TYPE: note.note_type.value,
            _KEY_DOMAIN: note.domain,
            _KEY_CLUSTER: note.cluster,
            _KEY_ALIASES: list(note.aliases),
            _KEY_PATH: relative_path,
        }

        # Index primary title
        index[note.title.value.lower()] = entry_payload
        # Index aliases
        for alias in note.aliases:
            index[alias.lower()] = entry_payload

        atomic_write(
            self.index_path,
            json.dumps(index, ensure_ascii=False, indent=_INDEX_JSON_INDENT),
        )

    def delete_atomic_note(self, note: AtomicNote) -> None:
        """Remove atomic note file from vault and clean up index entries."""
        sanitized = sanitize_filename(note.title.value)
        matched = list(self.vault_dir.glob(f"**/{sanitized}{_MARKDOWN_EXT}"))
        for p in matched:
            if _MOCS_DIR_NAME not in p.parts and p.is_file():
                p.unlink(missing_ok=True)

        self._remove_index_entry(note.title.value)
        for alias in note.aliases:
            self._remove_index_entry(alias)

    def _remove_index_entry(self, key: str) -> None:
        """Remove specific canonical title or alias key from master _index.json."""
        if not self.index_path.exists():
            return
        try:
            index = json.loads(self.index_path.read_text(encoding=_UTF8_ENCODING))
        except (json.JSONDecodeError, OSError):
            return

        normalized_key = key.lower().strip()
        if normalized_key in index:
            del index[normalized_key]
            atomic_write(
                self.index_path,
                json.dumps(index, ensure_ascii=False, indent=_INDEX_JSON_INDENT),
            )
