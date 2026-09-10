"""Stage 3 Use Case: Longitudinal & Synchronic Expansion.

Executes Braudelian longue durée (cresmo-long-expander) and Jaspers Axial Time (cresmo-wide-expander)
deep multi-secular and horizontal cross-sections.
"""

from __future__ import annotations

from cresmo.application.ports import LLMTransformationPort, VaultRepositoryPort
from cresmo.domain.entities import EnrichedCompendium
from cresmo.domain.exceptions import CompendiumStructureError

_COMPLEMENTARY_TAG = "## Informações Complementares"


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
        prompt_long = f"Execute Braudelian longitudinal expansion on:\n{compendium.body}"
        res_long = self.llm_port.transform(prompt=prompt_long)

        prompt_wide = f"Execute Jaspers synchronic expansion on:\n{res_long}"
        res_wide = self.llm_port.transform(prompt=prompt_wide)

        if _COMPLEMENTARY_TAG in res_wide:
            parts = res_wide.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            comp_info = parts[1].strip()
        else:
            body = res_wide.strip()
            comp_info = compendium.complementary_info

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
