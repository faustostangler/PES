"""Prompt Value Objects for template identification across Cresmo."""

from __future__ import annotations

from enum import StrEnum


class PromptKey(StrEnum):
    """Canonical enumeration of all prompt template identifiers across Cresmo."""

    FLUID_PROSE = "fluid_prose"
    GAP_FILLER_PASS1 = "gap_filler_pass1"
    GAP_FILLER_PASS_SUBSEQUENT = "gap_filler_pass_subsequent"
    LONG_EXPANDER = "long_expander"
    WIDE_EXPANDER = "wide_expander"
    ATOMIC_INVENTORY = "atomic_inventory"
    JUDGE_ATOMIC_INVENTORY = "judge_atomic_inventory"
    ATOMIC_BATCH = "atomic_batch"
    RECONCILE_MOCS = "reconcile_mocs"
    RAW_INDEX_SUMMARY = "raw_index_summary"
    RAW_INDEX_CONCEPTS = "raw_index_concepts"
    RAW_INDEX_CONCEPTS_REWRITE = "raw_index_concepts_rewrite"
    RAW_INDEX_SYNTHESIS = "raw_index_synthesis"
    JUDGE_RAW_INDEX_SUMMARY = "judge_raw_index_summary"
    JUDGE_RAW_INDEX_CONCEPTS = "judge_raw_index_concepts"
    JUDGE_RAW_INDEX_SYNTHESIS = "judge_raw_index_synthesis"
    LLM_JUDGE = "llm_judge"
    OLLAMA_CRITIQUE = "ollama_critique"
