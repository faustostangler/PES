"""Application Use Case for incrementally indexing raw transcripts.

Extracts a concise key concept and a dense paratactic synthesis paragraph from raw transcripts,
appending the result incrementally to both the channel's semantic catalog (_canal.md) and
the global tabular index (brain.csv).

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-001: Modular Monolith Domain Integrity
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
- ADR-019: SOTA KISS Nomenclature & Value Objects
- ADR-028: Strict Rejection of Standalone Raw Indexing & Universal FluidTranscript Contract
"""

from __future__ import annotations

import logging

from cresmo.application.ports import (
    LlmJudgePort,
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.application.ports.settings import DEFAULT_LANGUAGE
from cresmo.application.use_cases.indexing.distiller import LLMTranscriptDistiller
from cresmo.domain.entities import FluidTranscript, UserIdentity
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import (
    NoteTitle,
    RawIndexEntry,
)

logger = logging.getLogger(__name__)


class IndexRawTranscriptsUseCase:
    """Orchestrates paratactic conceptual indexing of media transcripts from clean fluid prose.

    Conforms to:
        - SPEC-001: Core Knowledge Synthesis Specifications (Incremental Indexing)
        - SPEC-011: Fluid Prose Detranscription and Gap Filler Decoupling
        - ADR-001: Modular Monolith Domain Integrity
        - ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
        - ADR-028: Strict Rejection of Standalone Raw Indexing & Universal FluidTranscript Contract

    Attributes:
        vault_port: Repository port for reading transcripts and appending indexes.
        llm_indexing_port: LLM transformation port for key concept and synthesis extraction.
        prompt_provider: Provider port supplying indexing prompt templates.
        max_chars: Maximum character limit from transcript body fed into LLM prompt (0 = full text).
        temperature: Generation sampling temperature.
        language: Target synthesis language.
        max_rewrites: Maximum corrective rewrite attempts if output violates formatting.
    """

    def __init__(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Trigger warmup on the underlying indexing LLM port (ADR-019: direct contract call)."""
        self.llm_indexing_port.warmup(timeout_seconds=timeout_seconds)

    def execute(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content_id
        channel_name = transcript.channel_name

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = (
            transcript.title.value
            if isinstance(transcript.title, NoteTitle)
            else (transcript.title or video_id.value)
        )

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.body.strip()
        if self.max_chars and self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel_id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel_id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel_id,
                user=user,
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
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content_id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry
