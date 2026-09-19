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
from cresmo.domain.value_objects import (
    ContentId,
    NoteTitle,
    RawIndexEntry,
    is_processable_transcript_file,
)

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
    r"(?:key\s*concepts?|keywords?|palavras?-chave|conceitos?(?:-chave)?|tópicos?|termo-chave|síntese(?: conceitual)?|sintese(?: conceitual)?|synthesis|linha\s*[12]|line\s*[12])"
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


def is_valid_concepts_output(raw_output: str) -> bool:
    """Validate whether LLM concepts output is clean of forbidden prefixes and labels.

    Args:
        raw_output: Generative LLM response text for key concepts pass.

    Returns:
        True if response is non-empty and contains no forbidden labels or prefixes.
    """
    clean = raw_output.strip()
    if not clean:
        return False
    first_line = clean.splitlines()[0].strip()
    if _FORBIDDEN_PREFIX_REGEX.search(first_line):
        return False
    clean_first = first_line.strip("\"'`*#_")
    return not _FORBIDDEN_PREFIX_REGEX.search(clean_first)


def is_valid_synthesis_paragraph(
    raw_output: str,
    min_words: int = 20,
    max_words: int = 120,
) -> bool:
    """Validate that candidate synthesis output is a single paragraph of appropriate size.

    Args:
        raw_output: Candidate synthesis paragraph from LLM.
        min_words: Minimum word threshold.
        max_words: Maximum word threshold.

    Returns:
        True if the output meets paragraph formatting and size constraints; False otherwise.
    """
    clean = raw_output.strip()
    if not clean:
        return False
    if _FORBIDDEN_PREFIX_REGEX.search(clean):
        return False
    clean_first = clean.splitlines()[0].strip("\"'`*#_")
    if _FORBIDDEN_PREFIX_REGEX.search(clean_first):
        return False

    # Reject multi-paragraph markdown outputs separated by empty lines
    paragraphs = [p.strip() for p in clean.split("\n\n") if p.strip()]
    if len(paragraphs) > 1:
        return False

    # Reject markdown bullet lists or numbered lists
    for line in clean.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ", "1.", "2.", "• ")):
            return False

    words = clean.split()
    return min_words <= len(words) <= max_words


def _can_retry(attempts: int, max_rewrites: int) -> bool:
    """Determine whether another retry attempt is permitted.

    A max_rewrites value of 0 or negative signifies unbounded (infinite) retries.

    Args:
        attempts: Number of rewrite attempts completed so far.
        max_rewrites: Configured threshold limit (0 = infinite).

    Returns:
        True if another attempt is allowed; False otherwise.
    """
    if max_rewrites <= 0:
        return True
    return attempts < max_rewrites


