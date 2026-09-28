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
        key: Canonical internal PromptKey enum.
        langfuse_name: Identifier used for remote versioning in Langfuse prompt management.
        skill_name: Agent skill folder name located under .agents/skills/.
        description: Architectural responsibility and synthesis intent.
    """

    key: PromptKey
    langfuse_name: str
    skill_name: str
    description: str


PROMPT_REGISTRY: dict[PromptKey, PromptMetadata] = {
    PromptKey.GAP_FILLER_PASS1: PromptMetadata(
        key=PromptKey.GAP_FILLER_PASS1,
        langfuse_name="cresmo-gap-filler-pass1",
        skill_name="cresmo-expander",
        description="Pass 1 Socratic gap filling and transcript detranscription into fluid prose.",
    ),
    PromptKey.GAP_FILLER_PASS_SUBSEQUENT: PromptMetadata(
        key=PromptKey.GAP_FILLER_PASS_SUBSEQUENT,
        langfuse_name="cresmo-gap-filler-pass2",
        skill_name="cresmo-expander",
        description="Subsequent passes Socratic densification and epistemic enrichment.",
    ),
    PromptKey.LONG_EXPANDER: PromptMetadata(
        key=PromptKey.LONG_EXPANDER,
        langfuse_name="cresmo-long-expander",
        skill_name="cresmo-long-expander",
        description="Braudelian longue durée and multi-secular structural expansion.",
    ),
    PromptKey.WIDE_EXPANDER: PromptMetadata(
        key=PromptKey.WIDE_EXPANDER,
        langfuse_name="cresmo-wide-expander",
        skill_name="cresmo-wide-expander",
        description="Jaspers synchronic cross-sectional comparative world history expansion.",
    ),
    PromptKey.ATOMIC_INVENTORY: PromptMetadata(
        key=PromptKey.ATOMIC_INVENTORY,
        langfuse_name="cresmo-atomic-inventory",
        skill_name="cresmo-atomic",
        description="Candidate entity extraction from expanded compendium.",
    ),
    PromptKey.JUDGE_ATOMIC_INVENTORY: PromptMetadata(
        key=PromptKey.JUDGE_ATOMIC_INVENTORY,
        langfuse_name="cresmo-judge-atomic-inventory",
        skill_name="cresmo-atomic",
        description="LLM-as-a-judge candidate entity extraction verification for Obsidian Second Brain.",
    ),
    PromptKey.ATOMIC_BATCH: PromptMetadata(
        key=PromptKey.ATOMIC_BATCH,
        langfuse_name="cresmo-atomic-batch",
        skill_name="cresmo-atomic",
        description="Batch synthesis of atomic notes adhering to Obsidian vault format.",
    ),
    PromptKey.RECONCILE_MOCS: PromptMetadata(
        key=PromptKey.RECONCILE_MOCS,
        langfuse_name="cresmo-mocs-reconciliation",
        skill_name="cresmo-moc-manager",
        description="Maps of Content reconciliation and cross-linking with zero orphans.",
    ),
    PromptKey.RAW_INDEX_SUMMARY: PromptMetadata(
        key=PromptKey.RAW_INDEX_SUMMARY,
        langfuse_name="cresmo-raw-index-summary",
        skill_name="cresmo",
        description="Executive summary generation for raw transcripts lake indexing.",
    ),
    PromptKey.RAW_INDEX_CONCEPTS: PromptMetadata(
        key=PromptKey.RAW_INDEX_CONCEPTS,
        langfuse_name="cresmo-raw-index-concepts",
        skill_name="cresmo",
        description="Canonical domain concept extraction for raw transcripts lake indexing.",
    ),
    PromptKey.RAW_INDEX_CONCEPTS_REWRITE: PromptMetadata(
        key=PromptKey.RAW_INDEX_CONCEPTS_REWRITE,
        langfuse_name="cresmo-raw-index-concepts-rewrite",
        skill_name="cresmo",
        description="Corrective rewrite prompt when key concepts violate format or syntax rules.",
    ),
    PromptKey.RAW_INDEX_SYNTHESIS: PromptMetadata(
        key=PromptKey.RAW_INDEX_SYNTHESIS,
        langfuse_name="cresmo-raw-index-synthesis",
        skill_name="cresmo",
        description="Dense paratactic synthesis paragraph generation for raw transcript indexing.",
    ),
    PromptKey.JUDGE_RAW_INDEX_SUMMARY: PromptMetadata(
        key=PromptKey.JUDGE_RAW_INDEX_SUMMARY,
        langfuse_name="cresmo-judge-raw-index-summary",
        skill_name="cresmo",
        description="LLM-as-a-judge summary compliance and quality verification.",
    ),
    PromptKey.JUDGE_RAW_INDEX_CONCEPTS: PromptMetadata(
        key=PromptKey.JUDGE_RAW_INDEX_CONCEPTS,
        langfuse_name="cresmo-judge-raw-index-concepts",
        skill_name="cresmo",
        description="LLM-as-a-judge concepts compliance and delimiter verification.",
    ),
    PromptKey.JUDGE_RAW_INDEX_SYNTHESIS: PromptMetadata(
        key=PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
        langfuse_name="cresmo-judge-raw-index-synthesis",
        skill_name="cresmo",
        description="LLM-as-a-judge synthesis compliance and parataxis verification.",
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
