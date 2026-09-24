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
from collections.abc import Mapping
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any

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
    def get_enriched_files_for_channel(self, channel_name: ChannelName | str) -> list[Path]:
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
        channel_name: ChannelName | str,
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
        channel_name: ChannelName | str,
        channel_category: str,
    ) -> None:
        """Delete previous master parts for channel before writing fresh sequential parts.

        Args:
            channel_name: Channel name whose prior parts will be purged.
            channel_category: Macro category under which master files reside.
        """
        raise NotImplementedError("Clear previous master documents for channel.")

    @abstractmethod
    def get_indexed_video_ids_for_channel(self, channel_name: ChannelName | str) -> set[str]:
        """Retrieve set of video IDs already indexed in the channel's _canal.md.

        Args:
            channel_name: Channel identifier.

        Returns:
            Set of string video IDs recorded in the channel raw index.
        """
        raise NotImplementedError("Retrieve indexed video IDs for channel.")

    @abstractmethod
    def append_channel_index_entry(
        self, channel_name: ChannelName | str, entry: RawIndexEntry
    ) -> None:
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
    def get_channel_index_path(self, channel_name: ChannelName | str) -> Path:
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

    Conforms to ADR-001 and EVAL-001. Separates raw prompt templates from use cases,
    enabling versioning, prompt mutation testing, and multi-model configuration.
    """

    @abstractmethod
    def get_gap_filler_prompt(
        self,
        pass_num: int,
        total_passes: int,
        channel_name: ChannelName | str,
        file_name: str,
        raw_text: str,
        current_text: str | None = None,
    ) -> str:
        """Format the Socratic gap filler prompt differentiating pass 1 from subsequent passes.

        Args:
            pass_num: 1-based current enrichment pass.
            total_passes: Total passes configured.
            channel_name: Creator channel name.
            file_name: Source file name for context tracking.
            raw_text: Verbatim ground truth transcript.
            current_text: Previous pass text (populated for pass >= 2).

        Returns:
            Formatted prompt string ready for LLM inference.
        """
        raise NotImplementedError

    @abstractmethod
    def get_long_expander_prompt(
        self,
        compendium_body: str,
        complementary_info: str,
    ) -> str:
        """Format the Braudelian longitudinal expander prompt.

        Args:
            compendium_body: Continuous fluid prose from Stage 2.
            complementary_info: Section text containing dates, context, and secondary details.

        Returns:
            Formatted longitudinal expansion prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_wide_expander_prompt(
        self,
        current_text: str,
    ) -> str:
        """Format the Jaspers synchronic wide expander prompt.

        Args:
            current_text: Longitudinally enriched Markdown prose.

        Returns:
            Formatted synchronic horizontal cross-section prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_inventory_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName | str,
        compendium_body: str,
    ) -> str:
        """Format the atomic inventory extraction prompt.

        Args:
            compendium_title: Compendium title string.
            channel_name: Creator channel name.
            compendium_body: Complete enriched prose text.

        Returns:
            Formatted inventory discovery prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_batch_notes_prompt(
        self,
        compendium_title: str,
        channel_name: ChannelName | str,
        compendium_body: str,
        targets_json: str,
    ) -> str:
        """Format the atomic note batch synthesis prompt.

        Args:
            compendium_title: Compendium title string.
            channel_name: Creator channel name.
            compendium_body: Complete enriched prose text.
            targets_json: JSON string with target entities to synthesize.

        Returns:
            Formatted batched atomic note synthesis prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_mocs_prompt(
        self,
        notes_json: str,
    ) -> str:
        """Format the MOC reconciliation prompt.

        Args:
            notes_json: JSON string of synthesized atomic notes.

        Returns:
            Formatted MOC reconciliation prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_raw_index_summary_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for Pass 1 raw transcript summarization.

        Args:
            video_title: Raw video title string.
            transcript_excerpt: First N characters of raw spoken transcript.
            language: Target synthesis language.

        Returns:
            Tuple containing system instruction and user prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_raw_index_concepts_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for key concepts extraction from raw transcript.

        Args:
            video_title: Raw video title string.
            transcript_excerpt: First N characters of raw spoken transcript.
            language: Target synthesis language.

        Returns:
            Tuple containing system instruction and user prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_raw_index_concepts_rewrite_prompt(
        self,
        previous_output: str,
        language: str = "Português do Brasil",
    ) -> str:
        """Format corrective rewrite prompt when key concepts extraction violates format rules.

        Args:
            previous_output: Verbatim output from previous LLM attempt.
            language: Target natural language for rewrite.

        Returns:
            Formatted rewrite prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_raw_index_synthesis_prompt(
        self,
        video_title: str,
        summary: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for dense paratactic synthesis paragraph.

        Args:
            video_title: Raw video title string.
            summary: Organized conceptual summary of the content.
            language: Target synthesis language.

        Returns:
            Tuple containing system instruction and user prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_judge_raw_index_summary_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        summary: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for LLM-as-a-judge summary compliance verification.

        Args:
            video_title: Raw video title string.
            transcript_excerpt: First N characters of raw spoken transcript.
            summary: Candidate summary produced in Pass 1.
            language: Target evaluation language.

        Returns:
            Tuple containing system instruction and user prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_judge_raw_index_concepts_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        concepts: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for LLM-as-a-judge concepts compliance verification.

        Args:
            video_title: Raw video title string.
            transcript_excerpt: First N characters of raw spoken transcript.
            concepts: Candidate comma-separated concepts.
            language: Target evaluation language.

        Returns:
            Tuple containing system instruction and user prompt string.
        """
        raise NotImplementedError

    @abstractmethod
    def get_judge_raw_index_synthesis_prompt(
        self,
        video_title: str,
        transcript_excerpt: str,
        synthesis: str,
        language: str = "Português do Brasil",
    ) -> tuple[str, str]:
        """Format (system_instruction, user_prompt) for LLM-as-a-judge synthesis compliance verification.

        Args:
            video_title: Raw video title string.
            transcript_excerpt: First N characters of raw spoken transcript.
            synthesis: Candidate single-paragraph synthesis.
            language: Target evaluation language.

        Returns:
            Tuple containing system instruction and user prompt string.
        """
        raise NotImplementedError


class TelemetryPort(ABC):
    """Hexagonal Port for OpenTelemetry distributed tracing, session replays, and FinOps metrics.

    Conforms to ADR-016. Decouples application use cases from concrete telemetry backends
    (OpenTelemetry SDK, Langfuse API, Prometheus).
    """

    @abstractmethod
    def start_pipeline_session(
        self,
        session_id: PipelineSessionId,
        user_id: UserIdentity | ChannelTenantId | str,
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
