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
from typing import Any

from cresmo.domain.value_objects import ChannelName, PromptKey

DEFAULT_LANGUAGE = "Português do Brasil"


@dataclass(frozen=True, slots=True)
class PromptVariableSchema:
    """Declarative normalization rules for a single PromptKey."""

    key: PromptKey
    aliases: Mapping[str, tuple[str, ...]]
    include_language: bool = False
    gap_filler_draft: bool = False


PROMPT_VARIABLE_SCHEMAS: Mapping[PromptKey, PromptVariableSchema] = {
    PromptKey.FLUID_PROSE: PromptVariableSchema(
        key=PromptKey.FLUID_PROSE,
        aliases={"raw_text": ("raw_text", "source_text")},
        include_language=True,
    ),
    PromptKey.JUDGE_FLUID_PROSE: PromptVariableSchema(
        key=PromptKey.JUDGE_FLUID_PROSE,
        aliases={},
    ),
    PromptKey.GAP_FILLER: PromptVariableSchema(
        key=PromptKey.GAP_FILLER,
        aliases={
            "raw_text": ("raw_text", "source_text"),
            "source_text": ("source_text", "raw_text"),
        },
        include_language=True,
        gap_filler_draft=True,
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
        aliases={},
    ),
    PromptKey.WIDE_EXPANDER: PromptVariableSchema(
        key=PromptKey.WIDE_EXPANDER,
        aliases={
            "current_text": ("current_text", "text"),
            "text": ("text", "current_text"),
        },
    ),
    PromptKey.RAW_INDEX_SUMMARY: PromptVariableSchema(
        key=PromptKey.RAW_INDEX_SUMMARY,
        aliases={"content_title": ("content_title", "title")},
        include_language=True,
    ),
    PromptKey.JUDGE_RAW_INDEX_SUMMARY: PromptVariableSchema(
        key=PromptKey.JUDGE_RAW_INDEX_SUMMARY,
        aliases={"content_title": ("content_title", "title")},
    ),
    PromptKey.RAW_INDEX_CONCEPTS: PromptVariableSchema(
        key=PromptKey.RAW_INDEX_CONCEPTS,
        aliases={"content_title": ("content_title", "title")},
        include_language=True,
    ),
    PromptKey.JUDGE_RAW_INDEX_CONCEPTS: PromptVariableSchema(
        key=PromptKey.JUDGE_RAW_INDEX_CONCEPTS,
        aliases={"content_title": ("content_title", "title")},
    ),
    PromptKey.RAW_INDEX_CONCEPTS_REWRITE: PromptVariableSchema(
        key=PromptKey.RAW_INDEX_CONCEPTS_REWRITE,
        aliases={},
        include_language=True,
    ),
    PromptKey.RAW_INDEX_SYNTHESIS: PromptVariableSchema(
        key=PromptKey.RAW_INDEX_SYNTHESIS,
        aliases={"content_title": ("content_title", "title")},
        include_language=True,
    ),
    PromptKey.JUDGE_RAW_INDEX_SYNTHESIS: PromptVariableSchema(
        key=PromptKey.JUDGE_RAW_INDEX_SYNTHESIS,
        aliases={
            "content_title": ("content_title", "title"),
            "summary": ("summary", "transcript_excerpt"),
        },
    ),
    PromptKey.ATOMIC_INVENTORY: PromptVariableSchema(
        key=PromptKey.ATOMIC_INVENTORY,
        aliases={"content_title": ("content_title", "title")},
    ),
    PromptKey.JUDGE_ATOMIC_INVENTORY: PromptVariableSchema(
        key=PromptKey.JUDGE_ATOMIC_INVENTORY,
        aliases={"content_title": ("content_title", "title")},
    ),
    PromptKey.ATOMIC_BATCH: PromptVariableSchema(
        key=PromptKey.ATOMIC_BATCH,
        aliases={"content_title": ("content_title", "title")},
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
    """Convert runtime context values (including ChannelName VOs) into strings."""
    if isinstance(value, ChannelName):
        return str(value)
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
        raw_lang = normalized.get("language", "").strip()
        normalized["language"] = raw_lang if raw_lang else default_language

    if schema.gap_filler_draft:
        raw_pass = context.get("pass_num")
        try:
            pass_num = int(raw_pass) if raw_pass is not None else 1
        except (TypeError, ValueError):
            pass_num = 1
        prev_pass_num = max(0, pass_num - 1)
        normalized["prev_pass_num"] = str(prev_pass_num)
        current_text = normalized.get("current_text", "")
        normalized["draft_section"] = (
            f'\n<draft pass="{prev_pass_num}">\n{current_text}\n</draft>\n' if current_text else ""
        )

    return normalized
