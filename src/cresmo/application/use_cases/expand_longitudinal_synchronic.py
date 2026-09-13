"""Stage 3 Use Case: Longitudinal & Synchronic Expansion.

Executes Braudelian longue durée (cresmo-long-expander) and Jaspers Axial Time (cresmo-wide-expander)
deep multi-secular and horizontal cross-sections.
"""

from __future__ import annotations

import re

from cresmo.application.ports import (
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import EnrichedCompendium
from cresmo.domain.exceptions import CompendiumStructureError

_COMPLEMENTARY_TAG = "## Informações Complementares"
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+.+$", re.MULTILINE)


class ExpandLongitudinalSynchronicUseCase:
    """Stage 3: Deep longitudinal & synchronic expansion in-place."""

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
        compendium: EnrichedCompendium,
    ) -> EnrichedCompendium:
        """Execute Stage 3 dual expansion in-place."""
        prompt_long = self.prompt_provider.get_long_expander_prompt(
            compendium_body=compendium.body,
            complementary_info=compendium.complementary_info,
        )
        res_long = self.llm_port.transform(prompt=prompt_long)

        prompt_wide = self.prompt_provider.get_wide_expander_prompt(
            current_text=res_long,
        )
        res_wide = self.llm_port.transform(prompt=prompt_wide)

        m_comp = _COMPLEMENTARY_REGEX.search(res_wide)
        if m_comp:
            body = res_wide[: m_comp.start()].strip()
            comp_info = res_wide[m_comp.end() :].strip()
        elif _COMPLEMENTARY_TAG in res_wide:
            parts = res_wide.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            comp_info = parts[1].strip()
        else:
            body = res_wide.strip()
            comp_info = compendium.complementary_info

        # Strip any leading H1 # Title from body if generated
        body = _TITLE_H1_PATTERN.sub("", body).strip()

        if not comp_info:
            raise CompendiumStructureError("Missing complementary info in expansion.")

        updated = EnrichedCompendium(
            content_id=compendium.content_id,
            channel_name=compendium.channel_name,
            title=compendium.title,
            body=body,
            complementary_info=comp_info,
            pass_count=compendium.pass_count + 1,
            channel_id=compendium.channel_id,
            channel_category=compendium.channel_category,
            source_url=compendium.source_url,
            video_date=compendium.video_date,
            video_description=compendium.video_description,
        )
        self.vault_port.save_enriched_compendium(updated)
        return updated
