"""Use Case: Longitudinal & Synchronic Expansion.

Executes Fernand Braudel's longue durée (cresmo-long-expander) and Karl Jaspers' Axial Time
(cresmo-wide-expander) deep multi-secular and horizontal cross-sections, subordinating short-term
surface events (l'histoire événementielle) to deep historical structures and global synchronies.

Conforms to:
- SPEC-001: §1 (Longitudinal and Synchronic Expander)
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
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import Content, PromptKey

# Resilient regex matching variations of the mandatory complementary section header
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Extra\s+Info|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+.+$", re.MULTILINE)


class ExpandCompendiumUseCase:
    """Deep longitudinal & synchronic expansion orchestrator."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize use case with required Hexagonal ports.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing enriched compendium persistence.
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for longitudinal/synchronic expansion.
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
        compendium: StageTranscript,
        user: UserIdentity | None = None,
    ) -> StageTranscript:
        """Execute dual expansion in-place.

        Args:
            compendium: StageTranscript aggregate from fluid prose synthesis.
            user: Optional executing UserIdentity principal (defaults to anonymous).

        Returns:
            Updated StageTranscript aggregate enriched with multi-secular and synchronic depth.

        Raises:
            CompendiumStructureError: If complementary information section is missing or empty.
            DomainValidationError: If construction invariants are violated.
        """
        session_id = PipelineSessionId.create(
            channel=compendium.channel,
            content_id=compendium.content,
        ).value
        user_id = user.value if user is not None else UserIdentity.anonymous().value

        source_match = _COMPLEMENTARY_REGEX.search(compendium.content.body)
        if source_match:
            source_body = compendium.content.body[: source_match.start()].strip()
            source_complementary = compendium.content.body[source_match.end() :].strip()
        else:
            source_body = compendium.content.body.strip()
            source_complementary = ""

        long_prompt = self.prompt_provider.get_prompt(
            PromptKey.LONG_EXPANDER,
            compendium_body=source_body,
            complementary_info=source_complementary,
        )
        longitudinal_expansion = self.llm_synthesis_port.transform(
            prompt=long_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content.id.value}_longitudinal",
            session_id=session_id,
            user_id=user_id,
        )

        wide_prompt = self.prompt_provider.get_prompt(
            PromptKey.WIDE_EXPANDER,
            current_text=longitudinal_expansion,
        )
        synchronic_expansion = self.llm_synthesis_port.transform(
            prompt=wide_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content.id.value}_synchronic",
            session_id=session_id,
            user_id=user_id,
        )

        complementary_match = _COMPLEMENTARY_REGEX.search(synchronic_expansion)
        if complementary_match:
            body = synchronic_expansion[: complementary_match.start()].strip()
            complementary_information = synchronic_expansion[complementary_match.end() :].strip()
        else:
            body = synchronic_expansion.strip()
            complementary_information = source_complementary

        # Strip any leading H1 # Title from body if generated
        body = _TITLE_H1_PATTERN.sub("", body).strip()

        if not complementary_information:
            raise CompendiumStructureError("Missing complementary info in expansion.")

        full_body = f"{body}\n\n### Extra Info\n\n{complementary_information}"

        updated = StageTranscript(
            channel=compendium.channel,
            provenance=compendium.provenance,
            content=Content.create(
                id=compendium.content.id,
                title=compendium.content.title,
                body=full_body,
            ),
            pass_count=compendium.pass_count + 1 if compendium.pass_count else 2,
            metadata=dict(compendium.metadata),
        )
        self.vault_port.save_enriched_compendium(updated)
        return updated