def parse_judge_boolean(raw_output: str) -> bool:
    """Parse boolean verdict from LLM-as-a-judge deterministic response.

    Args:
        raw_output: Verbatim output from judge LLM invocation.

    Returns:
        True if the response confirms compliance ('true'); False otherwise.
    """
    if not raw_output:
        return False
    clean = raw_output.strip()
    clean = re.sub(r"^```(?:json|txt)?\s*", "", clean)
    clean = re.sub(r"\s*```$", "", clean)
    clean = clean.strip().strip(".,;:!?\"'()")
    lower = clean.lower()
    return lower == "true" or lower.startswith("true")


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

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Asynchronously trigger warmup on the underlying LLM port."""
        if hasattr(self.llm, "warmup"):
            self.llm.warmup(timeout_seconds=timeout_seconds)

    def _extract_concepts(
        self,
        video_id: str,
        title: str,
        excerpt: str,
        channel_name: str,
    ) -> str:
        """Extract principal concepts through an iterative LLM-as-a-judge loop.

        Args:
            video_id: Transcript content identifier for tracing.
            title: Content title.
            excerpt: Transcript text excerpt.
            channel_name: Channel name for session and tenant observability tagging.

        Returns:
            Sanitized comma-separated concepts string, falling back to 'Síntese Conceitual'.
        """
        system_instructions, user_prompt = self.prompt_provider.get_raw_index_concepts_prompt(
            video_title=title,
            transcript_excerpt=excerpt,
            language=self.language,
        )

        session_id = f"raw_index_{channel_name}"
        user_id = channel_name
        is_valid = False
        retries = 0
        raw_concepts = ""

        while not is_valid:
            if retries == 0:
                prompt = user_prompt
                trace_id = f"{video_id}_concepts"
                judge_trace_id = f"{video_id}_concepts_judge"
            else:
                logger.info(
                    "[IndexRaw] Attempt %d: concepts compliance check failed for '%s'. Requesting rewrite.",
                    retries,
                    video_id,
                )
                prompt = self.prompt_provider.get_raw_index_concepts_rewrite_prompt(
                    previous_output=raw_concepts,
                    language=self.language,
                )
                trace_id = f"{video_id}_concepts_rewrite_{retries}"
                judge_trace_id = f"{video_id}_concepts_judge_retry_{retries}"

            raw_concepts = self.llm.transform(
                prompt=prompt,
                system_instruction=system_instructions,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )

            if is_valid_concepts_output(raw_concepts):
                judge_system_instructions, judge_prompt = (
                    self.prompt_provider.get_judge_raw_index_concepts_prompt(
                        video_title=title,
                        transcript_excerpt=excerpt,
                        concepts=raw_concepts,
                        language=self.language,
                    )
                )
                judge_response = self.llm.transform(
                    prompt=judge_prompt,
                    system_instruction=judge_system_instructions,
                    temperature=0.0,
                    trace_id=judge_trace_id,
                    session_id=session_id,
                    user_id=user_id,
                )
                is_valid = parse_judge_boolean(judge_response)
            else:
                is_valid = False

            if not is_valid:
                if not _can_retry(retries, self.max_rewrites):
                    break
                retries += 1

        cleaned = _clean_concept_line(raw_concepts)
        return cleaned if cleaned else "Síntese Conceitual"

    def _extract_summary(
        self,
        video_id: str,
        title: str,
        excerpt: str,
        channel_name: str,
    ) -> str:
        """Extract structured conceptual summary through an iterative LLM-as-a-judge loop.

        Args:
            video_id: Transcript content identifier for tracing.
            title: Content title.
            excerpt: Transcript text excerpt.
            channel_name: Channel name for session and tenant observability tagging.

        Returns:
            Sanitized summary string, falling back to title.
        """
        system_instructions, user_prompt = self.prompt_provider.get_raw_index_summary_prompt(
            video_title=title,
            transcript_excerpt=excerpt,
            language=self.language,
        )

        session_id = f"raw_index_{channel_name}"
        user_id = channel_name
        is_valid = False
        retries = 0
        raw_summary = ""
        summary = ""

        while not is_valid:
            trace_id = (
                f"{video_id}_summary" if retries == 0 else f"{video_id}_summary_retry_{retries}"
            )
            judge_trace_id = (
                f"{video_id}_summary_judge"
                if retries == 0
                else f"{video_id}_summary_judge_retry_{retries}"
            )
            if retries > 0:
                logger.info(
                    "[IndexRaw] Attempt %d: summary judge returned false for '%s'. Regenerating summary.",
                    retries,
                    video_id,
                )

            raw_summary = self.llm.transform(
                prompt=user_prompt,
                system_instruction=system_instructions,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            summary = _clean_text_line(raw_summary) or title

            judge_system_instructions, judge_prompt = (
                self.prompt_provider.get_judge_raw_index_summary_prompt(
                    video_title=title,
                    transcript_excerpt=excerpt,
                    summary=summary,
                    language=self.language,
                )
            )
            judge_response = self.llm.transform(
                prompt=judge_prompt,
                system_instruction=judge_system_instructions,
                temperature=0.0,
                trace_id=judge_trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            is_valid = parse_judge_boolean(judge_response)

            if not is_valid:
                if not _can_retry(retries, self.max_rewrites):
                    break
                retries += 1

        return summary if summary else title

    def _extract_synthesis(
        self,
        video_id: str,
        title: str,
        excerpt: str,
        summary: str,
        channel_name: str,
    ) -> str:
        """Synthesize dense single paratactic paragraph through an iterative LLM-as-a-judge loop.

        Args:
            video_id: Transcript content identifier for tracing.
            title: Content title.
            excerpt: Original transcript excerpt used for judge fidelity checking.
            summary: Structured conceptual summary from Pass 2.
            channel_name: Channel name for session and tenant observability tagging.

        Returns:
            Sanitized single paratactic synthesis paragraph, falling back to summary or title.
        """
        system_instructions, user_prompt = self.prompt_provider.get_raw_index_synthesis_prompt(
            video_title=title,
            summary=summary,
            language=self.language,
        )

        session_id = f"raw_index_{channel_name}"
        user_id = channel_name
        is_valid = False
        retries = 0
        raw_synthesis = ""
        synthesis = ""

        while not is_valid:
            trace_id = (
                f"{video_id}_synthesis" if retries == 0 else f"{video_id}_synthesis_retry_{retries}"
            )
            judge_trace_id = (
                f"{video_id}_synthesis_judge"
                if retries == 0
                else f"{video_id}_synthesis_judge_retry_{retries}"
            )
            if retries > 0:
                logger.info(
                    "[IndexRaw] Attempt %d: synthesis compliance check failed for '%s'. Regenerating synthesis.",
                    retries,
                    video_id,
                )

            raw_synthesis = self.llm.transform(
                prompt=user_prompt,
                system_instruction=system_instructions,
                temperature=self.temperature,
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
            )
            synthesis = _clean_text_line(raw_synthesis)

            if is_valid_synthesis_paragraph(synthesis):
                judge_system_instructions, judge_prompt = (
                    self.prompt_provider.get_judge_raw_index_synthesis_prompt(
                        video_title=title,
                        transcript_excerpt=excerpt,
                        synthesis=synthesis,
                        language=self.language,
                    )
                )
                judge_response = self.llm.transform(
                    prompt=judge_prompt,
                    system_instruction=judge_system_instructions,
                    temperature=0.0,
                    trace_id=judge_trace_id,
                    session_id=session_id,
                    user_id=user_id,
                )
                is_valid = parse_judge_boolean(judge_response)
            else:
                is_valid = False

            if not is_valid:
                if not _can_retry(retries, self.max_rewrites):
                    break
                retries += 1

        return synthesis if synthesis else (summary or title)

    def index_single_transcript(
        self,
        transcript: RawTranscript,
        force: bool = False,
    ) -> RawIndexEntry | None:
        """Index a single raw transcript incrementally if not already indexed.

        Walkthrough:
            1. Check whether content_id is already present in channel _canal.md index.
            2. If indexed and not force, skip immediately (idempotent 0-token cost).
            3. Pass 1: Extract strictly comma-separated key concepts from raw transcript excerpt.
            4. Pass 2: Summarize title and raw transcript excerpt into conceptual summary.
            5. Pass 3: Synthesize single dense paratactic paragraph prioritizing NERs and their relations.
            6. Construct RawIndexEntry and append to both channel index and brain.csv.

        Args:
            transcript: The RawTranscript entity to index.
            force: If True, re-index even if already present in channel index.

        Returns:
            The generated RawIndexEntry, or None if skipped or LLM call failed.
        """
        video_id = transcript.content_id.value
        channel_name = transcript.channel_name

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_repo.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id,
                    channel_name,
                )
                return None

        title = (
            transcript.title.value
            if isinstance(transcript.title, NoteTitle)
            else (transcript.title or video_id)
        )

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.body.strip()
        if self.max_chars and self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._extract_concepts(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                channel_name=channel_name,
            )
            summary = self._extract_summary(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                channel_name=channel_name,
            )
            synthesis = self._extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.source_url
            if transcript.source_url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = (
            transcript.channel_category.strip()
            if getattr(transcript, "channel_category", None)
            else ""
        )
        if not category:
            from cresmo.domain.taxonomy import classify_channel

            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content_id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_repo.append_channel_index_entry(channel_name, entry)
        self.vault_repo.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
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
            # Skip system indexes, artifacts, and hidden files
            if not is_processable_transcript_file(file_path):
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
        self.warmup()
        results: dict[str, list[RawIndexEntry]] = {}
        raw_dir = getattr(self.vault_repo, "raw_dir", None)
        if raw_dir is None:
            return results

        raw_path = Path(raw_dir)
        if not raw_path.exists():
            return results

        for sub_dir in sorted(raw_path.iterdir()):
            if sub_dir.is_dir() and not sub_dir.name.startswith((".", "_")):
                entries = self.index_channel(sub_dir.name, force=force)
                if entries:
                    results[sub_dir.name] = entries

        return results
