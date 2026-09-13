"""Stage 3 Use Case: Longitudinal & Synchronic Expansion.

Executes Braudelian longue durée (cresmo-long-expander) and Jaspers Axial Time (cresmo-wide-expander)
deep multi-secular and horizontal cross-sections.
"""

from __future__ import annotations

import re

from cresmo.application.ports import LLMTransformationPort, VaultRepositoryPort
from cresmo.domain.entities import EnrichedCompendium
from cresmo.domain.exceptions import CompendiumStructureError

_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_TAG = "## Informações Complementares"
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


class ExpandLongitudinalSynchronicUseCase:
    """Stage 3: Deep longitudinal & synchronic compendium expansion."""

    def __init__(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port

    def execute(
        self,
        compendium: EnrichedCompendium,
    ) -> EnrichedCompendium:
        """Execute Stage 3 dual expansion in-place."""
        prompt_long = (
            f"You are a senior analyst executing Braudelian longitudinal expansion (longue durée).\n"
            f"Deepen the multi-secular structural analysis, institutional permanence, and historical palimpsest of the following text in Brazilian Portuguese.\n"
            f"Preserve continuous fluid prose, analytical headings (## and ###), and the mandatory '## Informações Complementares' section.\n\n"
            f"Content:\n{compendium.body}\n\n"
            f"## Informações Complementares\n{compendium.complementary_info}"
        )
        res_long = self.llm_port.transform(prompt=prompt_long)

        prompt_wide = (
            f"You are a senior analyst executing Jaspers synchronic expansion (Axial Time and comparative civilizational networks).\n"
            f"Enrich the horizontal connectivity, global networks, and synchronized parallels of the following text in Brazilian Portuguese.\n"
            f"Preserve continuous fluid prose, analytical headings (## and ###), and the mandatory '## Informações Complementares' section.\n\n"
            f"{res_long}"
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
        )
        self.vault_port.save_enriched_compendium(updated)
        return updated
