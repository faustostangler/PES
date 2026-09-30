"""Prompt builder functions and dispatch registry for JsonPromptProvider.

Decouples template assembly and payload formatting from the adapter shell.
"""

from __future__ import annotations

from typing import Any

from cresmo.domain.value_objects import ChannelName
from cresmo.infrastructure.adapters.prompts.registry import PromptKey


def build_raw_index_summary(provider: Any, **context: Any) -> tuple[str, str]:
    return provider._format_paired_prompt(
        PromptKey.RAW_INDEX_SUMMARY.value,
        video_title=context.get("video_title", ""),
        transcript_excerpt=context.get("transcript_excerpt", ""),
        language=context.get("language", "Português do Brasil"),
    )


def build_raw_index_concepts(provider: Any, **context: Any) -> tuple[str, str]:
    return provider._format_paired_prompt(
        PromptKey.RAW_INDEX_CONCEPTS.value,
        video_title=context.get("video_title", ""),
        transcript_excerpt=context.get("transcript_excerpt", ""),
        language=context.get("language", "Português do Brasil"),
    )


def build_raw_index_concepts_rewrite(provider: Any, **context: Any) -> tuple[str, str]:
    lang = context.get("language", "Português do Brasil")
    prompt_text = provider._format_single_prompt(
        PromptKey.RAW_INDEX_CONCEPTS_REWRITE.value,
        previous_output=context.get("previous_output", ""),
        language=lang,
        language_upper=lang.upper(),
    )
    return "", prompt_text


def build_raw_index_synthesis(provider: Any, **context: Any) -> tuple[str, str]:
    return provider._format_paired_prompt(
        PromptKey.RAW_INDEX_SYNTHESIS.value,
        video_title=context.get("video_title", ""),
        summary=context.get("summary", ""),
        language=context.get("language", "Português do Brasil"),
    )


def build_judge_raw_index_summary(provider: Any, **context: Any) -> tuple[str, str]:
    return provider._format_paired_prompt(
        PromptKey.JUDGE_RAW_INDEX_SUMMARY.value,
        video_title=context.get("video_title", ""),
        transcript_excerpt=context.get("transcript_excerpt", ""),
        summary=context.get("summary", ""),
        language=context.get("language", "Português do Brasil"),
    )


def build_judge_raw_index_concepts(provider: Any, **context: Any) -> tuple[str, str]:
    return provider._format_paired_prompt(
        PromptKey.JUDGE_RAW_INDEX_CONCEPTS.value,
        video_title=context.get("video_title", ""),
        transcript_excerpt=context.get("transcript_excerpt", ""),
        concepts=context.get("concepts", ""),
        language=context.get("language", "Português do Brasil"),
    )


def build_judge_raw_index_synthesis(provider: Any, **context: Any) -> tuple[str, str]:
    transcript_excerpt = context.get("transcript_excerpt", "")
    return provider._format_paired_prompt(
        PromptKey.JUDGE_RAW_INDEX_SYNTHESIS.value,
        video_title=context.get("video_title", ""),
        transcript_excerpt=transcript_excerpt,
        summary=transcript_excerpt,
        synthesis=context.get("synthesis", ""),
        language=context.get("language", "Português do Brasil"),
    )


def build_gap_filler_pass1(provider: Any, **context: Any) -> tuple[str, str]:
    key = PromptKey.GAP_FILLER_PASS1.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-expander")
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
        return sys_inst, user_p

    return provider._format_paired_prompt(
        key,
        total_passes=total_passes,
        channel_name=channel_name,
        file_name=file_name,
        raw_text=raw_text,
    )


def build_gap_filler_subsequent(provider: Any, **context: Any) -> tuple[str, str]:
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
        return sys_inst, user_p

    return provider._format_paired_prompt(
        key,
        pass_num=pass_num,
        total_passes=total_passes,
        prev_pass_num=pass_num - 1,
        channel_name=channel_name,
        raw_text=raw_text,
        current_text=prev_draft,
    )


def build_long_expander(provider: Any, **context: Any) -> tuple[str, str]:
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
        return sys_inst, user_p

    return provider._format_paired_prompt(
        key,
        compendium_body=compendium_body,
        complementary_info=complementary_info,
    )


def build_wide_expander(provider: Any, **context: Any) -> tuple[str, str]:
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
        return sys_inst, current_text

    return provider._format_paired_prompt(
        key,
        current_text=current_text,
        text=current_text,
    )


