"""Hexagonal Prompt Provider Port and Null-Object implementation.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity (Ports & Adapters)
- ADR-017: Context & Privacy Isolation
- ADR-022: Multi-Model Prompt Registry & Evaluation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from cresmo.application.ports.settings import DEFAULT_LANGUAGE
from cresmo.domain.value_objects import PromptKey


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


_NOOP_BUILDERS: dict[PromptKey, Callable[[dict[str, Any]], tuple[str, str]]] = {
    PromptKey.FLUID_PROSE: lambda c: (
        f"You are Cresmo Fluid Prose Detranscriptor (cresmo-fluid-prose). Channel: {c.get('channel_name', '')}.",
        f"Transform raw transcript into clean, continuous fluid prose in third-person neutral narrative:\nFile: {c.get('file_name', '')}\n\nTranscript:\n{c.get('raw_text', '')}",
    ),
    PromptKey.GAP_FILLER_PASS1: lambda c: (
        f"You are Cresmo Expander. Enrich transcript for {c.get('channel_name', '')}.",
        f"Pass 1 of {c.get('total_passes', 1)} for {c.get('channel_name', '')} (file: {c.get('file_name', '')}):\nRaw transcript:\n{c.get('raw_text', '')}",
    ),
    PromptKey.GAP_FILLER_PASS_SUBSEQUENT: lambda c: (
        f"You are Cresmo Expander. Enrich transcript for {c.get('channel_name', '')}.",
        f"Pass {c.get('pass_num', 2)} of {c.get('total_passes', 2)} for {c.get('channel_name', '')} (file: {c.get('file_name', '')}):\nRaw transcript: {c.get('raw_text', '')}\nCurrent text:\n{c.get('current_text', '')}",
    ),
    PromptKey.LONG_EXPANDER: lambda c: (
        "You are Cresmo Long-Expander.",
        f"Take the following enriched Markdown document and apply longitudinal analysis:\n\n{c.get('compendium_body', '')}\n\n## Informações Complementares\n{c.get('complementary_info', '')}",
    ),
    PromptKey.WIDE_EXPANDER: lambda c: (
        "You are Cresmo Wide-Expander.",
        f"Take the following longitudinally expanded Markdown document and apply synchronic wide expansion:\n\n{c.get('current_text', '')}",
    ),
    PromptKey.ATOMIC_INVENTORY: lambda c: (
        "You are Cresmo Atomic Inventory Specialist (cresmo-atomic).",
        f'Source Compendium Title: {c.get("compendium_title", "")}\nSource Channel: {c.get("channel_name", "")}\n\nSource Context:\n{c.get("compendium_body", "")}\n\nOutput strictly a JSON array of candidate entities: [{{"title": "...", "type": "entity|concept|event|process"}}]',
    ),
    PromptKey.JUDGE_ATOMIC_INVENTORY: lambda c: (
        "You are an impartial evaluator assessing candidate entity extraction. Respond strictly with 'true' or 'false'.",
        f"Compendium Title: {c.get('compendium_title', '')}\nChannel: {c.get('channel_name', '')}\n\nContext:\n{c.get('compendium_body', '')}\n\nCandidate Inventory:\n{c.get('inventory_json', '')}\n\nDoes the candidate inventory strictly satisfy all ontological, factual, and typographical criteria? Respond ONLY with 'true' or 'false'.",
    ),
    PromptKey.ATOMIC_BATCH: lambda c: (
        "You are Cresmo Atomic Note Synthesizer (cresmo-atomic).",
        f"Source Compendium Title: {c.get('compendium_title', '')}\nSource Channel: {c.get('channel_name', '')}\n\nSource Context:\n{c.get('compendium_body', '')}\n\nTarget Entities to Synthesize in this batch:\n{c.get('targets_json', '')}\n\nOutput strictly a JSON array of note objects.",
    ),
    PromptKey.RECONCILE_MOCS: lambda c: (
        "You are Cresmo MOC Manager (cresmo-moc-manager).",
        f"Atomic Notes in Vault:\n{c.get('notes_json', '')}\n\nOutput strictly a JSON array of MOC objects.",
    ),
    PromptKey.RAW_INDEX_SUMMARY: lambda c: (
        f"You are Cresmo Indexer. Language: {c.get('language', DEFAULT_LANGUAGE)}.",
        f"Video Title: {c.get('video_title', '')}\nExcerpt:\n{c.get('transcript_excerpt', '')}",
    ),
    PromptKey.RAW_INDEX_CONCEPTS: lambda c: (
        f"You are Cresmo Concept Extractor. Language: {c.get('language', DEFAULT_LANGUAGE)}.",
        f"Video Title: {c.get('video_title', '')}\nExcerpt:\n{c.get('transcript_excerpt', '')}",
    ),
    PromptKey.RAW_INDEX_CONCEPTS_REWRITE: lambda c: (
        "",
        f"Rewrite concepts conforming to rules: {c.get('previous_output', '')}",
    ),
    PromptKey.RAW_INDEX_SYNTHESIS: lambda c: (
        f"You are Cresmo Synthesizer. Language: {c.get('language', DEFAULT_LANGUAGE)}.",
        f"Video Title: {c.get('video_title', '')}\nSummary:\n{c.get('summary', '')}",
    ),
    PromptKey.JUDGE_RAW_INDEX_SUMMARY: lambda c: (
        f"You are Judge. Language: {c.get('language', DEFAULT_LANGUAGE)}.",
        f"Title: {c.get('video_title', '')}\nExcerpt:\n{c.get('transcript_excerpt', '')}\nSummary:\n{c.get('summary', '')}",
    ),
    PromptKey.JUDGE_RAW_INDEX_CONCEPTS: lambda c: (
        f"You are Judge. Language: {c.get('language', DEFAULT_LANGUAGE)}.",
        f"Title: {c.get('video_title', '')}\nExcerpt:\n{c.get('transcript_excerpt', '')}\nConcepts:\n{c.get('concepts', '')}",
    ),
    PromptKey.JUDGE_RAW_INDEX_SYNTHESIS: lambda c: (
        f"You are Judge. Language: {c.get('language', DEFAULT_LANGUAGE)}.",
        f"Title: {c.get('video_title', '')}\nExcerpt:\n{c.get('transcript_excerpt', '')}\nSynthesis:\n{c.get('synthesis', '')}",
    ),
    PromptKey.LLM_JUDGE: lambda c: (
        "You are a rigorous, calibrated Quality Evaluation Judge for knowledge synthesis pipelines. You must return ONLY a valid JSON object matching the criteria structure.",
        f"Stage: {c.get('stage_name', '')}\nRequired Criteria to Evaluate: {c.get('criteria_json', '[]')}\n\n--- SOURCE REFERENCE TEXT ---\n{c.get('source_text', '')}\n\n--- CANDIDATE TEXT ---\n{c.get('candidate_text', '')}\n\nEvaluate now and output the JSON verdict.",
    ),
    PromptKey.OLLAMA_CRITIQUE: lambda c: (
        "You are an expert editorial director. Analyze the quality evaluation failure verdict and synthesize at most 3 concise, direct, imperative corrective directives for the generative model to follow on its retry attempt. Output ONLY the directives, with zero preamble.",
        f"Stage '{c.get('stage_name', '')}' failed quality evaluation with overall score {c.get('overall_score', '')}.\nCriteria Failures:\n{c.get('criteria_failures', '')}\n\nPlease output concise, direct instructions to fix these defects:",
    ),
}


class NoOpPromptProviderPort(PromptProviderPort):
    """Hermetic Null-Object implementation of PromptProviderPort for testing and fallback."""

    def get_prompt(
        self,
        key: PromptKey,
        **context: Any,
    ) -> tuple[str, str]:
        """Format basic system and user prompts without external template dependencies."""
        builder = _NOOP_BUILDERS.get(key)
        if builder is None:
            raise ValueError(f"Unsupported prompt key: {key}")
        return builder(context)
