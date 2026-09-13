"""Stage 2 Use Case: Fill Gaps and Expand Fluid Prose.

Executes Socratic audit and multi-pass fluid prose expansion (cresmo-expander).
"""

from __future__ import annotations

import re

from cresmo.application.ports import (
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import EnrichedCompendium, RawTranscript
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import NoteTitle

_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_TAG = "## Informações Complementares"
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


class FillGapsFluidProseUseCase:
    """Stage 2: Multi-pass Socratic gap analysis & fluid prose expansion."""

    def __init__(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

    def execute(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d")
            if raw_transcript.upload_date
            else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium
