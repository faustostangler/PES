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
- ADR-026: Clean Code Anti-Patterns & Code Smell Governance (Modularization)
- ADR-028: Strict Rejection of Standalone Raw Indexing & Universal FluidTranscript Contract
"""

from cresmo.application.use_cases.indexing import (
    IndexRawTranscriptsUseCase,
    LLMTranscriptDistiller,
    _can_retry,
    _clean_concept_line,
    _clean_text_line,
    can_retry,
    clean_concept_line,
    clean_text_line,
    is_valid_concepts_output,
    is_valid_raw_index_output,
    is_valid_synthesis_paragraph,
    parse_judge_boolean,
    parse_raw_index_response,
)

__all__ = [
    "IndexRawTranscriptsUseCase",
    "LLMTranscriptDistiller",
    "_can_retry",
    "_clean_concept_line",
    "_clean_text_line",
    "can_retry",
    "clean_concept_line",
    "clean_text_line",
    "is_valid_concepts_output",
    "is_valid_raw_index_output",
    "is_valid_synthesis_paragraph",
    "parse_judge_boolean",
    "parse_raw_index_response",
]
