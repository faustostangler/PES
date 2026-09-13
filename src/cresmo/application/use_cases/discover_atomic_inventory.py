"""Stage 4 Use Case: Discover Atomic Entity Inventory.

Executes holistic discovery scan across an Enriched Compendium to extract unique candidate entities.
"""

from __future__ import annotations

from cresmo.application.json_parser import extract_json_data
from cresmo.application.ports import LLMTransformationPort, PromptProviderPort
from cresmo.domain.entities import EnrichedCompendium
from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects import AtomicEntityInventory, NoteTitle, NoteType


class DiscoverAtomicInventoryUseCase:
    """Stage 4: Holistic entity discovery across enriched text."""

    def __init__(
        self,
        llm_port: LLMTransformationPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = llm_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

    def execute(self, compendium: EnrichedCompendium) -> AtomicEntityInventory:
        """Execute Stage 4 discovery scan at temperature=0.0.

        Args:
            compendium: Enriched compendium from Stage 3.

        Returns:
            AtomicEntityInventory Value Object containing deduplicated entities.

        Raises:
            DomainValidationError: If no valid entities could be discovered.
        """
        # Step 1: Format inventory discovery prompt with compendium body and metadata.
        prompt = self.prompt_provider.get_inventory_prompt(
            compendium_title=compendium.title.value,
            channel_name=compendium.channel_name,
            compendium_body=compendium.body,
        )

        # Step 2: Execute LLM transformation with deterministic temperature=0.0.
        response = self.llm_port.transform(prompt=prompt, temperature=0.0)

        # Step 3: Parse output JSON array.
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"Expected JSON array of entities for '{compendium.title.value}', got: {type(data).__name__}"
            )

        # Step 4: Deduplicate and normalize by canonical title.
        seen_titles: set[str] = set()
        items: list[tuple[NoteTitle, NoteType]] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            note_title = NoteTitle(title_str)
            key = note_title.value.lower()
            if key in seen_titles:
                continue
            seen_titles.add(key)

            type_raw = entry.get("type", "concept")
            try:
                note_type = NoteType.from_string(str(type_raw))
            except NoteTypologyError:
                note_type = NoteType.CONCEPT

            items.append((note_title, note_type))

        if not items:
            raise DomainValidationError(
                f"No valid entities discovered in compendium '{compendium.title.value}'."
            )

        # Step 5: Return AtomicEntityInventory Value Object.
        return AtomicEntityInventory(items=tuple(items))
