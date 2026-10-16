"""Use Case: Transform Raw Transcript to Fluid Prose.

Executes linguistic detranscription into continuous, neutral third-person Markdown prose,
purging all marks of orality and conversational noise while verifying Named Entity (NER) spelling.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-028: Decoupling Fluid Prose Detranscription and Socratic Gap Filling
- SPEC-011: Fluid Prose Detranscription and Gap Filler Decoupling Specification
"""

from __future__ import annotations

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
    post_process_fluid_transcript,
)
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import PromptKey


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

        file_name = f"{source_transcript.content.id.value}.txt"
        session_id = PipelineSessionId.create(
            channel=source_transcript.channel,
            content_id=source_transcript.content,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value

        chat_prompt = self.prompt_provider.get_prompt(
            PromptKey.FLUID_PROSE,
            channel_name=source_transcript.channel.name,
            file_name=file_name,
            raw_text=source_transcript.content.body,
        )

        raw_response = self.llm_synthesis_port.transform(
            prompt=chat_prompt,
            temperature=self.temperature,
            trace_id=f"{source_transcript.content.id.value}_fluid_prose",
            session_id=session_id,
            user_id=user_id,
        )

        return post_process_fluid_transcript(raw_response, source_transcript)
