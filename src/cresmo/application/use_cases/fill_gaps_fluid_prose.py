"""Stage 2 Use Case: Fill Gaps and Expand Fluid Prose.

Executes Socratic audit and multi-pass progressive fluid prose expansion (cresmo-expander),
purging oralities and speech noise while enforcing continuous narrative structure.

Conforms to:
- SPEC-001: §1 (Stage 2 Gap Filler Socratic Expansion)
- ADR-001: Modular Monolith Domain Integrity
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

# Extracts title from markdown H1 header
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_TAG = "## Informações Complementares"
# Resilient regex matching variations of the mandatory complementary section header
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


class FillGapsFluidProseUseCase:
    """Stage 2: Multi-pass Socratic gap analysis & fluid prose expansion orchestrator."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort | None = None,
        vault_port: VaultRepositoryPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
        *,
        llm_port: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize Stage 2 use case with required ports.

        Args:
            llm_synthesis_port: Hexagonal port for generative text transformations.
            vault_port: Port providing enriched compendium persistence.
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for fluid prose generation.
            llm_port: Backward-compatible alias for llm_synthesis_port.
        """
        port = llm_synthesis_port or llm_port
        if port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = port
        self.llm_port = port  # Backward compatibility
        self.vault_port = vault_port
        self.temperature = temperature
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
        """Execute Stage 2 multi-pass progressive enrichment.

        Args:
            raw_transcript: Source RawTranscript aggregate from Stage 1.
            passes: Number of sequential Socratic expansion cycles (default: 3).

        Returns:
            Validated EnrichedCompendium aggregate with segregated body and complementary info.

        Raises:
            CompendiumStructureError: If the mandatory complementary info section is missing or empty.
            DomainValidationError: If construction invariants are violated.
        """
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for pass_index in range(passes):
            system_instruction, user_prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=pass_index + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if pass_index > 0 else None,
            )
            current_text = self.llm_synthesis_port.transform(
                prompt=user_prompt,
                system_instruction=system_instruction,
                temperature=self.temperature,
                trace_id=f"{raw_transcript.content_id.value}_gap_fill_pass_{pass_index + 1}",
                session_id=f"stage2_fluid_prose_{raw_transcript.channel_name}",
                user_id=str(raw_transcript.channel_name),
            )

        # Extract title from H1 or fallback to raw title
        title_match = _TITLE_H1_PATTERN.search(current_text)
        if title_match:
            extracted_title = title_match.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        complementary_match = _COMPLEMENTARY_REGEX.search(current_text)
        if complementary_match:
            body = current_text[: complementary_match.start()].strip()
            complementary_information = current_text[complementary_match.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            complementary_information = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not complementary_information:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        pub_date = raw_transcript.publication_date
        video_date = pub_date.strftime("%Y%m%d") if pub_date else ""
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=complementary_information,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            publication_date=pub_date,
            video_date=video_date,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium
