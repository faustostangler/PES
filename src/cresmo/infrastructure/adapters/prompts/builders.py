"""Prompt builder functions and dispatch registry for JsonPromptProvider.

Decouples template assembly and payload formatting from the adapter shell.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol, overload, runtime_checkable

from cresmo.domain.value_objects import ChannelName, ChatPrompt
from cresmo.infrastructure.adapters.prompts.registry import PromptKey
from cresmo.infrastructure.config import CresmoSettings


def _resolve_language(provider: Any, context: dict[str, Any]) -> str:
    """Resolve target language adhering to SSOT configuration hierarchy.

    Order of precedence:
    1. Explicit execution context override ('language' key in context).
    2. Injected provider configured language (provider.language).
    3. Provider settings configured language (provider.settings.language).
    4. SSOT infrastructure fallback (CresmoSettings.DEFAULT_LANGUAGE).
    """
    return (
        context.get("language")
        or getattr(provider, "language", None)
        or getattr(getattr(provider, "settings", None), "language", None)
        or CresmoSettings.DEFAULT_LANGUAGE
    )


def _resolve_content_title(context: dict[str, Any]) -> str:
    """Resolve canonical content title adhering to ADR-034 Cognitive Parity."""
    return str(context.get("content_title") or context.get("title") or "")


def build_raw_index_summary(provider: Any, **context: Any) -> ChatPrompt:
    return provider._format_paired_prompt(
        PromptKey.RAW_INDEX_SUMMARY.value,
        content_title=_resolve_content_title(context),
        transcript_excerpt=context.get("transcript_excerpt", ""),
        language=_resolve_language(provider, context),
    )


def build_raw_index_concepts(provider: Any, **context: Any) -> ChatPrompt:
    return provider._format_paired_prompt(
        PromptKey.RAW_INDEX_CONCEPTS.value,
        content_title=_resolve_content_title(context),
        transcript_excerpt=context.get("transcript_excerpt", ""),
        language=_resolve_language(provider, context),
    )


def build_raw_index_concepts_rewrite(provider: Any, **context: Any) -> ChatPrompt:
    lang = _resolve_language(provider, context)
    return provider._format_single_prompt(
        PromptKey.RAW_INDEX_CONCEPTS_REWRITE.value,
        previous_output=context.get("previous_output", ""),
        language=lang,
        language_upper=lang.upper(),
    )


def build_raw_index_synthesis(provider: Any, **context: Any) -> ChatPrompt:
    return provider._format_paired_prompt(
        PromptKey.RAW_INDEX_SYNTHESIS.value,
        channel_name=context.get("channel_name", ""),
        content_title=_resolve_content_title(context),
        summary=context.get("summary", ""),
        language=_resolve_language(provider, context),
    )


def build_judge_raw_index_summary(provider: Any, **context: Any) -> ChatPrompt:
    return provider._format_paired_prompt(
        PromptKey.JUDGE_RAW_INDEX_SUMMARY.value,
        content_title=_resolve_content_title(context),
        transcript_excerpt=context.get("transcript_excerpt", ""),
        summary=context.get("summary", ""),
        language=_resolve_language(provider, context),
    )


def build_judge_raw_index_concepts(provider: Any, **context: Any) -> ChatPrompt:
    return provider._format_paired_prompt(
        PromptKey.JUDGE_RAW_INDEX_CONCEPTS.value,
        content_title=_resolve_content_title(context),
        transcript_excerpt=context.get("transcript_excerpt", ""),
        concepts=context.get("concepts", ""),
        language=_resolve_language(provider, context),
    )


def build_judge_raw_index_synthesis(provider: Any, **context: Any) -> ChatPrompt:
    transcript_excerpt = context.get("transcript_excerpt", "")
    return provider._format_paired_prompt(
        PromptKey.JUDGE_RAW_INDEX_SYNTHESIS.value,
        content_title=_resolve_content_title(context),
        transcript_excerpt=transcript_excerpt,
        summary=transcript_excerpt,
        synthesis=context.get("synthesis", ""),
        language=_resolve_language(provider, context),
    )


def build_fluid_prose(provider: Any, **context: Any) -> ChatPrompt:
    key = PromptKey.FLUID_PROSE.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-fluid-prose")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    channel_name = context.get("channel_name", "")
    file_name = context.get("file_name", "")
    raw_text = context.get("raw_text", "")
    language = _resolve_language(provider, context)

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Source Channel: {channel_name}\n"
            f"File: {file_name}\n\n"
            f"Transcript:\n{raw_text}\n\n"
            "Transform raw transcript into clean, continuous fluid prose in third-person neutral narrative without conversational noise."
        )
        return ChatPrompt.from_system_and_user(user=user_p, system=sys_inst if sys_inst else None)

    return provider._format_paired_prompt(
        key,
        channel_name=channel_name,
        file_name=file_name,
        raw_text=raw_text,
        language=language,
    )


def build_gap_filler_pass1(provider: Any, **context: Any) -> ChatPrompt:
    key = PromptKey.GAP_FILLER_PASS1.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-gap-filler")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    channel_name = context.get("channel_name", "")
    file_name = context.get("file_name", "")
    raw_text = context.get("raw_text", "")
    total_passes = context.get("total_passes", 1)

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Source Channel: {channel_name}\n"
            f"File: {file_name}\n\n"
            f"Transcript:\n{raw_text}\n\n"
            "Transform into continuous fluid Markdown prose with analytical headings (## and ###) "
            "and mandatory '## Informações Complementares' section."
        )
        return ChatPrompt.from_system_and_user(user=user_p, system=sys_inst if sys_inst else None)

    return provider._format_paired_prompt(
        key,
        total_passes=total_passes,
        channel_name=channel_name,
        file_name=file_name,
        raw_text=raw_text,
    )


def build_gap_filler_subsequent(provider: Any, **context: Any) -> ChatPrompt:
    key = PromptKey.GAP_FILLER_PASS_SUBSEQUENT.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-expander")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    pass_num = context.get("pass_num", 2)
    total_passes = context.get("total_passes", 2)
    channel_name = context.get("channel_name", "")
    raw_text = context.get("raw_text", "")
    current_text = context.get("current_text")
    prev_draft = current_text if current_text is not None else raw_text

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Source Channel: {channel_name}\n\n"
            f"--- ORIGINAL RAW TRANSCRIPT (GROUND TRUTH REFERENCE) ---\n{raw_text}\n\n"
            f"--- PREVIOUS PASS EXPANDED COMPENDIUM DRAFT (PASS {pass_num - 1} TO ENRICH) ---\n{prev_draft}\n\n"
            "Execute Socratic gap filling and theoretical densification."
        )
        return ChatPrompt.from_system_and_user(user=user_p, system=sys_inst if sys_inst else None)

    return provider._format_paired_prompt(
        key,
        pass_num=pass_num,
        total_passes=total_passes,
        prev_pass_num=pass_num - 1,
        channel_name=channel_name,
        raw_text=raw_text,
        current_text=prev_draft,
    )


def build_long_expander(provider: Any, **context: Any) -> ChatPrompt:
    key = PromptKey.LONG_EXPANDER.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-long-expander")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    compendium_body = context.get("compendium_body", "")
    complementary_info = context.get("complementary_info", "")

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Content:\n{compendium_body}\n\n## Informações Complementares\n{complementary_info}"
        )
        return ChatPrompt.from_system_and_user(user=user_p, system=sys_inst if sys_inst else None)

    return provider._format_paired_prompt(
        key,
        compendium_body=compendium_body,
        complementary_info=complementary_info,
    )


def build_wide_expander(provider: Any, **context: Any) -> ChatPrompt:
    key = PromptKey.WIDE_EXPANDER.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-wide-expander")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    current_text = context.get("current_text", "")

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        return ChatPrompt.from_system_and_user(user=current_text, system=sys_inst if sys_inst else None)

    return provider._format_paired_prompt(
        key,
        current_text=current_text,
        text=current_text,
    )


def build_atomic_inventory(provider: Any, **context: Any) -> ChatPrompt:
    key = PromptKey.ATOMIC_INVENTORY.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-atomic")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    content_title = _resolve_content_title(context)
    channel_name = context.get("channel_name", "")
    compendium_body = context.get("compendium_body", "")

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Title: {content_title}\n"
            f"Channel: {channel_name}\n\n"
            f"Content:\n{compendium_body}\n\n"
            'Output strictly a JSON array: [{"title": "...", "type": "entity|concept|event|process"}]'
        )
        return ChatPrompt.from_system_and_user(user=user_p, system=sys_inst if sys_inst else None)

    return provider._format_paired_prompt(
        key,
        content_title=content_title,
        channel_name=channel_name,
        compendium_body=compendium_body,
    )


def build_judge_atomic_inventory(provider: Any, **context: Any) -> ChatPrompt:
    channel_name = context.get("channel_name", "")
    ch_str = channel_name.value if isinstance(channel_name, ChannelName) else channel_name
    return provider._format_paired_prompt(
        PromptKey.JUDGE_ATOMIC_INVENTORY.value,
        content_title=_resolve_content_title(context),
        channel_name=ch_str,
        compendium_body=context.get("compendium_body", ""),
        inventory_json=context.get("inventory_json", ""),
    )


def build_atomic_batch(provider: Any, **context: Any) -> ChatPrompt:
    key = PromptKey.ATOMIC_BATCH.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-atomic")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    content_title = _resolve_content_title(context)
    channel_name = context.get("channel_name", "")
    compendium_body = context.get("compendium_body", "")
    targets_json = context.get("targets_json", "")

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Source Compendium Title: {content_title}\n"
            f"Source Channel: {channel_name}\n\n"
            f"Source Context:\n{compendium_body}\n\n"
            f"Target Entities to Synthesize in this batch:\n{targets_json}\n\n"
            "Output strictly a JSON array of note objects."
        )
        return ChatPrompt.from_system_and_user(user=user_p, system=sys_inst if sys_inst else None)

    return provider._format_paired_prompt(
        key,
        content_title=content_title,
        channel_name=channel_name,
        compendium_body=compendium_body,
        targets_json=targets_json,
    )


def build_reconcile_mocs(provider: Any, **context: Any) -> ChatPrompt:
    key = PromptKey.RECONCILE_MOCS.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-moc-manager")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    notes_json = context.get("notes_json", "")

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Atomic Notes in Vault:\n{notes_json}\n\nOutput strictly a JSON array of MOC objects."
        )
        return ChatPrompt.from_system_and_user(user=user_p, system=sys_inst if sys_inst else None)

    return provider._format_paired_prompt(
        key,
        notes_json=notes_json,
    )


def build_llm_judge(provider: Any, **context: Any) -> ChatPrompt:
    return provider._format_paired_prompt(
        PromptKey.LLM_JUDGE.value,
        stage_name=context.get("stage_name", ""),
        criteria_json=context.get("criteria_json", "[]"),
        source_text=context.get("source_text", ""),
        candidate_text=context.get("candidate_text", ""),
    )


def build_ollama_critique(provider: Any, **context: Any) -> ChatPrompt:
    return provider._format_paired_prompt(
        PromptKey.OLLAMA_CRITIQUE.value,
        stage_name=context.get("stage_name", ""),
        overall_score=context.get("overall_score", ""),
        criteria_failures=context.get("criteria_failures", ""),
    )


@runtime_checkable
class PromptBuilder(Protocol):
    """First-class callable signature for prompt formatting builders.

    Args:
        provider: Enclosing prompt provider adapter instance.
        **context: Keyword arguments for prompt formatting.

    Returns:
        ChatPrompt domain value object.
    """

    def __call__(self, provider: Any, /, **context: Any) -> ChatPrompt: ...


@dataclass
class PromptBuilderRegistry:
    """First-class typed registry managing prompt builder functions by PromptKey.

    Enforces:
    - Type safety (PromptKey -> PromptBuilder callable)
    - Fail-fast lookup with descriptive errors
    - Introspection, completeness checks, and runtime immutability (freezing)
    - High cohesion within the prompt infrastructure layer
    """

    _builders: dict[PromptKey, PromptBuilder] = field(default_factory=dict)
    _frozen: bool = False

    @overload
    def register(self, key: PromptKey, builder: PromptBuilder) -> None: ...

    @overload
    def register(
        self, key: PromptKey, builder: None = None
    ) -> Callable[[PromptBuilder], PromptBuilder]: ...

    def register(
        self,
        key: PromptKey,
        builder: PromptBuilder | None = None,
    ) -> Callable[[PromptBuilder], PromptBuilder] | None:
        """Register a builder function directly or as a decorator.

        Args:
            key: Canonical PromptKey to register.
            builder: Optional PromptBuilder callable. If omitted, returns a decorator.

        Returns:
            Decorator callable if builder was None, otherwise None.

        Raises:
            RuntimeError: If attempting to register on a frozen registry.
        """
        if self._frozen:
            raise RuntimeError("Cannot register builders on a frozen PromptBuilderRegistry.")

        if builder is not None:
            self._builders[key] = builder
            return None

        def decorator(fn: PromptBuilder) -> PromptBuilder:
            if self._frozen:
                raise RuntimeError("Cannot register builders on a frozen PromptBuilderRegistry.")
            self._builders[key] = fn
            return fn

        return decorator

    def get(self, key: PromptKey) -> PromptBuilder:
        """Retrieve the builder associated with key, raising ValueError if unsupported."""
        builder = self._builders.get(key)
        if builder is None:
            raise ValueError(f"Unsupported prompt key: {key}")
        return builder

    def __getitem__(self, key: PromptKey) -> PromptBuilder:
        return self.get(key)

    def __contains__(self, key: PromptKey) -> bool:
        return key in self._builders

    def __len__(self) -> int:
        return len(self._builders)

    def __iter__(self) -> Iterator[PromptKey]:
        return iter(self._builders)

    def keys(self) -> frozenset[PromptKey]:
        return frozenset(self._builders.keys())

    def freeze(self) -> PromptBuilderRegistry:
        """Freeze the registry to prevent subsequent mutations."""
        self._frozen = True
        return self

    @property
    def is_frozen(self) -> bool:
        return self._frozen

    def validate_completeness(self, expected_keys: Iterable[PromptKey] | None = None) -> None:
        """Verify all expected PromptKeys have registered builders.

        Raises:
            ValueError: If any expected PromptKey is missing.
        """
        targets = expected_keys if expected_keys is not None else PromptKey
        missing = [k for k in targets if k not in self._builders]
        if missing:
            raise ValueError(f"Missing prompt builders for keys: {missing}")


def create_default_prompt_builder_registry() -> PromptBuilderRegistry:
    """Instantiate, populate, validate, and freeze the canonical PromptBuilderRegistry."""
    registry = PromptBuilderRegistry()
    registry.register(PromptKey.FLUID_PROSE, build_fluid_prose)
    registry.register(PromptKey.GAP_FILLER_PASS1, build_gap_filler_pass1)
    registry.register(PromptKey.GAP_FILLER_PASS_SUBSEQUENT, build_gap_filler_subsequent)
    registry.register(PromptKey.LONG_EXPANDER, build_long_expander)
    registry.register(PromptKey.WIDE_EXPANDER, build_wide_expander)
    registry.register(PromptKey.ATOMIC_INVENTORY, build_atomic_inventory)
    registry.register(PromptKey.JUDGE_ATOMIC_INVENTORY, build_judge_atomic_inventory)
    registry.register(PromptKey.ATOMIC_BATCH, build_atomic_batch)
    registry.register(PromptKey.RECONCILE_MOCS, build_reconcile_mocs)
    registry.register(PromptKey.RAW_INDEX_SUMMARY, build_raw_index_summary)
    registry.register(PromptKey.RAW_INDEX_CONCEPTS, build_raw_index_concepts)
    registry.register(PromptKey.RAW_INDEX_CONCEPTS_REWRITE, build_raw_index_concepts_rewrite)
    registry.register(PromptKey.RAW_INDEX_SYNTHESIS, build_raw_index_synthesis)
    registry.register(PromptKey.JUDGE_RAW_INDEX_SUMMARY, build_judge_raw_index_summary)
    registry.register(PromptKey.JUDGE_RAW_INDEX_CONCEPTS, build_judge_raw_index_concepts)
    registry.register(PromptKey.JUDGE_RAW_INDEX_SYNTHESIS, build_judge_raw_index_synthesis)
    registry.register(PromptKey.LLM_JUDGE, build_llm_judge)
    registry.register(PromptKey.OLLAMA_CRITIQUE, build_ollama_critique)

    registry.validate_completeness()
    registry.freeze()
    return registry


PROMPT_BUILDER_REGISTRY: PromptBuilderRegistry = create_default_prompt_builder_registry()
