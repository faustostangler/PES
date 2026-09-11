"""Composition Root for the Cresmo Knowledge Synthesis Engine.

Centralizes pure Dependency Injection assembly, binding validated configuration
from CresmoSettings to concrete infrastructure adapters and instantiating CresmoPipeline.
"""

from __future__ import annotations

from cresmo.application.pipeline import CresmoPipeline
from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.json_ledger_adapter import JsonLedgerAdapter
from cresmo.infrastructure.adapters.legacy_isb_ingestion_adapter import LegacyIsbIngestionAdapter
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.config import CresmoSettings


def build_pipeline(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
) -> CresmoPipeline:
    """Instantiate and wire production infrastructure adapters into CresmoPipeline.

    Args:
        settings: Validated application settings. If None, loaded fail-fast from environment.
        batch_size_override: Optional operational override for note batch size.

    Returns:
        Configured and wired CresmoPipeline ready for execution.
    """
    resolved_settings = settings or CresmoSettings()

    media_ingestion_port = LegacyIsbIngestionAdapter()
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
    )
    vault_port = ObsidianVaultAdapter(root_dir=resolved_settings.vault_dir)
    ledger_port = JsonLedgerAdapter(ledger_path=resolved_settings.ledger_path)

    effective_batch_size = (
        batch_size_override
        if batch_size_override is not None
        else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
    )
