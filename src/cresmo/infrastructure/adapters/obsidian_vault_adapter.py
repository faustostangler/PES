"""Obsidian Second Brain Vault Repository Adapter.

Implements VaultRepositoryPort using atomic filesystem writes, YAML frontmatter serialization,
and tiered index management.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from cresmo.application.ports import VaultRepositoryPort
from cresmo.domain.entities import (
    AtomicNote,
    EnrichedCompendium,
    MapOfContent,
    RawTranscript,
)
from cresmo.domain.exceptions import NoteTypologyError
from cresmo.domain.value_objects import (
    CausalMatrix,
    ContentId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)

_ILLEGAL_FILENAME_CHARS = re.compile(r'[\\/*?:"<>|%]')
_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$")


def sanitize_filename(name: str) -> str:
    """Sanitize note title for safe filesystem path."""
    return _ILLEGAL_FILENAME_CHARS.sub("_", name.strip())


class ObsidianVaultAdapter(VaultRepositoryPort):
    """Filesystem-backed Obsidian Second Brain vault adapter."""

    def __init__(
        self,
        vault_dir: Path | None = None,
        raw_dir: Path | None = None,
        enriched_dir: Path | None = None,
        root_dir: Path | None = None,
    ) -> None:
        effective_vault = Path(vault_dir or root_dir or ".").resolve()
        self.root_dir = effective_vault

        # Decoupled mode (production layout with separate data_dir and vault_dir)
        if raw_dir is not None or enriched_dir is not None:
            self.wiki_dir = effective_vault
            self.raw_dir = (
                Path(raw_dir).resolve()
                if raw_dir is not None
                else effective_vault.parent / "data" / "raw"
            )
            self.enriched_dir = (
                Path(enriched_dir).resolve()
                if enriched_dir is not None
                else effective_vault.parent / "data" / "enriched"
            )
        elif (effective_vault / "entities").is_dir() or (effective_vault / "concepts").is_dir():
            # Vault root already contains atomic note folders directly
            self.wiki_dir = effective_vault
            self.raw_dir = effective_vault.parent / "data" / "raw"
            self.enriched_dir = effective_vault.parent / "data" / "enriched"
        else:
            # Monolithic / legacy mode where root_dir contains wiki/, raw/, enriched/
            self.wiki_dir = effective_vault / "wiki"
            self.raw_dir = effective_vault / "raw"
            self.enriched_dir = effective_vault / "enriched"

        self.mocs_dir = self.wiki_dir / "MOCs"
        self.index_path = self.wiki_dir / "_index.json"

        # Ensure base directory tree exists
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.enriched_dir.mkdir(parents=True, exist_ok=True)
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
        self.mocs_dir.mkdir(parents=True, exist_ok=True)

    def _atomic_write(self, target_path: Path, content: str) -> None:
        """Atomically write text content using temp-file replace pattern."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = target_path.parent / f"{target_path.name}.tmp.{uuid4().hex}"
        temp_file.write_text(content, encoding="utf-8")
        os.replace(temp_file, target_path)

    def save_raw_transcript(self, transcript: RawTranscript) -> None:
        """Persist raw transcript with YAML frontmatter to raw/{channel_name}/{content_id}.md."""
        channel_dir = self.raw_dir / sanitize_filename(transcript.channel_name)
        file_path = channel_dir / f"{transcript.content_id.value}.md"

        frontmatter_dict = {
            "id": transcript.content_id.value,
            "channel": transcript.channel_name,
            "type": "raw_transcript",
        }
        frontmatter_yaml = yaml.dump(frontmatter_dict, allow_unicode=True, sort_keys=False)
        content = f"---\n{frontmatter_yaml}---\n\n{transcript.body}"
        self._atomic_write(file_path, content)

    def get_raw_transcript(self, content_id: ContentId) -> RawTranscript | None:
        """Retrieve raw transcript by searching raw/ directory."""
        target_name = f"{content_id.value}.md"
        matched = list(self.raw_dir.glob(f"**/{target_name}"))
        if not matched:
            return None

        file_path = matched[0]
        text = file_path.read_text(encoding="utf-8")
        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            return RawTranscript(
                content_id=content_id,
                channel_name=file_path.parent.name,
                body=text,
            )

        fm_text, body = match.groups()
        meta = yaml.safe_load(fm_text) or {}
        return RawTranscript(
            content_id=content_id,
            channel_name=meta.get("channel", file_path.parent.name),
            body=body.strip(),
        )

    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        """Persist enriched compendium directly into enriched/ directory."""
        channel_dir = self.enriched_dir / sanitize_filename(compendium.channel_name)
        file_path = channel_dir / f"{compendium.content_id.value}.md"

        frontmatter_dict = {
            "id": compendium.content_id.value,
            "channel": compendium.channel_name,
            "title": compendium.title.value,
            "type": "enriched_compendium",
            "pass_count": compendium.pass_count,
        }
        frontmatter_yaml = yaml.dump(frontmatter_dict, allow_unicode=True, sort_keys=False)
        body_text = (
            f"# {compendium.title.value}\n\n"
            f"{compendium.body}\n\n"
            f"## Informações Complementares\n\n"
            f"{compendium.complementary_info}"
        )
        content = f"---\n{frontmatter_yaml}---\n\n{body_text}"
        self._atomic_write(file_path, content)

    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        """Retrieve enriched compendium by content ID."""
        target_name = f"{content_id.value}.md"
        matched = list(self.enriched_dir.glob(f"**/{target_name}"))
        if not matched:
            return None

        file_path = matched[0]
        text = file_path.read_text(encoding="utf-8")
        match = _FRONTMATTER_PATTERN.match(text)
        if not match:
            return None

        fm_text, raw_body = match.groups()
        meta = yaml.safe_load(fm_text) or {}

        # Split into main body and complementary info
        parts = raw_body.split("## Informações Complementares")
        body_part = parts[0].strip()
        comp_part = parts[1].strip() if len(parts) > 1 else ""

        # Strip initial # title if present
        if body_part.startswith("# "):
            body_lines = body_part.splitlines()
            body_part = "\n".join(body_lines[1:]).strip()

        return EnrichedCompendium(
            content_id=content_id,
            channel_name=meta.get("channel", file_path.parent.name),
            title=NoteTitle(meta.get("title", file_path.stem)),
            body=body_part,
            complementary_info=comp_part,
            pass_count=int(meta.get("pass_count", 1)),
        )

    @staticmethod
    def _get_note_subfolder(note_type: NoteType) -> str:
        """Return standardized plural folder name for a note type."""
        if note_type == NoteType.ENTITY:
            return "entities"
        if note_type == NoteType.PROCESS:
            return "processes"
        return f"{note_type.value}s"

    def _get_note_path(self, note: AtomicNote) -> Path:
        """Derive target file path in wiki/ for an atomic note."""
        sub_folder = self._get_note_subfolder(note.note_type)
        return self.wiki_dir / sub_folder / f"{sanitize_filename(note.title.value)}.md"

    def save_atomic_note(self, note: AtomicNote) -> None:
        """Persist individual atomic note with standardized YAML frontmatter."""
        target_path = self._get_note_path(note)

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

        self._atomic_write(target_path, "\n".join(lines).strip() + "\n")

    def _parse_atomic_note_file(self, file_path: Path) -> AtomicNote | None:
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
        if len(definition) < 20:
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
        """Retrieve atomic note by searching index or wiki directory."""
        sanitized = sanitize_filename(title.value)
        matched = list(self.wiki_dir.glob(f"**/{sanitized}.md"))
        for p in matched:
            if "MOCs" in p.parts:
                continue
            note = self._parse_atomic_note_file(p)
            if note and note.title.value.lower() == title.value.lower():
                return note
        return None

    def get_all_atomic_notes(self) -> list[AtomicNote]:
        """Retrieve all atomic notes in wiki/ excluding MOCs."""
        notes: list[AtomicNote] = []
        for file_path in self.wiki_dir.glob("**/*.md"):
            if "MOCs" in file_path.parts:
                continue
            note = self._parse_atomic_note_file(file_path)
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

        target_path = self._get_note_path(note)
        relative_path = str(target_path.relative_to(self.wiki_dir))

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

        self._atomic_write(
            self.index_path,
            json.dumps(index, ensure_ascii=False, indent=2),
        )

    def save_map_of_content(self, moc: MapOfContent) -> None:
        """Persist Map of Content in wiki/MOCs/ atomically."""
        target_path = self.mocs_dir / f"{sanitize_filename(moc.title.value)}.md"

        frontmatter_dict = {
            "title": moc.title.value,
            "type": "moc",
            "theme": moc.theme,
        }
        frontmatter_yaml = yaml.dump(frontmatter_dict, allow_unicode=True, sort_keys=False)

        lines: list[str] = [
            "---",
            frontmatter_yaml.strip(),
            "---",
            "",
            f"# [[{moc.title.value}]]",
            "",
            moc.overview,
            "",
            "## Notas Associadas",
        ]
        for note_title in moc.associated_notes:
            lines.append(f"- [[{note_title.value}]]")
        lines.append("")

        self._atomic_write(target_path, "\n".join(lines).strip() + "\n")

    def delete_atomic_note(self, note: AtomicNote) -> None:
        """Remove atomic note file from vault and clean up index entries."""
        sanitized = sanitize_filename(note.title.value)
        matched = list(self.wiki_dir.glob(f"**/{sanitized}.md"))
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
            self._atomic_write(
                self.index_path,
                json.dumps(index, ensure_ascii=False, indent=2),
            )

    def rewrite_wiki_links(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        """Rewrite all inbound [[old_title]] links to [[new_title]] across all markdown files in wiki/.

        Returns:
            Count of files updated.
        """
        old_val = old_title.value.strip()
        new_val = new_title.value.strip()
        if old_val.lower() == new_val.lower():
            return 0

        pattern = re.compile(rf"\[\[{re.escape(old_val)}(\|.*?)?\]\]", re.IGNORECASE)
        updated_count = 0

        for file_path in self.wiki_dir.glob("**/*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
            except OSError:
                continue

            def _repl(m: re.Match[str]) -> str:
                pipe_part = m.group(1) or ""
                return f"[[{new_val}{pipe_part}]]"

            new_content, count = pattern.subn(_repl, content)
            if count > 0:
                self._atomic_write(file_path, new_content)
                updated_count += 1

        return updated_count