def build_atomic_inventory(provider: Any, **context: Any) -> tuple[str, str]:
    key = PromptKey.ATOMIC_INVENTORY.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-atomic")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    compendium_title = context.get("compendium_title", "")
    channel_name = context.get("channel_name", "")
    compendium_body = context.get("compendium_body", "")

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Title: {compendium_title}\n"
            f"Channel: {channel_name}\n\n"
            f"Content:\n{compendium_body}\n\n"
            'Output strictly a JSON array: [{"title": "...", "type": "entity|concept|event|process"}]'
        )
        return sys_inst, user_p

    return provider._format_paired_prompt(
        key,
        compendium_title=compendium_title,
        channel_name=channel_name,
        compendium_body=compendium_body,
    )


def build_judge_atomic_inventory(provider: Any, **context: Any) -> tuple[str, str]:
    channel_name = context.get("channel_name", "")
    ch_str = channel_name.value if isinstance(channel_name, ChannelName) else channel_name
    return provider._format_paired_prompt(
        PromptKey.JUDGE_ATOMIC_INVENTORY.value,
        compendium_title=context.get("compendium_title", ""),
        channel_name=ch_str,
        compendium_body=context.get("compendium_body", ""),
        inventory_json=context.get("inventory_json", ""),
    )


def build_atomic_batch(provider: Any, **context: Any) -> tuple[str, str]:
    key = PromptKey.ATOMIC_BATCH.value
    entry = provider._templates.get(key, {})
    task = entry.get("task", "")
    skill_name = entry.get("skill_name", "cresmo-atomic")
    template = entry.get("template", "")
    system_template = entry.get("system_instruction", "")
    skill_block = provider._get_skill_block(skill_name)
    compendium_title = context.get("compendium_title", "")
    channel_name = context.get("channel_name", "")
    compendium_body = context.get("compendium_body", "")
    targets_json = context.get("targets_json", "")

    if not template and not system_template:
        sys_inst = f"{task}\n\n{skill_block}".strip()
        user_p = (
            f"Source Compendium Title: {compendium_title}\n"
            f"Source Channel: {channel_name}\n\n"
            f"Source Context:\n{compendium_body}\n\n"
            f"Target Entities to Synthesize in this batch:\n{targets_json}\n\n"
            "Output strictly a JSON array of note objects."
        )
        return sys_inst, user_p

    return provider._format_paired_prompt(
        key,
        compendium_title=compendium_title,
        channel_name=channel_name,
        compendium_body=compendium_body,
        targets_json=targets_json,
    )


def build_reconcile_mocs(provider: Any, **context: Any) -> tuple[str, str]:
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
        return sys_inst, user_p

    return provider._format_paired_prompt(
        key,
        notes_json=notes_json,
    )


PROMPT_BUILDER_DISPATCH_MAP: dict[PromptKey, Any] = {
    PromptKey.GAP_FILLER_PASS1: build_gap_filler_pass1,
    PromptKey.GAP_FILLER_PASS_SUBSEQUENT: build_gap_filler_subsequent,
    PromptKey.LONG_EXPANDER: build_long_expander,
    PromptKey.WIDE_EXPANDER: build_wide_expander,
    PromptKey.ATOMIC_INVENTORY: build_atomic_inventory,
    PromptKey.JUDGE_ATOMIC_INVENTORY: build_judge_atomic_inventory,
    PromptKey.ATOMIC_BATCH: build_atomic_batch,
    PromptKey.RECONCILE_MOCS: build_reconcile_mocs,
    PromptKey.RAW_INDEX_SUMMARY: build_raw_index_summary,
    PromptKey.RAW_INDEX_CONCEPTS: build_raw_index_concepts,
    PromptKey.RAW_INDEX_CONCEPTS_REWRITE: build_raw_index_concepts_rewrite,
    PromptKey.RAW_INDEX_SYNTHESIS: build_raw_index_synthesis,
    PromptKey.JUDGE_RAW_INDEX_SUMMARY: build_judge_raw_index_summary,
    PromptKey.JUDGE_RAW_INDEX_CONCEPTS: build_judge_raw_index_concepts,
    PromptKey.JUDGE_RAW_INDEX_SYNTHESIS: build_judge_raw_index_synthesis,
}
