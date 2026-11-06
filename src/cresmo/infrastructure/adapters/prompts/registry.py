"""Canonical Prompt Registry and Metadata for Cresmo.

Provides a Single Source of Truth (SSOT) mapping internal template keys,
Langfuse versioned prompt names, agent skills, and semantic descriptions.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-014: Fail-Fast Observability Preflight
    - ADR-017: Prompt Management with Langfuse & Local Fallback
"""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.domain.value_objects import PromptKey


@dataclass(frozen=True)
class PromptMetadata:
    """Immutable specification and linkage for a registered prompt template.

    Attributes:
        key: Canonical internal PromptKey enum (SSOT).
        description: Architectural responsibility and synthesis intent.
        langfuse_slug: Optional custom remote prompt slug override.
    """

    key: PromptKey
    description: str
    langfuse_slug: str | None = None

    @property
    def langfuse_name(self) -> str:
        """Deterministic remote Langfuse identifier (e.g. PromptKey.FLUID_PROSE -> cresmo-fluid-prose)."""
        return self.langfuse_slug or f"cresmo-{self.key.value.replace('_', '-')}"


PROMPT_REGISTRY: dict[PromptKey, PromptMetadata] = {
    PromptKey.FLUID_PROSE: PromptMetadata(
        key=PromptKey.FLUID_PROSE,
        description="You are the Fluid Prose agent within the Cresmo ecosystem. Your task is to transform raw audio transcripts and drafts into continuous, dense, precise, and authoritative text.",
    ),
    PromptKey.GAP_FILLER: PromptMetadata(
        key=PromptKey.GAP_FILLER,
        description="Socratic gap filling and epistemic causal stratification into enriched compendium across iterative passes.",
    ),
    PromptKey.LONG_EXPANDER: PromptMetadata(
        key=PromptKey.LONG_EXPANDER,
        description="Braudelian longue durée and multi-secular structural expansion.",
    ),
    PromptKey.WIDE_EXPANDER: PromptMetadata(
        key=PromptKey.WIDE_EXPANDER,
        description="Jaspers synchronic cross-sectional comparative world history expansion.",
    ),
    PromptKey.ATOMIC_INVENTORY: PromptMetadata(
        key=PromptKey.ATOMIC_INVENTORY,
        description="Candidate entity extraction from expanded compendium.",
    ),
    PromptKey.JUDGE_ATOMIC_INVENTORY: PromptMetadata(
        key=PromptKey.JUDGE_ATOMIC_INVENTORY,
        description="LLM-as-a-judge candidate entity extraction verification for Obsidian Second Brain.",
    ),
    PromptKey.ATOMIC_BATCH: PromptMetadata(
        key=PromptKey.ATOMIC_BATCH,
        description="Batch synthesis of atomic notes adhering to Obsidian vault format.",
    ),
    PromptKey.RECONCILE_MOCS: PromptMetadata(
        key=PromptKey.RECONCILE_MOCS,
        langfuse_slug="cresmo-mocs-reconciliation",
        description="Maps of Content reconciliation and cross-linking with zero orphans.",
    ),
    PromptKey.RAW_INDEX_SUMMARY: PromptMetadata(
        key=PromptKey.RAW_INDEX_SUMMARY,
        description="Executive summary generation for raw transcripts lake indexing.",
    ),
    PromptKey.RAW_INDEX_CONCEPTS: PromptMetadata(
        key=PromptKey.RAW_INDEX_CONCEPTS,
        description="Canonical domain concept extraction for raw transcripts lake indexing.",
    ),
    PromptKey.RAW_INDEX_CONCEPTS_REWRITE: PromptMetadata(
        key=PromptKey.RAW_INDEX_CONCEPTS_REWRITE,
        description="Corrective rewrite prompt when key concepts violate format or syntax rules.",
    ),
    PromptKey.RAW_INDEX_SYNTHESIS: PromptMetadata(
        key=PromptKey.RAW_INDEX_SYNTHESIS,
        description="Dense paratactic synthesis paragraph generation for raw transcript indexing.",
    ),
    PromptKey.JUDGE_RAW_INDEX_SUMMARY: PromptMetadata(
        key=PromptKey.JUDGE_RAW_INDEX_SUMMARY,
        description="LLM-as-a-judge summary compliance and quality verification.",
    ),
    PromptKey.JUDGE_RAW_INDEX_CONCEPTS: PromptMetadata(
        key=PromptKey.JUDGE_RAW_INDEX_CONCEPTS,
        description="LLM-as-a-judge concepts compliance and delimiter verification.",
    ),
    PromptKey.JUDGE_RAW_INDEX_SYNTHESIS: PromptMetadata(
        key=PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
        description="LLM-as-a-judge synthesis compliance and parataxis verification.",
    ),
    PromptKey.JUDGE_FLUID_PROSE: PromptMetadata(
        key=PromptKey.JUDGE_FLUID_PROSE,
        description="LLM-as-a-judge quality evaluation for fluid_prose stage verifying orality removal, semantic faithfulness, NER preservation, and authorial voice.",
    ),
    PromptKey.JUDGE_GAP_FILLER: PromptMetadata(
        key=PromptKey.JUDGE_GAP_FILLER,
        description="LLM-as-a-judge quality evaluation for gap_filler evaluating factual grounding, epistemic depth, causality, and complementary substance.",
    ),
    PromptKey.OLLAMA_CRITIQUE: PromptMetadata(
        key=PromptKey.OLLAMA_CRITIQUE,
        description="Converts structured judge evaluation failures into directed natural language corrective directives.",
    ),
}


LANGFUSE_TO_PROMPT_KEY: dict[str, PromptKey] = {
    meta.langfuse_name: meta.key for meta in PROMPT_REGISTRY.values()
}


def get_prompt_metadata(key: PromptKey | str) -> PromptMetadata:
    """Retrieve metadata definition for a given PromptKey or string name.

    Args:
        key: PromptKey instance or string matching a PromptKey value or langfuse_name.

    Returns:
        Immutable PromptMetadata instance.

    Raises:
        KeyError: If key is not registered in PROMPT_REGISTRY.
    """
    if isinstance(key, PromptKey):
        return PROMPT_REGISTRY[key]

    # Try lookup by string value of PromptKey
    try:
        enum_key = PromptKey(key)
        return PROMPT_REGISTRY[enum_key]
    except ValueError:
        pass

    # Try lookup by langfuse_name
    if key in LANGFUSE_TO_PROMPT_KEY:
        return PROMPT_REGISTRY[LANGFUSE_TO_PROMPT_KEY[key]]

    raise KeyError(f"Unknown prompt key: '{key}'")


__all__ = [
    "LANGFUSE_TO_PROMPT_KEY",
    "PROMPT_REGISTRY",
    "PromptKey",
    "PromptMetadata",
    "get_prompt_metadata",
]
