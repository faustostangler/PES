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
    PipelineSessionId,
    StageTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CompendiumStructureError, DomainValidationError
from cresmo.domain.value_objects import Content, PromptKey

# Extracts title from markdown H1 header
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_TAG = "### Extra Info"
# Resilient regex matching variations of the mandatory complementary section header
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Extra\s+Info|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
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
        fluid_transcript: StageTranscript,
        passes: int = 3,
        user: UserIdentity | None = None,
    ) -> StageTranscript:
        """Execute multi-pass progressive Socratic gap enrichment on fluid prose.

        Args:
            fluid_transcript: Source StageTranscript aggregate with normalized prose.
            passes: Number of sequential Socratic expansion cycles (default: 3).
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            Validated StageTranscript aggregate with segregated body and complementary info.

        Raises:
            CompendiumStructureError: If the mandatory complementary info section is missing or empty.
            DomainValidationError: If input is not a StageTranscript or invariants are violated.
        """
        if not isinstance(fluid_transcript, StageTranscript):
            raise DomainValidationError(
                f"FillGapsUseCase strictly requires StageTranscript, got: {type(fluid_transcript).__name__}"
            )

        file_name = f"{fluid_transcript.content.id.value}.txt"

        session_id = PipelineSessionId.create(
            channel=fluid_transcript.channel,
            content_id=fluid_transcript.content,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value

        # Pass 1: Initial Socratic gap filling
        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.GAP_FILLER,
            pass_num=1,
            total_passes=passes,
            channel_name=fluid_transcript.channel.name,
            file_name=file_name,
            raw_text=fluid_transcript.content.text,
            current_text=None,
        )
        current_text = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{fluid_transcript.content.id.value}_gap_fill_pass_1",
            session_id=session_id,
            user_id=user_id,
        )

        # Subsequent passes: Progressive enrichment over current text
        for pass_index in range(1, passes):
            chat_prompt = self.prompt_provider.get_prompt(
                PromptKey.GAP_FILLER,
                pass_num=pass_index + 1,
                total_passes=passes,
                channel_name=fluid_transcript.channel.name,
                file_name=file_name,
                raw_text=fluid_transcript.content.text,
                current_text=current_text,
            )
            current_text = self.llm_synthesis_port.transform(
                prompt=chat_prompt,
                temperature=self.temperature,
                trace_id=f"{fluid_transcript.content.id.value}_gap_fill_pass_{pass_index + 1}",
                session_id=session_id,
                user_id=user_id,
            )

        # Extract title from H1 or fallback to transcript title
        title_match = _TITLE_H1_PATTERN.search(current_text)
        if title_match:
            extracted_title = title_match.group(1).strip()
        else:
            extracted_title = fluid_transcript.content.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        complementary_match = _COMPLEMENTARY_REGEX.search(current_text)
        if complementary_match:
            body = current_text[: complementary_match.start()].strip()
            complementary_information = current_text[complementary_match.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not complementary_information:
            raise CompendiumStructureError(
                "StageTranscript must contain a non-empty 'Extra Info' section."
            )

        full_body = f"{body}\n\n### Extra Info\n\n{complementary_information}"

        compendium = StageTranscript(
            channel=fluid_transcript.channel,
            provenance=fluid_transcript.provenance,
            content=Content.create(
                id=fluid_transcript.content.id,
                title=extracted_title,
                body=full_body,
            ),
            pass_count=passes,
            metadata=dict(fluid_transcript.metadata),
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium
