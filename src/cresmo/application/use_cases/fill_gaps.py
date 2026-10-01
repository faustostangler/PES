"""Use Case: Fill Gaps and Expand Fluid Prose.

Executes Socratic audit and multi-pass progressive fluid prose expansion (cresmo-expander),
purging oralities and speech noise while enforcing continuous narrative structure.

Conforms to:
- SPEC-001: §1 (Gap Filler Socratic Expansion)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import re

from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpPromptProviderPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import (
    EnrichedCompendium,
    FluidTranscript,
    PipelineSessionId,
    UserIdentity,
)
from cresmo.domain.exceptions import CompendiumStructureError, DomainValidationError
from cresmo.domain.value_objects import NoteTitle, PromptKey

# Extracts title from markdown H1 header
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_TAG = "## Informações Complementares"
# Resilient regex matching variations of the mandatory complementary section header
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


class FillGapsUseCase:
    """Multi-pass Socratic gap analysis & epistemic compendium expansion orchestrator."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with required ports.

        Args:
            llm_synthesis_port: Hexagonal port for generative text transformations.
            vault_port: Port providing enriched compendium persistence.
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for fluid prose generation.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        if vault_port is None:
            raise ValueError("vault_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.temperature = temperature
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()

    def execute(
        self,
        fluid_transcript: FluidTranscript,
        passes: int = 3,
        user: UserIdentity | None = None,
    ) -> EnrichedCompendium:
        """Execute multi-pass progressive Socratic gap enrichment on fluid prose.

        Args:
            fluid_transcript: Source FluidTranscript aggregate with normalized prose.
            passes: Number of sequential Socratic expansion cycles (default: 3).
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            Validated EnrichedCompendium aggregate with segregated body and complementary info.

        Raises:
            CompendiumStructureError: If the mandatory complementary info section is missing or empty.
            DomainValidationError: If input is not a FluidTranscript or invariants are violated.
        """
        if not isinstance(fluid_transcript, FluidTranscript):
            raise DomainValidationError(
                f"FillGapsUseCase strictly requires FluidTranscript, got: {type(fluid_transcript).__name__}"
            )

        current_text = fluid_transcript.body
        file_name = f"{fluid_transcript.content_id.value}.txt"

        session_id = PipelineSessionId.create(
            channel=fluid_transcript.channel_name,
            content_id=fluid_transcript.content_id,
            channel_id=fluid_transcript.channel_id,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value

        for pass_index in range(passes):
            prompt_key = (
                PromptKey.GAP_FILLER_PASS1
                if pass_index == 0
                else PromptKey.GAP_FILLER_PASS_SUBSEQUENT
            )
            system_instruction, user_prompt = self.prompt_provider.get_prompt(
                prompt_key,
                pass_num=pass_index + 1,
                total_passes=passes,
                channel_name=fluid_transcript.channel_name,
                file_name=file_name,
                raw_text=fluid_transcript.body,
                current_text=current_text if pass_index > 0 else None,
            )
            current_text = self.llm_synthesis_port.transform(
                prompt=user_prompt,
                system_instruction=system_instruction,
                temperature=self.temperature,
                trace_id=f"{fluid_transcript.content_id.value}_gap_fill_pass_{pass_index + 1}",
                session_id=session_id,
                user_id=user_id,
            )

        # Extract title from H1 or fallback to transcript title
        title_match = _TITLE_H1_PATTERN.search(current_text)
        if title_match:
            extracted_title = title_match.group(1).strip()
        else:
            extracted_title = fluid_transcript.title or "Untitled Compendium"

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

        pub_date = fluid_transcript.publication_date
        video_date = pub_date.strftime("%Y%m%d") if pub_date else ""
        compendium = EnrichedCompendium(
            content_id=fluid_transcript.content_id,
            channel_name=fluid_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=complementary_information,
            pass_count=passes,
            channel_id=fluid_transcript.channel_id,
            channel_category=fluid_transcript.channel_category,
            source_url=fluid_transcript.source_url,
            publication_date=pub_date,
            video_date=video_date,
            video_description=fluid_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium
