"""Application Use Case for incrementally indexing raw transcripts.

Extracts a concise key concept and a dense paratactic synthesis paragraph from raw transcripts,
appending the result incrementally to both the channel's semantic catalog (_canal.md) and
the global tabular index (brain.csv).

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from cresmo.application.ports import (
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import RawTranscript
from cresmo.domain.value_objects import ContentId, NoteTitle, RawIndexEntry

logger = logging.getLogger(__name__)

_INDICATIVE_PREFIXES = (
    "key concept:",
    "key concepts:",
    "conceito-chave:",
    "conceito chave:",
    "conceitos-chave:",
    "conceitos chave:",
    "conceito:",
    "concept:",
    "síntese conceitual:",
    "sintese conceitual:",
    "síntese:",
    "sintese:",
    "synthesis:",
)

_FORBIDDEN_PREFIX_REGEX = re.compile(
    r"^\s*(?:\*{1,3}|#{1,6}\s*)?"
    r"(?:key\s*concepts?|keywords?|palavras?-chave|conceitos?(?:-chave)?|tópicos?|termo-chave|linha\s*[12]|line\s*[12])"
    r"\s*[:：\-–—]",
    re.IGNORECASE,
)


def is_valid_raw_index_output(raw_output: str) -> bool:
    """Validate that raw index output conforms to expected structure without forbidden labels.

    Args:
        raw_output: Generative LLM response text.

    Returns:
        True if response contains no forbidden prefixes and has valid structure.
    """
    clean = raw_output.strip()
    lines = [line.strip() for line in clean.splitlines() if line.strip()]
    if not lines:
        return False
    first_line = lines[0]
    if _FORBIDDEN_PREFIX_REGEX.search(first_line):
        return False
    clean_first = first_line.strip("\"'`*#_")
    if _FORBIDDEN_PREFIX_REGEX.search(clean_first):
        return False

    # Must have either multi-line structure (Line 1: concepts, Line 2+: synthesis)
    # or single-line comma-delimited structure (<concept>, <synthesis>).
    if len(lines) >= 2:
        return True
    return "," in first_line


def _clean_text_line(text: str) -> str:
    """Strip markdown formatting, quotes, and conversational prefixes from a single line.

    Args:
        text: Raw line text from LLM response.

    Returns:
        Sanitized clean string line.
    """
    clean = text.strip().strip("\"'`*#_")
    lower = clean.lower()
    for prefix in _INDICATIVE_PREFIXES:
        if lower.startswith(prefix):
            clean = clean[len(prefix) :].strip().strip("\"'`*#_")
            lower = clean.lower()
    return clean.strip()


def _clean_concept_line(line: str) -> str:
    """Sanitize Line 1 into comma-separated concepts with zero labels or meta-prefixes.

    Args:
        line: Raw first line from LLM response.

    Returns:
        Comma-separated string of clean concept terms.
    """
    clean = _clean_text_line(line)
    clean = _FORBIDDEN_PREFIX_REGEX.sub("", clean).strip().strip("\"'`*#_:")
    parts = [p.strip().strip("\"'`*#_") for p in clean.split(",") if p.strip().strip("\"'`*#_")]
    if parts:
        return ", ".join(parts)
    return clean or "Síntese Conceitual"


def parse_raw_index_response(raw_output: str, fallback_title: str) -> tuple[str, str]:
    """Parse LLM output into (key_concept, paratactic_synthesis) with fallbacks.

    Supports both:
    1. Multi-line format:
       Line 1: Key Concept
       Line 2+: Paratactic paragraph
    2. Single-line format:
       <Key Concept>, <Synthesis sentence>

    Args:
        raw_output: Generative LLM response text.
        fallback_title: Video title used as fallback concept if extraction is empty.

    Returns:
        Tuple of (key_concept, paratactic_synthesis).
    """
    clean_output = raw_output.strip()
    lines = [line.strip() for line in clean_output.splitlines() if line.strip()]

    if not lines:
        return "Síntese Conceitual", fallback_title

    # Multi-line format
    if len(lines) >= 2:
        concept = _clean_concept_line(lines[0])
        synthesis = " ".join(lines[1:])
        synthesis = _clean_text_line(synthesis)
        if not concept:
            concept = "Síntese Conceitual"
        if not synthesis:
            synthesis = fallback_title
        return concept, synthesis

    # Single-line format (e.g. "Concept, Synthesis")
    single_line = lines[0]
    if "," in single_line:
        part_c, part_s = single_line.split(",", 1)
        concept = _clean_concept_line(part_c)
        synthesis = _clean_text_line(part_s)
        if not concept:
            concept = "Síntese Conceitual"
        if not synthesis:
            synthesis = fallback_title
        return concept, synthesis

    # If single line without comma, treat line as concept or synthesis
    cleaned = _clean_text_line(single_line)
    return "Síntese Conceitual", cleaned or fallback_title


class IndexRawTranscriptsUseCase:
    """Orchestrates paratactic conceptual indexing of raw media transcripts.

    Conforms to:
        - SPEC-001: Core Knowledge Synthesis Specifications (Incremental Indexing)
        - ADR-001: Modular Monolith Domain Integrity
        - ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation

    Attributes:
        vault_repo: Repository port for reading raw transcripts and appending indexes.
        llm: LLM transformation port for key concept and synthesis extraction.
        prompt_provider: Provider port supplying indexing prompt templates.
        max_chars: Maximum character limit from transcript body fed into LLM prompt (0 = full text).
        temperature: Generation sampling temperature.
        language: Target synthesis language.
        max_rewrites: Maximum corrective rewrite attempts if output violates formatting.
    """

    def __init__(
        self,
        vault_repo: VaultRepositoryPort,
        llm: LLMTransformationPort,
        prompt_provider: PromptProviderPort,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = "Português do Brasil",
        max_rewrites: int = 3,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Args:
            vault_repo: Vault persistence adapter for raw transcripts and catalog indexes.
            llm: Language model adapter for conceptual extraction.
            prompt_provider: Provider delivering raw indexing prompt templates.
            max_chars: Maximum character count from raw transcript body to feed prompt (0 = full text).
            temperature: Sampling temperature for LLM transformation.
            language: Target natural language for concept extraction and paratactic synthesis.
            max_rewrites: Maximum corrective rewrite retries when output violates formatting.
        """
        self.vault_repo = vault_repo
        self.llm = llm
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites

    def index_single_transcript(
        self,
        transcript: RawTranscript,
        force: bool = False,
    ) -> RawIndexEntry | None:
        """Index a single raw transcript incrementally if not already indexed.

        Walkthrough:
            1. Check whether content_id is already present in channel _index_<channel>.md index.
            2. If indexed and not force, skip immediately (idempotent 0-token cost).
            3. Format prompt with video title and transcript excerpt in target language.
            4. Invoke LLM transformation contract with telemetry trace_id.
            5. Self-healing loop: if output contains forbidden labels/prefixes, request rewrite.
            6. Parse response into (comma_separated_concepts, synthesis).
            7. Construct RawIndexEntry and append to both channel index and brain.csv.

        Args:
            transcript: The RawTranscript entity to index.
            force: If True, re-index even if already present in channel index.

        Returns:
            The generated RawIndexEntry, or None if skipped or LLM call failed.
        """
        video_id_str = transcript.content_id.value
        channel_name = transcript.channel_name

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_repo.get_indexed_video_ids_for_channel(channel_name)
            if video_id_str in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id_str,
                    channel_name,
                )
                return None

        title_str = (
            transcript.title.value
            if isinstance(transcript.title, NoteTitle)
            else (transcript.title or video_id_str)
        )

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.body.strip()
        if self.max_chars and self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]
        sys_inst, user_prompt = self.prompt_provider.get_raw_index_prompt(
            video_title=title_str,
            transcript_excerpt=excerpt,
            language=self.language,
        )

        try:
            raw_response = self.llm.transform(
                prompt=user_prompt,
                system_instruction=sys_inst,
                temperature=self.temperature,
                trace_id=video_id_str,
            )

            # Self-healing rewrite loop if LLM outputs forbidden prefixes or violates format
            attempts = 0
            while not is_valid_raw_index_output(raw_response) and attempts < self.max_rewrites:
                attempts += 1
                logger.info(
                    "[IndexRaw] Attempt %d: output contains forbidden framing. Requesting format rewrite for '%s'.",
                    attempts,
                    video_id_str,
                )
                rewrite_prompt = self.prompt_provider.get_raw_index_rewrite_prompt(
                    previous_output=raw_response,
                    language=self.language,
                )
                raw_response = self.llm.transform(
                    prompt=rewrite_prompt,
                    system_instruction=sys_inst,
                    temperature=self.temperature,
                    trace_id=video_id_str,
                )
        except Exception as exc:  # noqa: BLE001
            # Gracefully degrade on network/Ollama outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s): %s",
                video_id_str,
                channel_name,
                exc,
            )
            return None

        concept, synthesis = parse_raw_index_response(raw_response, fallback_title=title_str)

        url = (
            transcript.source_url
            if transcript.source_url
            else f"https://youtube.com/watch?v={video_id_str}"
        )

        entry = RawIndexEntry(
            video_id=transcript.content_id,
            url=url,
            title=title_str,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_repo.append_channel_index_entry(channel_name, entry)
        self.vault_repo.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id_str,
            channel_name,
            concept,
        )
        return entry

    def index_channel(self, channel_name: str, force: bool = False) -> list[RawIndexEntry]:
        """Index all raw markdown transcripts under a channel folder.

        Args:
            channel_name: Subdirectory name representing the channel.
            force: If True, forces re-indexing of previously indexed transcripts.

        Returns:
            List of newly created RawIndexEntry instances.
        """
        indexed_entries: list[RawIndexEntry] = []
        raw_dir = getattr(self.vault_repo, "raw_dir", None)
        if raw_dir is None:
            return indexed_entries

        ch_dir = Path(raw_dir) / channel_name
        if not ch_dir.exists() or not ch_dir.is_dir():
            return indexed_entries

        for file_path in sorted(ch_dir.glob("*.md")):
            # Skip system indexes and hidden files
            if file_path.name.startswith("_") or file_path.name == "_canal.md":
                continue

            content_id = ContentId(file_path.stem)
            transcript = self.vault_repo.get_raw_transcript(content_id)
            if transcript is not None:
                entry = self.index_single_transcript(transcript, force=force)
                if entry is not None:
                    indexed_entries.append(entry)

        return indexed_entries

    def index_all_channels(self, force: bool = False) -> dict[str, list[RawIndexEntry]]:
        """Index all raw transcripts across all channels in the raw directory.

        Args:
            force: If True, forces re-indexing across all channels.

        Returns:
            Dictionary mapping channel names to lists of newly generated RawIndexEntry items.
        """
        results: dict[str, list[RawIndexEntry]] = {}
        raw_dir = getattr(self.vault_repo, "raw_dir", None)
        if raw_dir is None:
            return results

        raw_path = Path(raw_dir)
        if not raw_path.exists():
            return results

        for sub_dir in sorted(raw_path.iterdir()):
            if sub_dir.is_dir() and not sub_dir.name.startswith("."):
                entries = self.index_channel(sub_dir.name, force=force)
                if entries:
                    results[sub_dir.name] = entries

        return results
