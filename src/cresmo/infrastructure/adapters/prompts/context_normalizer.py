"""Declarative prompt variable schemas and shared local/remote context normalization.

Conforms to:
    - ADR-034: Title Context Propagation in Prompt Rendering
    - ADR-052: Langfuse Chat-Native Prompt Catalog & Local JSON Fallback
    - ADR-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
    - SPEC-071: Langfuse-Mirrored Prompt Resources, Context Normalization Parity & Taxonomy Relocation
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from cresmo.domain.value_objects import DEFAULT_LANGUAGE, PromptKey

__all__ = [
    "DEFAULT_LANGUAGE",
    "PROMPT_VARIABLE_SCHEMAS",
    "PromptVariableSchema",
    "normalize_prompt_context",
]


_KEY_RAW_TEXT: Final[str] = "raw_text"
_KEY_SOURCE_TEXT: Final[str] = "source_text"
_KEY_CONTENT_TITLE: Final[str] = "content_title"
_KEY_TITLE: Final[str] = "title"
_KEY_SUMMARY: Final[str] = "summary"
_KEY_TRANSCRIPT_EXCERPT: Final[str] = "transcript_excerpt"
_KEY_LANGUAGE: Final[str] = "language"
_KEY_PASS_NUM: Final[str] = "pass_num"
_KEY_PREV_PASS_NUM: Final[str] = "prev_pass_num"
_KEY_CURRENT_TEXT: Final[str] = "current_text"
_KEY_DRAFT_SECTION: Final[str] = "draft_section"
_DEFAULT_PASS_NUM: Final[int] = 1
_MIN_PREV_PASS_NUM: Final[int] = 0
_ITERATIVE_SOURCE_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    _KEY_RAW_TEXT: (_KEY_RAW_TEXT, _KEY_SOURCE_TEXT),
    _KEY_SOURCE_TEXT: (_KEY_SOURCE_TEXT, _KEY_RAW_TEXT),
}
_CONTENT_TITLE_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    _KEY_CONTENT_TITLE: (_KEY_CONTENT_TITLE, _KEY_TITLE),
}


@dataclass(frozen=True, slots=True)
class PromptVariableSchema:
    """Declarative normalization rules for a single PromptKey."""

    key: PromptKey
    aliases: Mapping[str, tuple[str, ...]]
    include_language: bool = False
    iterative_draft: bool = False


PROMPT_VARIABLE_SCHEMAS: Mapping[PromptKey, PromptVariableSchema] = {
    PromptKey.FLUID_PROSE: PromptVariableSchema(
        key=PromptKey.FLUID_PROSE,
        aliases={_KEY_RAW_TEXT: (_KEY_RAW_TEXT, _KEY_SOURCE_TEXT)},
        include_language=True,
    ),
    PromptKey.JUDGE_FLUID_PROSE: PromptVariableSchema(
        key=PromptKey.JUDGE_FLUID_PROSE,
        aliases={},
    ),
    PromptKey.GAP_FILLER: PromptVariableSchema(
        key=PromptKey.GAP_FILLER,
        aliases=_ITERATIVE_SOURCE_ALIASES,
        include_language=True,
        iterative_draft=True,
    ),
    PromptKey.JUDGE_GAP_FILLER: PromptVariableSchema(
        key=PromptKey.JUDGE_GAP_FILLER,
        aliases={},
    ),
    PromptKey.OLLAMA_CRITIQUE: PromptVariableSchema(
        key=PromptKey.OLLAMA_CRITIQUE,
        aliases={},
    ),
    PromptKey.LONG_EXPANDER: PromptVariableSchema(
        key=PromptKey.LONG_EXPANDER,
        aliases=_ITERATIVE_SOURCE_ALIASES,
        include_language=True,
        iterative_draft=True,
    ),
    PromptKey.JUDGE_LONG_EXPANDER: PromptVariableSchema(
        key=PromptKey.JUDGE_LONG_EXPANDER,
        aliases={},
    ),
    PromptKey.WIDE_EXPANDER: PromptVariableSchema(
        key=PromptKey.WIDE_EXPANDER,
        aliases=_ITERATIVE_SOURCE_ALIASES,
        include_language=True,
        iterative_draft=True,
    ),
    PromptKey.JUDGE_WIDE_EXPANDER: PromptVariableSchema(
        key=PromptKey.JUDGE_WIDE_EXPANDER,
        aliases={},
    ),
    PromptKey.RAW_INDEX_SUMMARY: PromptVariableSchema(
        key=PromptKey.RAW_INDEX_SUMMARY,
        aliases=_CONTENT_TITLE_ALIASES,
        include_language=True,
    ),
    PromptKey.JUDGE_RAW_INDEX_SUMMARY: PromptVariableSchema(
        key=PromptKey.JUDGE_RAW_INDEX_SUMMARY,
        aliases=_CONTENT_TITLE_ALIASES,
    ),
    PromptKey.RAW_INDEX_CONCEPTS: PromptVariableSchema(
        key=PromptKey.RAW_INDEX_CONCEPTS,
        aliases=_CONTENT_TITLE_ALIASES,
        include_language=True,
    ),
    PromptKey.JUDGE_RAW_INDEX_CONCEPTS: PromptVariableSchema(
        key=PromptKey.JUDGE_RAW_INDEX_CONCEPTS,
        aliases=_CONTENT_TITLE_ALIASES,
    ),
    PromptKey.RAW_INDEX_CONCEPTS_REWRITE: PromptVariableSchema(
        key=PromptKey.RAW_INDEX_CONCEPTS_REWRITE,
        aliases={},
        include_language=True,
    ),
    PromptKey.RAW_INDEX_SYNTHESIS: PromptVariableSchema(
        key=PromptKey.RAW_INDEX_SYNTHESIS,
        aliases=_CONTENT_TITLE_ALIASES,
        include_language=True,
    ),
    PromptKey.JUDGE_RAW_INDEX_SYNTHESIS: PromptVariableSchema(
        key=PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
        aliases={
            _KEY_CONTENT_TITLE: (_KEY_CONTENT_TITLE, _KEY_TITLE),
            _KEY_SUMMARY: (_KEY_SUMMARY, _KEY_TRANSCRIPT_EXCERPT),
        },
    ),
    PromptKey.ATOMIC_INVENTORY: PromptVariableSchema(
        key=PromptKey.ATOMIC_INVENTORY,
        aliases=_CONTENT_TITLE_ALIASES,
    ),
    PromptKey.JUDGE_ATOMIC_INVENTORY: PromptVariableSchema(
        key=PromptKey.JUDGE_ATOMIC_INVENTORY,
        aliases=_CONTENT_TITLE_ALIASES,
    ),
    PromptKey.ATOMIC_BATCH: PromptVariableSchema(
        key=PromptKey.ATOMIC_BATCH,
        aliases=_CONTENT_TITLE_ALIASES,
    ),
    PromptKey.RECONCILE_MOCS: PromptVariableSchema(
        key=PromptKey.RECONCILE_MOCS,
        aliases={},
    ),
}

if set(PROMPT_VARIABLE_SCHEMAS.keys()) != set(PromptKey):
    missing = sorted(k.value for k in set(PromptKey) - set(PROMPT_VARIABLE_SCHEMAS.keys()))
    raise RuntimeError(f"PROMPT_VARIABLE_SCHEMAS missing PromptKey entries: {missing}")


def _coerce_value(value: Any) -> str:
    """Convert runtime context values into strings."""
    return str(value)


def normalize_prompt_context(
    key: PromptKey,
    context: Mapping[str, Any],
    *,
    default_language: str = DEFAULT_LANGUAGE,
) -> dict[str, str]:
    """Normalize runtime context identically for JsonPromptProvider and LangfusePromptProvider.

    Args:
        key: Canonical prompt key being rendered or compiled.
        context: Caller-supplied keyword arguments (may include Domain VOs like ``ChannelName``).
        default_language: Fallback output language when ``language`` is omitted or empty.

    Returns:
        Normalized ``dict[str, str]`` ready for Mustache substitution or Langfuse compilation.
    """
    schema = PROMPT_VARIABLE_SCHEMAS[key]
    normalized: dict[str, str] = {}

    for raw_k, raw_v in context.items():
        if raw_v is None:
            continue
        normalized[str(raw_k)] = _coerce_value(raw_v)

    for canonical_key, candidates in schema.aliases.items():
        if normalized.get(canonical_key):
            continue
        for candidate in candidates:
            val = normalized.get(candidate)
            if val:
                normalized[canonical_key] = val
                break

    if schema.include_language:
        raw_lang = normalized.get(_KEY_LANGUAGE, "").strip()
        normalized[_KEY_LANGUAGE] = raw_lang if raw_lang else default_language

    if schema.iterative_draft:
        raw_pass = context.get(_KEY_PASS_NUM)
        try:
            pass_num = int(raw_pass) if raw_pass is not None else _DEFAULT_PASS_NUM
        except (TypeError, ValueError):
            pass_num = _DEFAULT_PASS_NUM
        prev_pass_num = max(_MIN_PREV_PASS_NUM, pass_num - 1)
        normalized[_KEY_PREV_PASS_NUM] = str(prev_pass_num)
        current_text = normalized.get(_KEY_CURRENT_TEXT, "")
        normalized[_KEY_DRAFT_SECTION] = (
            f'\n<draft pass="{prev_pass_num}">\n{current_text}\n</draft>\n' if current_text else ""
        )

    return normalized
