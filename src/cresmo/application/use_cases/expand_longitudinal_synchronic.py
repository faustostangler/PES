"""Stage 3 Use Case: Longitudinal & Synchronic Expansion.

Executes Fernand Braudel's longue durée (cresmo-long-expander) and Karl Jaspers' Axial Time
(cresmo-wide-expander) deep multi-secular and horizontal cross-sections, subordinating short-term
surface events (l'histoire événementielle) to deep historical structures and global synchronies.

Conforms to:
- SPEC-001: §1 (Stage 3 Expander)
- ADR-001: Modular Monolith Domain Integrity
"""

from __future__ import annotations

import re

from cresmo.application.ports import (
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import EnrichedCompendium
from cresmo.domain.exceptions import CompendiumStructureError

_COMPLEMENTARY_TAG = "## Informações Complementares"
# Resilient regex matching variations of the mandatory complementary section header
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)
_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+.+$", re.MULTILINE)


class ExpandLongitudinalSynchronicUseCase:
    """Stage 3: Deep longitudinal & synchronic expansion orchestrator."""

    def __init__(
        self,
        llm_synthesis_port: LLMTransformationPort | None = None,
        vault_port: VaultRepositoryPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        temperature: float | None = None,
        *,
        llm_port: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize Stage 3 use case with required Hexagonal ports.

        Args:
            llm_synthesis_port: Hexagonal port for generative LLM inference.
            vault_port: Port providing enriched compendium persistence.
            prompt_provider: Optional provider for decoupled prompt templates.
            temperature: Sampling temperature override for longitudinal/synchronic expansion.
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
        compendium: EnrichedCompendium,
    ) -> EnrichedCompendium:
        """Execute Stage 3 dual expansion in-place.

        Args:
            compendium: EnrichedCompendium aggregate from Stage 2.

        Returns:
            Updated EnrichedCompendium aggregate enriched with multi-secular and synchronic depth.

        Raises:
            CompendiumStructureError: If complementary information section is missing or empty.
            DomainValidationError: If construction invariants are violated.
        """
        longitudinal_prompt = self.prompt_provider.get_long_expander_prompt(
            compendium_body=compendium.body,
            complementary_info=compendium.complementary_info,
        )
        longitudinal_expansion = self.llm_synthesis_port.transform(
            prompt=longitudinal_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_longitudinal",
            session_id=f"stage3_expansion_{compendium.channel_name}",
            user_id=str(compendium.channel_name),
        )

        synchronic_prompt = self.prompt_provider.get_wide_expander_prompt(
            current_text=longitudinal_expansion,
        )
        synchronic_expansion = self.llm_synthesis_port.transform(
            prompt=synchronic_prompt,
            temperature=self.temperature,
            trace_id=f"{compendium.content_id.value}_synchronic",
            session_id=f"stage3_expansion_{compendium.channel_name}",
            user_id=str(compendium.channel_name),
        )

        complementary_match = _COMPLEMENTARY_REGEX.search(synchronic_expansion)
        if complementary_match:
            body = synchronic_expansion[: complementary_match.start()].strip()
            complementary_information = synchronic_expansion[complementary_match.end() :].strip()
        elif _COMPLEMENTARY_TAG in synchronic_expansion:
            parts = synchronic_expansion.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            complementary_information = parts[1].strip()
        else:
            body = synchronic_expansion.strip()
            complementary_information = compendium.complementary_info

        # Strip any leading H1 # Title from body if generated
        body = _TITLE_H1_PATTERN.sub("", body).strip()

        if not complementary_information:
            raise CompendiumStructureError("Missing complementary info in expansion.")

        updated = EnrichedCompendium(
            content_id=compendium.content_id,
            channel_name=compendium.channel_name,
            title=compendium.title,
            body=body,
            complementary_info=complementary_information,
            pass_count=compendium.pass_count + 1,
            channel_id=compendium.channel_id,
            channel_category=compendium.channel_category,
            source_url=compendium.source_url,
            publication_date=compendium.publication_date,
            video_date=compendium.video_date,
            video_description=compendium.video_description,
        )
        self.vault_port.save_enriched_compendium(updated)
        return updated
