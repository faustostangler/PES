"""Cresmo Knowledge Synthesis Pipeline Orchestrator.

Orchestrates the cognitive synthesis pipeline per ADR-007 (Template Method) and ADR-021:
- Raw Ingestion (MediaIngestionPort ACL)
- Raw Indexing (IndexRawTranscriptsUseCase)
- Fluid Prose Synthesis (FillGapsUseCase)
- Longitudinal & Synchronic Expansion (ExpandCompendiumUseCase)
- Holistic Inventory Discovery (DiscoverAtomicInventoryUseCase)
- Batched Atomic Synthesis (SynthesizeAtomicBatchUseCase)
- Map of Content Reconciliation (ReconcileMOCsUseCase)
- Duplicate Unification & Entity Resolution (UnifyDuplicateNotesUseCase)

Conforms to:
- ADR-001: Cresmo Modular Monolith Strangling
- ADR-007: Pipeline Template Method DRY
- ADR-021: Unified Pipeline Execution Template Method and Telemetry
- SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeVar, overload

import yaml

logger = logging.getLogger(__name__)

_StageRet = TypeVar("_StageRet")

from cresmo.application.ports import (
    DefaultPipelineSettings,
    LedgerRepositoryPort,
    LLMTransformationPort,
    MediaIngestionPort,
    MetricsPort,
    NoOpMetricsPort,
    NoOpPromptProviderPort,
    NoOpTelemetryPort,
    PipelineSettingsProtocol,
    PromptProviderPort,
    TelemetryPort,
    VaultRepositoryPort,
)
from cresmo.application.use_cases import (
    ConcatMasterUseCase,
    DeduplicationReport,
    DiscoverAtomicInventoryUseCase,
    ExpandCompendiumUseCase,
    FillGapsUseCase,
    IndexRawTranscriptsUseCase,
    IngestRawTranscriptUseCase,
    ReconcileMOCsUseCase,
    SynthesizeAtomicBatchUseCase,
    UnifyDuplicateNotesUseCase,
)
from cresmo.domain.entities import (
    AtomicNote,
    ChannelTenantId,
    EnrichedCompendium,
    MapOfContent,
    PipelineSessionId,
    RawTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CresmoDomainError
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    ChannelId,
    ChannelName,
    ContentId,
    RawIndexEntry,
    is_processable_transcript_file,
)


@dataclass(frozen=True)
class PipelineResult:
    """Summary record emitted at the conclusion of an end-to-end pipeline execution.

    Encapsulates both the terminal operational outcome and the rich domain aggregates
    and intermediate artifacts produced across all incremental synthesis stages.

    Attributes:
        content_id: Canonical ContentId processed.
        success: True if all stages completed successfully without unhandled errors.
        synthesized_notes: Tuple of all newly synthesized AtomicNote domain aggregates.
        reconciled_mocs: Tuple of MapOfContent aggregates updated or created.
        raw_transcript: Optional RawTranscript aggregate root from raw ingestion.
        index_entry: Optional RawIndexEntry catalog projection from raw indexing.
        compendium: Optional EnrichedCompendium aggregate root from fluid prose & expansion.
        inventory: Optional AtomicEntityInventory value object from inventory discovery.
        dedup_report: Optional DeduplicationReport execution summary from duplicate unification.
        duplicates_unified: Total count of duplicate notes consolidated during duplicate unification.
        already_processed: True if execution was skipped due to ledger idempotency match.
        error_message: Optional error message string if execution terminated early.
    """

    content_id: ContentId
    success: bool
    synthesized_notes: tuple[AtomicNote, ...] = ()
    reconciled_mocs: tuple[MapOfContent, ...] = ()
    raw_transcript: RawTranscript | None = None
    index_entry: RawIndexEntry | None = None
    compendium: EnrichedCompendium | None = None
    inventory: AtomicEntityInventory | None = None
    dedup_report: DeduplicationReport | None = None
    duplicates_unified: int = 0
    already_processed: bool = False
    error_message: str | None = None


class CresmoPipeline:
    """Hexagonal Modular Monolith orchestrator for the Cresmo synthesis engine.

    Implements the Template Method execution flow across cognitive synthesis use cases,
    coordinating dependency-injected Use Cases, Ports, and Adapters.
    """

    def __init__(
        self,
        media_ingestion_port: MediaIngestionPort,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        ledger_port: LedgerRepositoryPort | None = None,
        batch_size: int = 5,
        prompt_provider: PromptProviderPort | None = None,
        settings: PipelineSettingsProtocol | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        telemetry_port: TelemetryPort | None = None,
        metrics_port: MetricsPort | None = None,
    ) -> None:
        self.media_ingestion_port = media_ingestion_port

        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port

        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.vault_port = vault_port
        self.ledger_port = ledger_port
        self.telemetry_port: TelemetryPort = telemetry_port or NoOpTelemetryPort()
        self.metrics_port: MetricsPort = metrics_port or NoOpMetricsPort()
        self.settings: PipelineSettingsProtocol = settings or DefaultPipelineSettings()
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()
        self.llm_indexing_port = llm_indexing_port or self.llm_synthesis_port

        # Use cases instantiation
        self.ingest_raw_transcript = IngestRawTranscriptUseCase(
            ingestion_port=self.media_ingestion_port,
            vault_port=self.vault_port,
        )
        self.index_raw = IndexRawTranscriptsUseCase(
            vault_port=self.vault_port,
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            max_chars=self.settings.raw_index_max_chars,
            temperature=self.settings.raw_index_temperature,
            language=self.settings.language,
        )
        self.fill_gaps = FillGapsUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )
        self.expand_compendium = ExpandCompendiumUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )
        self.discover_atomic_inventory = DiscoverAtomicInventoryUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            prompt_provider=self.prompt_provider,
            temperature=0.0,
        )
        self.synthesize_atomic_batch = SynthesizeAtomicBatchUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            batch_size=batch_size,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )
        self.reconcile_mocs = ReconcileMOCsUseCase(
            llm_synthesis_port=self.llm_synthesis_port,
            vault_port=self.vault_port,
            prompt_provider=self.prompt_provider,
            temperature=self.settings.llm_temperature,
        )
        self.unify_duplicate_notes = UnifyDuplicateNotesUseCase(
            vault_port=self.vault_port,
        )
        self.concat_master = ConcatMasterUseCase(
            vault_port=self.vault_port,
            settings=self.settings,
        )

    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Asynchronously trigger warmup across pipeline LLM ports.

        Dispatches non-blocking model weight preloading for both the primary synthesis LLM port
        and the conceptual indexing LLM port (Ollama/local) so weights are loaded concurrently
        while media ingestion, crawler queries, or file parsing execute.
        """
        self.llm_indexing_port.warmup(timeout_seconds=timeout_seconds)
        if self.llm_synthesis_port is not self.llm_indexing_port:
            self.llm_synthesis_port.warmup(timeout_seconds=timeout_seconds)

    def execute(
        self,
        raw: RawTranscript,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
        entry: RawIndexEntry | None = None,
    ) -> PipelineResult:
        """Execute the end-to-end synthesis pipeline (canonical Template Method).

        Coordinates cognitive synthesis use cases under a single root telemetry session span:
        - Root Span: cresmo.pipeline.execution
        - Idempotency guard (ledger_port.is_processed)
        - Raw Transcript Indexing & Paratactic Synthesis (raw_indexing)
        - Socratic Gap Filler (fluid_prose)
        - Longitudinal & Synchronic Expander (expansion)
        - Holistic Inventory Discovery (inventory)
        - Batched Atomic Synthesis (atomic_batch)
        - Map of Content Reconciliation (mocs)
        - Graph Entity Resolution & Duplicate Unification (duplicate_unification)
        - Ledger mark processed & Session Coherence Evaluation

        Args:
            raw: Input RawTranscript domain aggregate root.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.
            user: Optional UserIdentity (anonymous or identified OAuth user).
            entry: Optional pre-computed RawIndexEntry (e.g. for test doubles or cached cataloging).

        Returns:
            PipelineResult encapsulating all synthesized domain aggregates.
        """
        # Identity & Context
        content_id = raw.content_id
        channel_name = raw.channel_name
        session_id = PipelineSessionId.create(channel=channel_name, content_id=content_id)
        tenant_id = ChannelTenantId.create(channel=channel_name)
        user_identity = user or UserIdentity.anonymous()

        # Trace root (Langfuse/OpenTelemetry)
        with self.telemetry_port.start_pipeline_session(
            session_id=session_id,
            user_id=user_identity,
            channel_tenant_id=tenant_id,
            metadata={"source": "transcript", "channel": channel_name.value},
        ):
            # 1. Idempotency guard & early exit
            if early_result := self._check_idempotent_exit(raw, entry, force_reprocess):
                return early_result

            # 2. Stage Execution Pipeline
            if entry is None:
                entry = self._run_stage(
                    "raw_indexing",
                    lambda: self.index_raw.execute(raw),
                    channel_name=channel_name,
                    content_id=content_id,
                    fatal=False,
                )

            expanded_compendium = self.vault_port.get_enriched_compendium(content_id)
            if expanded_compendium is None:
                fluid_compendium = self._run_stage(
                    "fluid_prose",
                    lambda: self.fill_gaps.execute(
                        raw_transcript=raw,
                        passes=gap_filler_passes,
                    ),
                    channel_name=channel_name,
                    content_id=content_id,
                )
                expanded_compendium = self._run_stage(
                    "expansion",
                    lambda: self.expand_compendium.execute(
                        compendium=fluid_compendium,
                    ),
                    channel_name=channel_name,
                    content_id=content_id,
                )

            inventory = self._run_stage(
                "inventory",
                lambda: self.discover_atomic_inventory.execute(
                    compendium=expanded_compendium,
                ),
                channel_name=channel_name,
                content_id=content_id,
            )

            synthesized_notes = self._run_stage(
                "atomic_batch",
                lambda: self.synthesize_atomic_batch.execute(
                    inventory=inventory,
                    compendium=expanded_compendium,
                ),
                channel_name=channel_name,
                content_id=content_id,
            )

            mocs = self._run_stage(
                "mocs",
                lambda: self.reconcile_mocs.execute(),
                channel_name=channel_name,
                content_id=content_id,
            )

            dedup_report = self._run_stage(
                "duplicate_unification",
                lambda: self.unify_duplicate_notes.execute(),
                channel_name=channel_name,
                content_id=content_id,
            )

            # 3. Post-execution ledger mark & telemetry recording
            if self.ledger_port:
                self.ledger_port.mark_processed(content_id)

            self._record_session_completion(
                session_id=session_id,
                content_id=content_id,
                channel_name=channel_name,
                synthesized_notes=synthesized_notes,
                inventory=inventory,
                mocs=mocs,
                dedup_report=dedup_report,
            )

            return PipelineResult(
                content_id=content_id,
                success=True,
                raw_transcript=raw,
                index_entry=entry,
                compendium=expanded_compendium,
                inventory=inventory,
                synthesized_notes=tuple(synthesized_notes),
                reconciled_mocs=tuple(mocs),
                dedup_report=dedup_report,
                duplicates_unified=dedup_report.duplicates_unified_count,
            )

    def _check_idempotent_exit(
        self,
        raw: RawTranscript,
        entry: RawIndexEntry | None,
        force_reprocess: bool,
    ) -> PipelineResult | None:
        """Evaluate ledger idempotency guard and return existing result if already processed.

        Args:
            raw: Input RawTranscript domain aggregate root.
            entry: Optional pre-computed RawIndexEntry.
            force_reprocess: If True, bypasses ledger idempotency guard.

        Returns:
            PipelineResult if already processed and not force_reprocess, None otherwise.
        """
        content_id = raw.content_id
        if self.ledger_port and self.ledger_port.is_processed(content_id) and not force_reprocess:
            self.metrics_port.increment_counter(
                "cresmo_transcripts_processed_total",
                1.0,
                labels={
                    "channel": raw.channel_name.value,
                    "status": "skipped_idempotent",
                    "modality": "transcript",
                },
            )
            return PipelineResult(
                content_id=content_id,
                success=True,
                raw_transcript=raw,
                index_entry=entry,
                compendium=self.vault_port.get_enriched_compendium(content_id),
                synthesized_notes=(),
                reconciled_mocs=(),
                already_processed=True,
            )
        return None

    @overload
    def _run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        fatal: Literal[True] = ...,
        fallback: _StageRet | None = ...,
    ) -> _StageRet: ...

    @overload
    def _run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        fatal: Literal[False],
        fallback: _StageRet | None = ...,
    ) -> _StageRet | None: ...

    def _run_stage(
        self,
        stage_name: str,
        fn: Callable[[], _StageRet],
        *,
        channel_name: ChannelName,
        content_id: ContentId,
        fatal: bool = True,
        fallback: _StageRet | None = None,
    ) -> _StageRet | None:
        """Execute a pipeline stage wrapped with telemetry spans, metrics, and error handling.

        Args:
            stage_name: Identifier for the stage (e.g. 'fluid_prose', 'atomic_batch').
            fn: Callable executing the use case logic.
            channel_name: Target channel name for metric labeling.
            content_id: Target content identifier for audit logging.
            fatal: If True, re-raises any caught exception. If False, logs warning and returns fallback.
            fallback: Value returned when non-fatal execution encounters an exception.

        Returns:
            Result of fn() or fallback if non-fatal exception caught.
        """
        start_time = time.perf_counter()
        status = "success"

        with self.telemetry_port.start_stage_span(stage_name):
            try:
                return fn()
            except Exception as exc:
                status = "failure"
                self.metrics_port.increment_counter(
                    "cresmo_pipeline_errors_total",
                    1.0,
                    labels={
                        "error_type": exc.__class__.__name__,
                        "channel": channel_name.value,
                        "stage": stage_name,
                    },
                )
                if fatal:
                    raise
                logger.warning(
                    "[Pipeline] %s skipped for %s: %s",
                    stage_name,
                    content_id.value,
                    exc,
                )
                return fallback
            finally:
                elapsed = time.perf_counter() - start_time
                self.metrics_port.observe_histogram(
                    "cresmo_pipeline_stage_duration_seconds",
                    elapsed,
                    labels={
                        "stage": stage_name,
                        "channel": channel_name.value,
                        "status": status,
                    },
                )

    def _record_session_completion(
        self,
        session_id: PipelineSessionId,
        content_id: ContentId,
        channel_name: ChannelName,
        synthesized_notes: Sequence[AtomicNote],
        inventory: AtomicEntityInventory,
        mocs: Sequence[MapOfContent],
        dedup_report: DeduplicationReport,
    ) -> None:
        """Record completed process metrics and session coherence evaluation score per EVAL-001 & ADR-016."""
        self.metrics_port.increment_counter(
            "cresmo_transcripts_processed_total",
            1.0,
            labels={
                "channel": channel_name.value,
                "status": "completed",
                "modality": "transcript",
            },
        )
        self.metrics_port.increment_counter(
            "cresmo_atomic_notes_synthesized_total",
            float(len(synthesized_notes)),
            labels={
                "channel": channel_name.value,
                "note_type": "all",
            },
        )

        item_count = len(inventory.items) if hasattr(inventory, "items") else 1
        coherence_score = (
            min(1.0, len(synthesized_notes) / max(1, item_count)) if item_count else 1.0
        )
        self.telemetry_port.record_session_coherence(
            session_id=session_id,
            content_id=content_id,
            score=coherence_score,
            details={
                "synthesized_notes_count": len(synthesized_notes),
                "inventory_count": item_count,
                "mocs_count": len(mocs),
                "duplicates_unified": dedup_report.duplicates_unified_count,
            },
        )

    def _load_transcript_from_file(self, file_path: Path) -> RawTranscript:
        """Parse and construct RawTranscript domain entity from a local file."""
        if not is_processable_transcript_file(file_path):
            raise CresmoDomainError(
                f"File '{file_path.name}' is an internal Cresmo artifact or system index "
                "and cannot be processed as a transcript."
            )
        if not file_path.is_file():
            raise CresmoDomainError(f"Priority text file not found: {file_path}")

        raw_body = file_path.read_text(encoding="utf-8").strip()
        if not raw_body:
            raise CresmoDomainError(f"Priority text file is empty: {file_path}")

        # Derive ContentId safely (must match ^[a-zA-Z0-9_-]{8,64}$)
        stem = file_path.stem
        clean_stem = "".join(c for c in stem if c.isalnum() or c in ("-", "_"))
        if 8 <= len(clean_stem) <= 64:
            content_id_str = clean_stem
        else:
            # Fallback: combine clean prefix with stable sha256 hash
            prefix = clean_stem[:24] if clean_stem else "text"
            suffix = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()[:16]
            content_id_str = f"{prefix}_{suffix}"

        content_id = ContentId(value=content_id_str)

        title = stem.replace("_", " ").replace("-", " ").title()
        channel_name_raw = file_path.parent.name if file_path.parent.name else "text"
        channel_id_obj: ChannelId | None = ChannelId("priority_text")
        channel_category, _ = classify_channel(ChannelName(channel_name_raw))
        source_url = f"file://{file_path.resolve()}"
        video_description = ""
        body = raw_body

        if raw_body.startswith("---"):
            fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$", raw_body)
            if fm_match:
                fm_text, parsed_body = fm_match.groups()
                body = parsed_body.strip()
                try:
                    meta = yaml.safe_load(fm_text) or {}
                    if meta.get("video_title") or meta.get("title"):
                        title = str(meta.get("video_title") or meta.get("title"))
                    if meta.get("channel_name") or meta.get("channel"):
                        channel_name_raw = str(meta.get("channel_name") or meta.get("channel"))
                    if meta.get("channel_id"):
                        channel_id_obj = ChannelId.from_string(str(meta["channel_id"]))
                    if meta.get("channel_category") or meta.get("domain"):
                        channel_category = str(meta.get("channel_category") or meta.get("domain"))
                    if meta.get("url"):
                        source_url = str(meta["url"])
                    if meta.get("video_description"):
                        video_description = str(meta["video_description"])
                except Exception:  # noqa: BLE001, S110
                    pass

        channel_name = ChannelName(channel_name_raw)
        channel_category = channel_category or classify_channel(channel_name)[0]

        return RawTranscript(
            content_id=content_id,
            channel_name=channel_name,
            body=body,
            title=title,
            source_url=source_url,
            channel_id=channel_id_obj,
            channel_category=channel_category,
            video_description=video_description,
        )

    def run_for_video(
        self,
        video_url: str,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline for a single video source.

        Args:
            video_url: Target YouTube or media URL.
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.
            user: Optional UserIdentity (anonymous or identified OAuth user).

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        self.warmup()
        # Execute raw ingestion for a target media item
        raw = self.ingest_raw_transcript.execute(video_url=video_url)
        if raw is None:
            raise CresmoDomainError(f"Ingestion failed to retrieve transcript for: {video_url}")

        # Execute the end-to-end synthesis pipeline (canonical Template Method).
        return self.execute(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
            user=user,
        )

    def run_for_text_file(
        self,
        file_path: Path,
        gap_filler_passes: int = 3,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
    ) -> PipelineResult:
        """Run the end-to-end synthesis pipeline starting from a local raw text file.

        Bypasses media crawling and speech-to-text ingestion, loading
        the transcript directly into the domain and continuing through the synthesis pipeline.

        Args:
            file_path: Path to the raw text or markdown file (.txt, .md).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.
            user: Optional UserIdentity (anonymous or identified OAuth user).

        Returns:
            PipelineResult summarizing synthesized notes, MOCs, and status.
        """
        if not is_processable_transcript_file(file_path):
            raise CresmoDomainError(
                f"File '{file_path.name}' is an internal Cresmo artifact or system index "
                "and cannot be processed as a transcript."
            )
        self.warmup()
        raw = self._load_transcript_from_file(file_path)

        # Avoid redundant disk I/O when file is already located inside the raw transcript lake
        raw_dir = getattr(self.vault_port, "raw_dir", None)
        is_already_in_raw = False
        if isinstance(raw_dir, Path):
            try:
                is_already_in_raw = file_path.resolve().is_relative_to(raw_dir.resolve())
            except (ValueError, RuntimeError):
                is_already_in_raw = False

        if not is_already_in_raw:
            self.vault_port.save_raw_transcript(raw)

        return self.execute(
            raw=raw,
            gap_filler_passes=gap_filler_passes,
            force_reprocess=force_reprocess,
            user=user,
        )

    def run_for_manifest(
        self,
        manifest_path: Path,
        gap_filler_passes: int = 1,
        force_reprocess: bool = False,
        user: UserIdentity | None = None,
    ) -> list[PipelineResult]:
        """Run the end-to-end synthesis pipeline sequentially for all video URLs in a manifest file.

        Args:
            manifest_path: Path to text file containing video URLs (comments with # and blank lines ignored).
            gap_filler_passes: Number of refinement passes for gap filling.
            force_reprocess: If True, bypasses ledger idempotency guard.
            user: Optional UserIdentity (anonymous or identified OAuth user).

        Returns:
            List of PipelineResult outcomes for each video in the manifest.
        """
        if not manifest_path.is_file():
            raise CresmoDomainError(f"Manifest file not found: {manifest_path}")

        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        urls: list[str] = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                urls.append(line_str)

        results: list[PipelineResult] = []
        for url in urls:
            res = self.run_for_video(
                video_url=url,
                gap_filler_passes=gap_filler_passes,
                force_reprocess=force_reprocess,
                user=user,
            )
            results.append(res)
        return results
