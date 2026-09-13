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

        for p in range(passes):
            prompt = (
                f"You are a senior analyst executing the Cresmo Socratic gap expansion and detranscription pipeline (Pass {p + 1}/{passes}).\n"
                f"Transform the following spoken transcript into a dense, continuous, formal Markdown compendium written in Brazilian Portuguese:\n\n"
                f"Source Channel: {raw_transcript.channel_name}\n\n"
                f"Transcript:\n{current_text}\n\n"
                "MANDATORY STRUCTURAL AND FORMATTING RULES:\n"
                "1. Line 1 MUST begin with a top-level heading: # <Title of Compendium>\n"
                "2. The main body must be written in continuous, highly informative fluid Markdown prose using analytical headings (## and ###).\n"
                "3. Strict Bans: Absolutely NO bullet lists, NO numbered lists in the main body, NO markdown tables, NO oralities/speech filler words, and NO em-dashes (—).\n"
                "4. MANDATORY SECTION: You MUST conclude the document with the following exact heading:\n"
                "## Informações Complementares\n"
                "Under this heading, provide detailed numbered paragraphs containing: historical context, verified dates, mini-biographies, statistical data, and secondary conceptual gap expansions."
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
