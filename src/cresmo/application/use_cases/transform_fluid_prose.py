"""Use Case: Transform Raw Transcript to Fluid Prose.

Executes linguistic detranscription into continuous, neutral third-person Markdown prose,
purging all marks of orality and conversational noise while verifying Named Entity (NER) spelling.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
- SPEC-011: Fluid Prose Detranscription and Gap Filler Decoupling Specification
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
    FluidTranscript,
    PipelineSessionId,
    SourceTranscript,
    UserIdentity,
)
from cresmo.domain.exceptions import CompendiumStructureError, DomainValidationError
from cresmo.domain.value_objects import CandidateText, PromptKey

# Matches Markdown H1 title header
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
# Matches any accidental complementary information section headers
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


def post_process_fluid_transcript(
    candidate: CandidateText | str,
    source: SourceTranscript,
) -> FluidTranscript:
    """Post-process candidate text into a validated FluidTranscript domain aggregate.

    Strips H1 headers to preserve clean heading hierarchy, removes accidental
    complementary sections, and maps provenance metadata from the source transcript.
    """
    current_text = (
        candidate.text.strip() if isinstance(candidate, CandidateText) else str(candidate).strip()
    )

    # Extract title from H1 if present, otherwise fall back to source transcript title
    title_match = _TITLE_H1_PATTERN.search(current_text)
    if title_match:
        extracted_title = title_match.group(1).strip()
        body = _TITLE_H1_PATTERN.sub("", current_text).strip()
    else:
        extracted_title = source.title or "Untitled Compendium"
        body = current_text

    # Purge any accidental complementary information section in Stage 1
    comp_match = _COMPLEMENTARY_REGEX.search(body)
    if comp_match:
        body = body[: comp_match.start()].strip()

    if not body:
        raise CompendiumStructureError(
            f"Generated fluid prose body is empty for '{source.content_id.value}'."
        )

    return FluidTranscript(
        content_id=source.content_id,
        channel_name=source.channel_name,
        body=body,
        title=extracted_title,
        source_url=source.source_url,
        publication_date=source.publication_date,
        upload_date=source.upload_date,
        channel_id=source.channel_id,
        channel_category=source.channel_category,
        video_description=source.video_description,
    )


class TransformFluidProseUseCase:
    """Orchestrator for linguistic detranscription into continuous fluid prose."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with required ports.

        Args:
            llm_synthesis_port: Hexagonal port for generative text transformations.
            vault_port: Optional port for persisting intermediate fluid transcripts.
            prompt_provider: Provider for prompt templates.
            temperature: Sampling temperature override for fluid prose generation.

        Raises:
            ValueError: If llm_synthesis_port is None.
        """
        if llm_synthesis_port is None:
            raise ValueError("llm_synthesis_port must be provided")
        self.llm_synthesis_port = llm_synthesis_port
        self.vault_port = vault_port
        self.prompt_provider: PromptProviderPort = prompt_provider or NoOpPromptProviderPort()
        self.temperature = temperature

    def execute(
        self,
        source_transcript: SourceTranscript,
        user: UserIdentity | None = None,
    ) -> FluidTranscript:
        """Execute linguistic detranscription on source spoken transcript.

        Args:
            source_transcript: Source SourceTranscript aggregate with verbatim spoken text.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            Validated FluidTranscript aggregate containing clean continuous narrative prose.

        Raises:
            DomainValidationError: If input is not a SourceTranscript or if generated body is empty.
            CompendiumStructureError: If generated text violates structural constraints.
        """
        if not isinstance(source_transcript, SourceTranscript):
            raise DomainValidationError(
                f"TransformFluidProseUseCase expects SourceTranscript, got: {type(source_transcript).__name__}"
            )

        file_name = f"{source_transcript.content_id.value}.txt"
        session_id = PipelineSessionId.create(
            channel=source_transcript.channel_name,
            content_id=source_transcript.content_id,
            channel_id=source_transcript.channel_id,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value

        system_instruction, user_prompt = self.prompt_provider.get_prompt(
            PromptKey.FLUID_PROSE,
            channel_name=source_transcript.channel_name.value,
            file_name=file_name,
            raw_text=source_transcript.body,
        )

        raw_response = self.llm_synthesis_port.transform(
            prompt=user_prompt,
            system_instruction=system_instruction,
            temperature=self.temperature,
            trace_id=f"{source_transcript.content_id.value}_fluid_prose",
            session_id=session_id,
            user_id=user_id,
        )

        return post_process_fluid_transcript(raw_response, source_transcript)
