"""Stage 2 Use Case: Fill Gaps and Expand Fluid Prose.

Executes Socratic audit and multi-pass fluid prose expansion (cresmo-expander).
"""

from __future__ import annotations

import re

from cresmo.application.ports import LLMTransformationPort, VaultRepositoryPort
from cresmo.domain.entities import EnrichedCompendium, RawTranscript
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import NoteTitle

_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_TAG = "## Informações Complementares"


class FillGapsFluidProseUseCase:
    """Stage 2: Multi-pass Socratic gap analysis & fluid prose expansion."""

    def __init__(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port

    def execute(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        prompt = f"Perform Socratic enrichment on transcript:\n{current_text}"

        for _ in range(passes):
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info
        if _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            # Strip the leading # Title line from body if present
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium
