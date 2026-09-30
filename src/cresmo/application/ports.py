"""Application Ports (Abstract Base Classes) for the Cresmo Knowledge Synthesis Bounded Context.

Defines the Hexagonal Ports that decouple business logic orchestration from infrastructure
adapters (media scraping, LLM APIs, Obsidian filesystem storage, status ledgers, and prompt templates).

Conforms to:
- ADR-001: Modular Monolith Domain Integrity (Ports & Adapters)
- ADR-004: Native Media Ingestion Decommissioning & Pure Python Adapter
- SPEC-001: Core Knowledge Synthesis Specifications
- SPEC-004: Native Media Ingestion Specifications
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator, Mapping
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from cresmo.domain.entities import (
    AtomicNote,
    ChannelTenantId,
    EnrichedCompendium,
    MapOfContent,
    PipelineSessionId,
    RawTranscript,
    UserIdentity,
)
from cresmo.domain.value_objects import (
    ChannelFeedQuery,
    ChannelName,
    ContentId,
    DiscoveredMediaItem,
    LedgerEntry,
    NoteTitle,
    PromptKey,
    RawIndexEntry,
)


class MediaIngestionPort(ABC):
    """Hexagonal Port for media crawling, audio downloading, and subtitle/transcript ingestion.

    Conforms to ADR-004 and SPEC-004. Abstracts external tools (yt-dlp, whisper) behind
    pure domain aggregates (RawTranscript).
    """

    @abstractmethod
    def ingest_single_video(
        self,
        video_url: str,
        output_dir: Path,
        whisper_model: str = "base",
        keep_audio: bool = False,
    ) -> RawTranscript | None:
        """Fetch transcript or transcribe audio for a single video.

        Args:
            video_url: Target YouTube or media item URL.
            output_dir: Directory where raw text and audio scratch files reside.
            whisper_model: Whisper model checkpoint name (tiny, base, small, medium).
            keep_audio: If True, preserves downloaded audio; otherwise cleans up.

        Returns:
            RawTranscript domain aggregate if successful, or None if extraction fails.

        Raises:
            RateLimitExceededError: If upstream provider returns HTTP 429.
            IngestionNetworkError: If socket timeout or network failure occurs.
        """
        raise NotImplementedError("Implement single video ingestion contract.")

    @abstractmethod
    def discover_channel_feed(
        self,
        query: ChannelFeedQuery,
    ) -> list[DiscoveredMediaItem]:
        """Query and discover media items from a channel or playlist feed within constraints.

        Args:
            query: Feed query containing channel URL, lookback window, and count limits.

        Returns:
            List of DiscoveredMediaItem value objects.
        """
        raise NotImplementedError("Implement discover channel feed contract.")

    @abstractmethod
    def extract_channel_url_from_video(
        self,
        video_url: str,
    ) -> str | None:
        """Resolve YouTube channel URL or feed identifier from a video URL.

        Extracts channel/uploader metadata without downloading video or audio streams.

        Args:
            video_url: Canonical or short video URL.

        Returns:
            Canonical channel URL (e.g. https://www.youtube.com/channel/{channel_id})
            or None if resolution fails.
        """
        raise NotImplementedError("Implement video channel resolution contract.")


class LLMTransformationPort(ABC):
    """Hexagonal Port defining contracts for generative synthesis and structured extraction.

    Conforms to ADR-001 and EVAL-001. Shields use cases from provider-specific SDKs
    (Google GenAI, Ollama, local models).
    """

    @abstractmethod
    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation given input prompt and optional system directive.

        Args:
            prompt: Formatted user prompt or synthesis task.
            system_instruction: Optional system instruction guiding model persona.
            temperature: Sampling temperature override.
            trace_id: Optional trace ID (e.g. ContentId or session key).
            session_id: Pipeline session identifier.
            user_id: Operator or channel identifier.

        Returns:
            Generated response text string.

        Raises:
            LLMInfrastructureError: If provider API or socket fails.
            RateLimitExceededError: If rate quotas are exhausted.
        """
        raise NotImplementedError("Implement LLM transformation contract.")

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Asynchronously preload model weights in background if supported by provider.

        Default implementation is a no-op for providers not requiring local weight loading
        (e.g. cloud APIs or test doubles).

        Args:
            timeout_seconds: Optional timeout in seconds for background model loading.
        """

    def wait_for_warmup(self, timeout_seconds: float | None = None) -> bool:
        """Wait at the rendezvous barrier until model warmup completes.

        Default implementation returns True immediately for providers not requiring
        explicit local memory allocation.

        Args:
            timeout_seconds: Optional timeout in seconds to wait for warmup.

        Returns:
            True if warmup completed successfully; False if timed out.
        """
        _ = timeout_seconds
        return True


class VaultRepositoryPort(ABC):
    """Hexagonal Persistence Port for the Obsidian Second Brain vault and raw/enriched storage.

    Conforms to ADR-001 and SPEC-001. Enforces atomic file writes, YAML frontmatter serialization,
    tiered index synchronization (_index.json), and bidirectional WikiLink reconciliation.
    """

    @abstractmethod
    def save_raw_transcript(self, transcript: RawTranscript) -> None:
        """Persist raw transcript to raw storage directory.

        Args:
            transcript: RawTranscript domain aggregate containing verbatim text and metadata.
        """
        raise NotImplementedError("Persist raw transcript atomically.")

    @abstractmethod
    def get_raw_transcript(self, content_id: ContentId) -> RawTranscript | None:
        """Retrieve raw transcript by content ID.

        Args:
            content_id: Target unique content identifier.

        Returns:
            RawTranscript aggregate or None if not present in storage.
        """
        raise NotImplementedError("Retrieve raw transcript by content ID.")

    @abstractmethod
    def save_enriched_compendium(self, compendium: EnrichedCompendium) -> None:
        """Persist enriched compendium directly into enriched/ directory.

        Args:
            compendium: Validated multi-pass fluid prose compendium.
        """
        raise NotImplementedError("Persist enriched compendium atomically.")

    @abstractmethod
    def get_enriched_compendium(self, content_id: ContentId) -> EnrichedCompendium | None:
        """Retrieve enriched compendium by content ID.

        Args:
            content_id: Target unique content identifier.

        Returns:
            EnrichedCompendium aggregate or None if not present in storage.
        """
        raise NotImplementedError("Retrieve enriched compendium by content ID.")

    @abstractmethod
    def save_atomic_note(self, note: AtomicNote) -> None:
        """Persist individual atomic note with standardized YAML frontmatter.

        Args:
            note: Validated AtomicNote aggregate with taxonomy, tags, and WikiLinks.
        """
        raise NotImplementedError("Render frontmatter and persist atomic note atomically.")

    @abstractmethod
    def get_atomic_note_by_title(self, title: NoteTitle) -> AtomicNote | None:
        """Retrieve atomic note by its canonical title.

        Args:
            title: Canonical NoteTitle of the target note.

        Returns:
            Parsed AtomicNote aggregate or None if not found.
        """
        raise NotImplementedError("Read and parse atomic note by title.")

    @abstractmethod
    def get_all_atomic_notes(self) -> list[AtomicNote]:
        """Retrieve all atomic notes currently persisted in the vault.

        Returns:
            List of all parsed AtomicNote aggregates.
        """
        raise NotImplementedError("Retrieve all atomic notes.")

    @abstractmethod
    def update_index_entry(self, note: AtomicNote) -> None:
        """Update master _index.json lookup index with note metadata and aliases.

        Args:
            note: AtomicNote providing title, slug, and alias keys for indexing.
        """
        raise NotImplementedError("Update _index.json atomically.")

    @abstractmethod
    def save_map_of_content(self, moc: MapOfContent) -> None:
        """Persist or update Map of Content in vault/MOCs/.

        Args:
            moc: MapOfContent aggregate reconciling note cluster.
        """
        raise NotImplementedError("Persist Map of Content atomically.")

    @abstractmethod
    def delete_atomic_note(self, note: AtomicNote) -> None:
        """Remove atomic note file from vault and clean up index entries.

        Args:
            note: Target note to delete.
        """
        raise NotImplementedError("Delete atomic note.")

    @abstractmethod
    def rewrite_wiki_links(self, old_title: NoteTitle, new_title: NoteTitle) -> int:
        """Rewrite all inbound [[old_title]] links to [[new_title]] across vault markdown files.

        Args:
            old_title: Prior note title being renamed.
            new_title: Target canonical note title.

        Returns:
            Count of markdown files updated with rewritten links.
        """
        raise NotImplementedError("Rewrite wiki links.")

    @abstractmethod
    def remove_index_entry(self, key: str) -> None:
        """Remove specific canonical title or alias key from master _index.json.

        Args:
            key: Title or alias lookup key to purge.
        """
        raise NotImplementedError("Remove index entry.")

    @abstractmethod
    def get_enriched_files_for_channel(self, channel_name: ChannelName) -> list[Path]:
        """Retrieve sorted list of all enriched markdown file paths for a given channel.

        Args:
            channel_name: Human-readable creator channel name.

        Returns:
            List of Path objects for all channel enriched markdown files.
        """
        raise NotImplementedError("Retrieve enriched file paths for channel.")

    @abstractmethod
    def save_master_document(
        self,
        channel_name: ChannelName,
        channel_category: str,
        part_number: int,
        content: str,
    ) -> Path:
        """Persist aggregated master document to master/<channel_category>/<channel_slug>_001.md.

        Args:
            channel_name: Creator channel name.
            channel_category: Macro taxonomy category name.
            part_number: 1-based sequential part number.
            content: Consolidated markdown document string.

        Returns:
            Path to the saved master document on disk.
        """
        raise NotImplementedError("Persist master document atomically.")

    @abstractmethod
    def clear_master_documents_for_channel(
        self,
        channel_name: ChannelName,
        channel_category: str,
    ) -> None:
        """Delete previous master parts for channel before writing fresh sequential parts.

        Args:
            channel_name: Channel name whose prior parts will be purged.
            channel_category: Macro category under which master files reside.
        """
        raise NotImplementedError("Clear previous master documents for channel.")

    @abstractmethod
    def get_indexed_video_ids_for_channel(self, channel_name: ChannelName) -> set[ContentId]:
        """Retrieve set of ContentIds already indexed in the channel's _canal.md.

        Args:
            channel_name: Channel identifier.

        Returns:
            Set of ContentId instances recorded in the channel raw index.
        """
        raise NotImplementedError("Retrieve indexed video IDs for channel.")

    @abstractmethod
    def append_channel_index_entry(self, channel_name: ChannelName, entry: RawIndexEntry) -> None:
        """Append raw index entry to data/raw/<channel_name>/_canal.md atomically.

        Args:
            channel_name: Channel identifier.
            entry: RawIndexEntry value object.
        """
        raise NotImplementedError("Append entry to channel raw index.")

    @abstractmethod
    def append_brain_csv_entry(self, entry: RawIndexEntry) -> None:
        """Append raw index entry to data/brain.csv atomically.

        Args:
            entry: RawIndexEntry value object.
        """
        raise NotImplementedError("Append entry to brain.csv.")

    @abstractmethod
    def get_channel_index_path(self, channel_name: ChannelName) -> Path:
        """Return absolute path to channel's _canal.md index file.

        Args:
            channel_name: Channel identifier.

        Returns:
            Path to the target _canal.md.
        """
        raise NotImplementedError("Return channel index path.")


class LedgerRepositoryPort(ABC):
    """Hexagonal Persistence Port for tracking processed content status and idempotency.

    Conforms to ADR-001 and ADR-003. Employs transactional SQLite WAL storage to guarantee
    zero duplicate LLM calls and reproducible execution audits.
    """

    @abstractmethod
    def is_processed(self, content_id: ContentId) -> bool:
        """Check whether a content item has already completed all pipeline stages.

        Args:
            content_id: Target ContentId.

        Returns:
            True if marked COMPLETED in ledger; False otherwise.
        """
        raise NotImplementedError("Check processed ledger status.")

    @abstractmethod
    def mark_processed(self, content_id: ContentId) -> None:
        """Record content item as successfully processed.

        Args:
            content_id: ContentId to mark COMPLETED.
        """
        raise NotImplementedError("Record content ID in processed ledger.")

    @abstractmethod
    def save_entry(self, entry: LedgerEntry) -> None:
        """Persist or update an immutable LedgerEntry audit record atomically.

        Args:
            entry: LedgerEntry value object with timestamps and outcome status.
        """
        raise NotImplementedError("Persist ledger entry.")

    @abstractmethod
    def get_entry(self, content_id: ContentId) -> LedgerEntry | None:
        """Retrieve the latest LedgerEntry for a given content ID.

        Args:
            content_id: ContentId lookup key.

        Returns:
            LedgerEntry or None if no record exists.
        """
        raise NotImplementedError("Retrieve ledger entry.")

    @abstractmethod
    def list_entries(self, limit: int = 100) -> list[LedgerEntry]:
        """List recently recorded ledger entries.

        Args:
            limit: Maximum count of entries to return.

        Returns:
            List of LedgerEntry records ordered reverse-chronologically.
        """
        raise NotImplementedError("List ledger entries.")


class PromptProviderPort(ABC):
    """Hexagonal Port for loading decoupled LLM prompt templates and skill specifications.

    Conforms to ADR-001, ADR-017, and ADR-022. Separates raw prompt templates from use cases,
    enabling versioning, prompt mutation testing, and multi-model configuration via a unified
    dispatcher keyed by canonical PromptKey.
    """

    @abstractmethod
    def get_prompt(
        self,
        key: PromptKey,
        **context: Any,
    ) -> tuple[str, str]:
        """Dispatch prompt resolution by canonical PromptKey.

        Args:
            key: Canonical prompt identifier from registry.
            **context: Template variable substitutions (prompt-specific kwargs).

        Returns:
            Tuple containing (system_instruction, user_prompt).
        """
        raise NotImplementedError("Implement prompt dispatch contract.")

    def get_last_prompt_version(self, prompt_name: str) -> Any | None:
        """Return the last resolved version for a given prompt identifier.

        Default implementation returns None for providers that do not track versions.
        """
        _ = prompt_name
        return None


class NoOpPromptProviderPort(PromptProviderPort):
    """Hermetic Null-Object implementation of PromptProviderPort for testing and fallback."""

    def get_prompt(
        self,
        key: PromptKey,
        **context: Any,
    ) -> tuple[str, str]:
        """Format basic system and user prompts without external template dependencies."""
        match key:
            case PromptKey.GAP_FILLER_PASS1:
                channel_name = context.get("channel_name", "")
                file_name = context.get("file_name", "")
                raw_text = context.get("raw_text", "")
                total_passes = context.get("total_passes", 1)
                system_instruction = (
                    f"You are Cresmo Expander. Enrich transcript for {channel_name}."
                )
                user_prompt = (
                    f"Pass 1 of {total_passes} for {channel_name} (file: {file_name}):\n"
                    f"Raw transcript:\n{raw_text}"
                )
                return system_instruction, user_prompt

            case PromptKey.GAP_FILLER_PASS_SUBSEQUENT:
                channel_name = context.get("channel_name", "")
                file_name = context.get("file_name", "")
                raw_text = context.get("raw_text", "")
                current_text = context.get("current_text", "")
                pass_num = context.get("pass_num", 2)
                total_passes = context.get("total_passes", 2)
                system_instruction = (
                    f"You are Cresmo Expander. Enrich transcript for {channel_name}."
                )
                user_prompt = (
                    f"Pass {pass_num} of {total_passes} for {channel_name} (file: {file_name}):\n"
                    f"Raw transcript: {raw_text}\n"
                    f"Current text:\n{current_text}"
                )
                return system_instruction, user_prompt

            case PromptKey.LONG_EXPANDER:
                compendium_body = context.get("compendium_body", "")
                complementary_info = context.get("complementary_info", "")
                system_instruction = "You are Cresmo Long-Expander."
                user_prompt = (
                    "Take the following enriched Markdown document and apply longitudinal analysis:\n\n"
                    f"{compendium_body}\n\n"
                    f"## Informações Complementares\n{complementary_info}"
                )
                return system_instruction, user_prompt

            case PromptKey.WIDE_EXPANDER:
                current_text = context.get("current_text", "")
                system_instruction = "You are Cresmo Wide-Expander."
                user_prompt = (
                    "Take the following longitudinally expanded Markdown document and apply synchronic wide expansion:\n\n"
                    f"{current_text}"
                )
                return system_instruction, user_prompt

            case PromptKey.ATOMIC_INVENTORY:
                compendium_title = context.get("compendium_title", "")
                channel_name = context.get("channel_name", "")
                compendium_body = context.get("compendium_body", "")
                system_instruction = "You are Cresmo Atomic Inventory Specialist (cresmo-atomic)."
                user_prompt = (
                    f"Source Compendium Title: {compendium_title}\n"
                    f"Source Channel: {channel_name}\n\n"
                    f"Source Context:\n{compendium_body}\n\n"
                    'Output strictly a JSON array of candidate entities: [{"title": "...", "type": "entity|concept|event|process"}]'
                )
                return system_instruction, user_prompt

            case PromptKey.JUDGE_ATOMIC_INVENTORY:
                compendium_title = context.get("compendium_title", "")
                channel_name = context.get("channel_name", "")
                compendium_body = context.get("compendium_body", "")
                inventory_json = context.get("inventory_json", "")
                system_instruction = (
                    "You are an impartial evaluator assessing candidate entity extraction. "
                    "Respond strictly with 'true' or 'false'."
                )
                user_prompt = (
                    f"Compendium Title: {compendium_title}\n"
                    f"Channel: {channel_name}\n\n"
                    f"Context:\n{compendium_body}\n\n"
                    f"Candidate Inventory:\n{inventory_json}\n\n"
                    "Does the candidate inventory strictly satisfy all ontological, factual, and typographical criteria? "
                    "Respond ONLY with 'true' or 'false'."
                )
                return system_instruction, user_prompt

            case PromptKey.ATOMIC_BATCH:
                compendium_title = context.get("compendium_title", "")
                channel_name = context.get("channel_name", "")
                compendium_body = context.get("compendium_body", "")
                targets_json = context.get("targets_json", "")
                system_instruction = "You are Cresmo Atomic Note Synthesizer (cresmo-atomic)."
                user_prompt = (
                    f"Source Compendium Title: {compendium_title}\n"
                    f"Source Channel: {channel_name}\n\n"
                    f"Source Context:\n{compendium_body}\n\n"
                    f"Target Entities to Synthesize in this batch:\n{targets_json}\n\n"
                    "Output strictly a JSON array of note objects."
                )
                return system_instruction, user_prompt

            case PromptKey.RECONCILE_MOCS:
                notes_json = context.get("notes_json", "")
                system_instruction = "You are Cresmo MOC Manager (cresmo-moc-manager)."
                user_prompt = f"Atomic Notes in Vault:\n{notes_json}\n\nOutput strictly a JSON array of MOC objects."
                return system_instruction, user_prompt

            case PromptKey.RAW_INDEX_SUMMARY:
                video_title = context.get("video_title", "")
                transcript_excerpt = context.get("transcript_excerpt", "")
                language = context.get("language", "Português do Brasil")
                system_instruction = f"You are Cresmo Indexer. Language: {language}."
                user_prompt = f"Video Title: {video_title}\nExcerpt:\n{transcript_excerpt}"
                return system_instruction, user_prompt

            case PromptKey.RAW_INDEX_CONCEPTS:
                video_title = context.get("video_title", "")
                transcript_excerpt = context.get("transcript_excerpt", "")
                language = context.get("language", "Português do Brasil")
                system_instruction = f"You are Cresmo Concept Extractor. Language: {language}."
                user_prompt = f"Video Title: {video_title}\nExcerpt:\n{transcript_excerpt}"
                return system_instruction, user_prompt

            case PromptKey.RAW_INDEX_CONCEPTS_REWRITE:
                previous_output = context.get("previous_output", "")
                return "", f"Rewrite concepts conforming to rules: {previous_output}"

            case PromptKey.RAW_INDEX_SYNTHESIS:
                video_title = context.get("video_title", "")
                summary = context.get("summary", "")
                language = context.get("language", "Português do Brasil")
                system_instruction = f"You are Cresmo Synthesizer. Language: {language}."
                user_prompt = f"Video Title: {video_title}\nSummary:\n{summary}"
                return system_instruction, user_prompt

            case PromptKey.JUDGE_RAW_INDEX_SUMMARY:
                video_title = context.get("video_title", "")
                transcript_excerpt = context.get("transcript_excerpt", "")
                summary = context.get("summary", "")
                language = context.get("language", "Português do Brasil")
                system_instruction = f"You are Judge. Language: {language}."
                user_prompt = (
                    f"Title: {video_title}\nExcerpt:\n{transcript_excerpt}\nSummary:\n{summary}"
                )
                return system_instruction, user_prompt

            case PromptKey.JUDGE_RAW_INDEX_CONCEPTS:
                video_title = context.get("video_title", "")
                transcript_excerpt = context.get("transcript_excerpt", "")
                concepts = context.get("concepts", "")
                language = context.get("language", "Português do Brasil")
                system_instruction = f"You are Judge. Language: {language}."
                user_prompt = (
                    f"Title: {video_title}\nExcerpt:\n{transcript_excerpt}\nConcepts:\n{concepts}"
                )
                return system_instruction, user_prompt

            case PromptKey.JUDGE_RAW_INDEX_SYNTHESIS:
                video_title = context.get("video_title", "")
                transcript_excerpt = context.get("transcript_excerpt", "")
                synthesis = context.get("synthesis", "")
                language = context.get("language", "Português do Brasil")
                system_instruction = f"You are Judge. Language: {language}."
                user_prompt = (
                    f"Title: {video_title}\nExcerpt:\n{transcript_excerpt}\nSynthesis:\n{synthesis}"
                )
                return system_instruction, user_prompt

            case _:
                raise ValueError(f"Unsupported prompt key: {key}")


class TelemetryPort(ABC):
    """Hexagonal Port for OpenTelemetry distributed tracing, session replays, and FinOps metrics.

    Conforms to ADR-016. Decouples application use cases from concrete telemetry backends
    (OpenTelemetry SDK, Langfuse API, Prometheus).
    """

    @abstractmethod
    def start_pipeline_session(
        self,
        session_id: PipelineSessionId,
        user_id: UserIdentity | ChannelTenantId,
        channel_tenant_id: ChannelTenantId | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AbstractContextManager[Any]:
        """Initiate root OpenTelemetry span binding session_id and user_id attributes.

        Args:
            session_id: Canonical multi-stage content session identifier.
            user_id: UserIdentity (anonymous or identified OAuth user), ChannelTenantId, or string.
            channel_tenant_id: Optional Channel tenant identifier for cost and volume aggregation.
            metadata: Additional contextual metadata (e.g. source, pipeline version).

        Returns:
            ContextManager managing the root span lifecycle.
        """
        raise NotImplementedError

    @abstractmethod
    def start_stage_span(
        self,
        stage_name: str,
        attributes: dict[str, Any] | None = None,
    ) -> AbstractContextManager[Any]:
        """Create child OpenTelemetry span demarcating a discrete pipeline stage.

        Args:
            stage_name: Identifier for the active pipeline stage.
            attributes: Optional key-value attributes to attach to the stage span.

        Returns:
            ContextManager managing the child stage span.
        """
        raise NotImplementedError

    @abstractmethod
    def record_judge_evaluation(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        iteration: int,
        max_iterations: int,
        verdict: str,
    ) -> None:
        """Record an LLM-as-a-judge evaluation iteration and its friction ratio.

        Args:
            session_id: Content session identifier.
            content_id: Media content identifier.
            iteration: 1-based attempt index.
            max_iterations: Configured retry ceiling.
            verdict: PASS or NEEDS_REWRITE verdict.
        """
        raise NotImplementedError

    @abstractmethod
    def record_session_coherence(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        score: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record an end-to-end session coherence evaluation score.

        Args:
            session_id: Content session identifier.
            content_id: Media content identifier.
            score: Coherence score in [0.0, 1.0].
            details: Supporting diagnostic attributes (e.g. wikilink counts).
        """
        raise NotImplementedError

    @abstractmethod
    def record_score(
        self,
        name: str,
        value: float,
        comment: str | None = None,
        trace_id: str | None = None,
    ) -> None:
        """Record an arbitrary evaluation or clinical score to telemetry backend.

        Args:
            name: Identifier for the score (e.g. 'style_compliance', 'faithfulness').
            value: Score metric value.
            comment: Optional explanatory context or rubric details.
            trace_id: Optional trace ID to associate score with directly.
        """
        raise NotImplementedError

    def flush(self) -> None:
        """Flush pending spans, metrics, and buffer queues to backend telemetry collectors.

        Default no-op implementation allowing concrete adapters to gracefully drain
        in-memory buffers without raising NotImplementedError.
        """


class NoOpTelemetryPort(TelemetryPort):
    """Hermetic Null-Object implementation of TelemetryPort for offline/test environments."""

    @contextmanager
    def start_pipeline_session(
        self,
        session_id: PipelineSessionId,
        user_id: UserIdentity | ChannelTenantId,
        channel_tenant_id: ChannelTenantId | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Generator[Any]:
        """No-op session context manager."""
        _ = (session_id, user_id, channel_tenant_id, metadata)
        yield None

    @contextmanager
    def start_stage_span(
        self,
        stage_name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Generator[Any]:
        """No-op stage span context manager."""
        _ = (stage_name, attributes)
        yield None

    def record_judge_evaluation(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        iteration: int,
        max_iterations: int,
        verdict: str,
    ) -> None:
        """No-op judge evaluation recorder."""

    def record_session_coherence(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        score: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """No-op session coherence recorder."""

    def record_score(
        self,
        name: str,
        value: float,
        comment: str | None = None,
        trace_id: str | None = None,
    ) -> None:
        """No-op score recorder."""

    def flush(self) -> None:
        """No-op flush."""


class AnonymizerPort(ABC):
    """Hexagonal Port for data anonymization, PII redaction, and credential scrubbing.

    Conforms to ADR-017. Decouples privacy and LGPD compliance rules from infrastructure
    telemetry collectors and application use cases.
    """

    @abstractmethod
    def mask_text(self, text: str) -> str:
        """Sanitize raw text string by redacting PII (emails, phones) and sensitive secrets.

        Args:
            text: Unsanitized input string.

        Returns:
            Sanitized string with sensitive tokens replaced with redaction markers.
        """
        raise NotImplementedError("Implement mask_text contract.")

    @abstractmethod
    def mask_mapping(self, data: Mapping[str, Any]) -> dict[str, Any]:
        """Recursively scrub sensitive keys and redact sensitive string values in a dictionary.

        Args:
            data: Key-value mapping potentially containing credentials or PII.

        Returns:
            Clean copy of the dictionary with sensitive fields redacted or removed.
        """
        raise NotImplementedError("Implement mask_mapping contract.")

    @abstractmethod
    def mask_span_attributes(self, attributes: Mapping[str, Any]) -> dict[str, Any]:
        """Sanitize OpenTelemetry span attributes before export.

        Args:
            attributes: Raw span attributes mapping.

        Returns:
            Clean dictionary conforming to OpenTelemetry types with sensitive data removed.
        """
        raise NotImplementedError("Implement mask_span_attributes contract.")


class MetricsPort(ABC):
    """Hexagonal Port defining time-series operational and domain metrics contracts.

    Conforms to:
    - ADR-023: Prometheus SRE Golden Signals and DORA Metrics Platform
    - SPEC-008: MetricsPort, Prometheus SRE Golden Signals, and DORA Metrics Platform
    """

    @abstractmethod
    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonically increasing counter by a non-negative value.

        Args:
            name: Canonical metric name conforming to Prometheus naming rules.
            value: Increment value (must be >= 0.0).
            labels: Optional dimensional key-value pairs.

        Raises:
            ValueError: If value is negative.
        """

    @abstractmethod
    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record an observed floating-point value into a histogram distribution.

        Args:
            name: Canonical metric name.
            value: Observed duration or size value (must be >= 0.0).
            labels: Optional dimensional key-value pairs.

        Raises:
            ValueError: If value is negative.
        """

    @abstractmethod
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the current instantaneous value of a gauge.

        Args:
            name: Canonical metric name.
            value: Arbitrary numeric value.
            labels: Optional dimensional key-value pairs.
        """


class NoOpMetricsPort(MetricsPort):
    """Hermetic Null-Object implementation of MetricsPort for offline/test environments."""

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a monotonically increasing counter."""
        _ = (name, labels)
        if value < 0.0:
            raise ValueError("Counter increment must be non-negative")

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record an observed floating-point value into a histogram distribution."""
        _ = (name, labels)
        if value < 0.0:
            raise ValueError("Histogram observation must be non-negative")

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set the current instantaneous value of a gauge."""
        _ = (name, value, labels)


@runtime_checkable
class PipelineSettingsProtocol(Protocol):
    """Protocol defining runtime settings required by application use cases and pipeline."""

    @property
    def raw_index_max_chars(self) -> int: ...

    @property
    def raw_index_temperature(self) -> float: ...

    @property
    def language(self) -> str: ...

    @property
    def llm_temperature(self) -> float: ...

    @property
    def indexing_provider(self) -> str: ...

    @property
    def batch_size(self) -> int: ...

    @property
    def concat_max_words(self) -> int: ...

    @property
    def raw_dir(self) -> Path: ...

    @property
    def enriched_dir(self) -> Path: ...

    @property
    def priority_texts_dir(self) -> Path | None: ...

    @property
    def playlist_path(self) -> Path: ...

    @property
    def playlist_priority_path(self) -> Path | None: ...

    @property
    def discovery_queue_maxsize(self) -> int: ...

    @property
    def channel_discovery_workers(self) -> int: ...

    @property
    def days_lookback(self) -> int: ...

    @property
    def inventory_max_attempts(self) -> int: ...


@dataclass
class DefaultPipelineSettings:
    """Default in-memory settings for standalone application use cases without .env dependency."""

    raw_index_max_chars: int = 2000
    raw_index_temperature: float = 0.2
    language: str = "Português do Brasil"
    llm_temperature: float = 0.7
    indexing_provider: str = "gemini"
    batch_size: int = 5
    concat_max_words: int = 50000
    raw_dir: Path = Path("data/raw")
    enriched_dir: Path = Path("data/enriched")
    priority_texts_dir: Path | None = None
    playlist_path: Path = Path("data/playlist.txt")
    playlist_priority_path: Path | None = None
    discovery_queue_maxsize: int = 50
    channel_discovery_workers: int = 4
    days_lookback: int = 30
    inventory_max_attempts: int = 3
