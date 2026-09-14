"""Composition Root for the Cresmo Knowledge Synthesis Engine.

Centralizes pure Dependency Injection assembly, binding validated configuration
from CresmoSettings to concrete infrastructure adapters and instantiating CresmoPipeline.
"""

from __future__ import annotations

from collections.abc import Callable

from cresmo.application.pipeline import CresmoPipeline
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.application.use_cases.discover_batch_sources import DiscoverBatchSourcesUseCase
from cresmo.application.use_cases.sync_channel import SyncChannelUseCase
from cresmo.application.use_cases.unify_duplicate_notes import UnifyDuplicateNotesUseCase
from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.header_generator import RandomHeaderGenerator
from cresmo.infrastructure.adapters.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.sqlite_ledger_adapter import SqliteLedgerAdapter
from cresmo.infrastructure.config import CresmoSettings


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_build_pipeline__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_build_pipeline__mutmut)
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_orig(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_1(
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
    resolved_settings = None

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_2(
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
    resolved_settings = settings and CresmoSettings()

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_3(
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

    header_generator = None
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_4(
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

    header_generator = RandomHeaderGenerator(headers_path=None)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_5(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = None
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_6(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=None,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_7(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=None,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_8(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_9(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_10(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = ""
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_11(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key or resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_12(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = None
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_13(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["XXLANGFUSE_PUBLIC_KEYXX"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_14(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["langfuse_public_key"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_15(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = None
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_16(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["XXLANGFUSE_SECRET_KEYXX"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_17(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["langfuse_secret_key"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_18(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = None
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_19(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["XXLANGFUSE_HOSTXX"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_20(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["langfuse_host"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_21(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = None
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_22(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=None,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_23(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=None,
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_24(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=None,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_25(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_26(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_27(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_28(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = ""

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_29(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = None
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_30(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=None,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_31(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=None,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_32(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_33(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_34(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = None
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_35(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=None,
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_36(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=None,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_37(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=None,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_38(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=None,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_39(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_40(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_41(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_42(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_43(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = None
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_44(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=None,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_45(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=None,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_46(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=None,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_47(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_48(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_49(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_50(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = None

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_51(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=None)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_52(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = None

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_53(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_54(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=None,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_55(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=None,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_56(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=None,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_57(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=None,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_58(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=None,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_59(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=None,
    )


def x_build_pipeline__mutmut_60(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_61(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_62(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_63(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        batch_size=effective_batch_size,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_64(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        prompt_provider=prompt_provider,
    )


def x_build_pipeline__mutmut_65(
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

    header_generator = RandomHeaderGenerator(headers_path=resolved_settings.browser_headers_path)
    prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    langfuse_client = None
    if (
        resolved_settings.langfuse_public_key
        and resolved_settings.langfuse_secret_key.get_secret_value()
    ):
        import os

        os.environ["LANGFUSE_PUBLIC_KEY"] = resolved_settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = resolved_settings.langfuse_secret_key.get_secret_value()
        os.environ["LANGFUSE_HOST"] = resolved_settings.langfuse_host
        try:
            from langfuse import Langfuse

            langfuse_client = Langfuse(
                public_key=resolved_settings.langfuse_public_key,
                secret_key=resolved_settings.langfuse_secret_key.get_secret_value(),
                host=resolved_settings.langfuse_host,
            )
        except Exception:  # noqa: BLE001
            langfuse_client = None

    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved_settings.whisper_workers,
    )
    llm_port = GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
    )
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    ledger_port = SqliteLedgerAdapter(db_path=resolved_settings.sqlite_ledger_path)

    effective_batch_size = (
        batch_size_override if batch_size_override is not None else resolved_settings.batch_size
    )

    return CresmoPipeline(
        media_ingestion_port=media_ingestion_port,
        llm_port=llm_port,
        vault_port=vault_port,
        ledger_port=ledger_port,
        batch_size=effective_batch_size,
        )

mutants_x_build_pipeline__mutmut['_mutmut_orig'] = x_build_pipeline__mutmut_orig # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_1'] = x_build_pipeline__mutmut_1 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_2'] = x_build_pipeline__mutmut_2 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_3'] = x_build_pipeline__mutmut_3 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_4'] = x_build_pipeline__mutmut_4 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_5'] = x_build_pipeline__mutmut_5 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_6'] = x_build_pipeline__mutmut_6 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_7'] = x_build_pipeline__mutmut_7 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_8'] = x_build_pipeline__mutmut_8 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_9'] = x_build_pipeline__mutmut_9 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_10'] = x_build_pipeline__mutmut_10 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_11'] = x_build_pipeline__mutmut_11 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_12'] = x_build_pipeline__mutmut_12 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_13'] = x_build_pipeline__mutmut_13 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_14'] = x_build_pipeline__mutmut_14 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_15'] = x_build_pipeline__mutmut_15 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_16'] = x_build_pipeline__mutmut_16 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_17'] = x_build_pipeline__mutmut_17 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_18'] = x_build_pipeline__mutmut_18 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_19'] = x_build_pipeline__mutmut_19 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_20'] = x_build_pipeline__mutmut_20 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_21'] = x_build_pipeline__mutmut_21 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_22'] = x_build_pipeline__mutmut_22 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_23'] = x_build_pipeline__mutmut_23 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_24'] = x_build_pipeline__mutmut_24 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_25'] = x_build_pipeline__mutmut_25 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_26'] = x_build_pipeline__mutmut_26 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_27'] = x_build_pipeline__mutmut_27 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_28'] = x_build_pipeline__mutmut_28 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_29'] = x_build_pipeline__mutmut_29 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_30'] = x_build_pipeline__mutmut_30 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_31'] = x_build_pipeline__mutmut_31 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_32'] = x_build_pipeline__mutmut_32 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_33'] = x_build_pipeline__mutmut_33 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_34'] = x_build_pipeline__mutmut_34 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_35'] = x_build_pipeline__mutmut_35 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_36'] = x_build_pipeline__mutmut_36 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_37'] = x_build_pipeline__mutmut_37 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_38'] = x_build_pipeline__mutmut_38 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_39'] = x_build_pipeline__mutmut_39 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_40'] = x_build_pipeline__mutmut_40 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_41'] = x_build_pipeline__mutmut_41 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_42'] = x_build_pipeline__mutmut_42 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_43'] = x_build_pipeline__mutmut_43 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_44'] = x_build_pipeline__mutmut_44 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_45'] = x_build_pipeline__mutmut_45 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_46'] = x_build_pipeline__mutmut_46 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_47'] = x_build_pipeline__mutmut_47 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_48'] = x_build_pipeline__mutmut_48 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_49'] = x_build_pipeline__mutmut_49 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_50'] = x_build_pipeline__mutmut_50 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_51'] = x_build_pipeline__mutmut_51 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_52'] = x_build_pipeline__mutmut_52 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_53'] = x_build_pipeline__mutmut_53 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_54'] = x_build_pipeline__mutmut_54 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_55'] = x_build_pipeline__mutmut_55 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_56'] = x_build_pipeline__mutmut_56 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_57'] = x_build_pipeline__mutmut_57 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_58'] = x_build_pipeline__mutmut_58 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_59'] = x_build_pipeline__mutmut_59 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_60'] = x_build_pipeline__mutmut_60 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_61'] = x_build_pipeline__mutmut_61 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_62'] = x_build_pipeline__mutmut_62 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_63'] = x_build_pipeline__mutmut_63 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_64'] = x_build_pipeline__mutmut_64 # type: ignore # mutmut generated
mutants_x_build_pipeline__mutmut['x_build_pipeline__mutmut_65'] = x_build_pipeline__mutmut_65 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_build_preflight_checker__mutmut)
def build_preflight_checker(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_orig(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_1(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = False,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_2(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = None
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_3(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings and CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_4(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=None,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_5(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=None,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_6(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=None,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_7(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=None,
    )


def x_build_preflight_checker__mutmut_8(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_9(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_10(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        check_ffmpeg=check_ffmpeg,
    )


def x_build_preflight_checker__mutmut_11(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings.

    Args:
        settings: Validated application settings.
        check_ffmpeg: Whether to verify presence of ffmpeg in system PATH.

    Returns:
        Configured PreflightHealthChecker instance.
    """
    resolved_settings = settings or CresmoSettings()
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        )

mutants_x_build_preflight_checker__mutmut['_mutmut_orig'] = x_build_preflight_checker__mutmut_orig # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_1'] = x_build_preflight_checker__mutmut_1 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_2'] = x_build_preflight_checker__mutmut_2 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_3'] = x_build_preflight_checker__mutmut_3 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_4'] = x_build_preflight_checker__mutmut_4 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_5'] = x_build_preflight_checker__mutmut_5 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_6'] = x_build_preflight_checker__mutmut_6 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_7'] = x_build_preflight_checker__mutmut_7 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_8'] = x_build_preflight_checker__mutmut_8 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_9'] = x_build_preflight_checker__mutmut_9 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_10'] = x_build_preflight_checker__mutmut_10 # type: ignore # mutmut generated
mutants_x_build_preflight_checker__mutmut['x_build_preflight_checker__mutmut_11'] = x_build_preflight_checker__mutmut_11 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_build_sync_channel_use_case__mutmut)
def build_sync_channel_use_case(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_orig(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_1(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = False,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_2(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = None
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_3(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings and CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_4(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = None
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_5(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(None, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_6(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=None)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_7(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_8(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, )
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_9(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = None

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_10(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(None, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_11(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=None)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_12(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_13(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, )

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_14(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_15(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "XXLedger port must be wired for channel sync.XX"

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_16(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_17(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "LEDGER PORT MUST BE WIRED FOR CHANNEL SYNC."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_18(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=None,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_19(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=None,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_20(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=None,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_21(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=None,
    )


def x_build_sync_channel_use_case__mutmut_22(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_23(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        pipeline=pipeline,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_24(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        preflight_checker=preflight_checker,
    )


def x_build_sync_channel_use_case__mutmut_25(
    settings: CresmoSettings | None = None,
    batch_size_override: int | None = None,
    check_ffmpeg: bool = True,
) -> SyncChannelUseCase:
    """Construct SyncChannelUseCase with all ports and dependencies wired.

    Args:
        settings: Validated application settings.
        batch_size_override: Optional operational override for batch size.
        check_ffmpeg: Whether to verify ffmpeg in preflight.

    Returns:
        Wired SyncChannelUseCase orchestrator.
    """
    resolved_settings = settings or CresmoSettings()
    pipeline = build_pipeline(resolved_settings, batch_size_override=batch_size_override)
    preflight_checker = build_preflight_checker(resolved_settings, check_ffmpeg=check_ffmpeg)

    assert pipeline.ledger_port is not None, "Ledger port must be wired for channel sync."

    return SyncChannelUseCase(
        media_ingestion_port=pipeline.media_ingestion_port,
        ledger_port=pipeline.ledger_port,
        pipeline=pipeline,
        )

mutants_x_build_sync_channel_use_case__mutmut['_mutmut_orig'] = x_build_sync_channel_use_case__mutmut_orig # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_1'] = x_build_sync_channel_use_case__mutmut_1 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_2'] = x_build_sync_channel_use_case__mutmut_2 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_3'] = x_build_sync_channel_use_case__mutmut_3 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_4'] = x_build_sync_channel_use_case__mutmut_4 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_5'] = x_build_sync_channel_use_case__mutmut_5 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_6'] = x_build_sync_channel_use_case__mutmut_6 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_7'] = x_build_sync_channel_use_case__mutmut_7 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_8'] = x_build_sync_channel_use_case__mutmut_8 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_9'] = x_build_sync_channel_use_case__mutmut_9 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_10'] = x_build_sync_channel_use_case__mutmut_10 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_11'] = x_build_sync_channel_use_case__mutmut_11 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_12'] = x_build_sync_channel_use_case__mutmut_12 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_13'] = x_build_sync_channel_use_case__mutmut_13 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_14'] = x_build_sync_channel_use_case__mutmut_14 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_15'] = x_build_sync_channel_use_case__mutmut_15 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_16'] = x_build_sync_channel_use_case__mutmut_16 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_17'] = x_build_sync_channel_use_case__mutmut_17 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_18'] = x_build_sync_channel_use_case__mutmut_18 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_19'] = x_build_sync_channel_use_case__mutmut_19 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_20'] = x_build_sync_channel_use_case__mutmut_20 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_21'] = x_build_sync_channel_use_case__mutmut_21 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_22'] = x_build_sync_channel_use_case__mutmut_22 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_23'] = x_build_sync_channel_use_case__mutmut_23 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_24'] = x_build_sync_channel_use_case__mutmut_24 # type: ignore # mutmut generated
mutants_x_build_sync_channel_use_case__mutmut['x_build_sync_channel_use_case__mutmut_25'] = x_build_sync_channel_use_case__mutmut_25 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_build_unify_duplicates_use_case__mutmut)
def build_unify_duplicates_use_case(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_orig(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_1(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = None
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_2(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings and CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_3(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = None
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_4(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=None,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_5(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=None,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_6(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=None,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_7(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_8(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_9(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        )
    return UnifyDuplicateNotesUseCase(vault_port=vault_port)


def x_build_unify_duplicates_use_case__mutmut_10(
    settings: CresmoSettings | None = None,
) -> UnifyDuplicateNotesUseCase:
    """Construct UnifyDuplicateNotesUseCase with ObsidianVaultAdapter wired.

    Args:
        settings: Validated application settings.

    Returns:
        Configured UnifyDuplicateNotesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    vault_port = ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
    )
    return UnifyDuplicateNotesUseCase(vault_port=None)

mutants_x_build_unify_duplicates_use_case__mutmut['_mutmut_orig'] = x_build_unify_duplicates_use_case__mutmut_orig # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_1'] = x_build_unify_duplicates_use_case__mutmut_1 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_2'] = x_build_unify_duplicates_use_case__mutmut_2 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_3'] = x_build_unify_duplicates_use_case__mutmut_3 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_4'] = x_build_unify_duplicates_use_case__mutmut_4 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_5'] = x_build_unify_duplicates_use_case__mutmut_5 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_6'] = x_build_unify_duplicates_use_case__mutmut_6 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_7'] = x_build_unify_duplicates_use_case__mutmut_7 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_8'] = x_build_unify_duplicates_use_case__mutmut_8 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_9'] = x_build_unify_duplicates_use_case__mutmut_9 # type: ignore # mutmut generated
mutants_x_build_unify_duplicates_use_case__mutmut['x_build_unify_duplicates_use_case__mutmut_10'] = x_build_unify_duplicates_use_case__mutmut_10 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_build_discover_batch_sources_use_case__mutmut)
def build_discover_batch_sources_use_case(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_orig(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_1(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = None
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_2(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings and CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_3(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = None
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_4(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(None, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_5(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, None, None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_6(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr("browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_7(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_8(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", )
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_9(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "XXbrowser_headers_pathXX", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_10(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "BROWSER_HEADERS_PATH", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_11(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = None
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_12(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=None)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_13(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = None
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_14(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(None, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_15(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, None, 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_16(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", None)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_17(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr("whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_18(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_19(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", )
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_20(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "XXwhisper_workersXX", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_21(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "WHISPER_WORKERS", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_22(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 2)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_23(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = None
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_24(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=None,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_25(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=None,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_26(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_27(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_28(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=None,
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_29(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=None,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_30(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        progress_callback=None,
    )


def x_build_discover_batch_sources_use_case__mutmut_31(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        settings=resolved_settings,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_32(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        progress_callback=progress_callback,
    )


def x_build_discover_batch_sources_use_case__mutmut_33(
    settings: CresmoSettings | None = None,
    progress_callback: Callable[[str], object] | None = None,
) -> DiscoverBatchSourcesUseCase:
    """Construct DiscoverBatchSourcesUseCase with NativeMediaIngestionAdapter wired.

    Args:
        settings: Validated application settings.
        progress_callback: Optional callback for status and discovery notifications.

    Returns:
        Configured DiscoverBatchSourcesUseCase instance.
    """
    resolved_settings = settings or CresmoSettings()
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)
    media_ingestion_port = NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
    )
    return DiscoverBatchSourcesUseCase(
        media_ingestion_port=media_ingestion_port,
        settings=resolved_settings,
        )

mutants_x_build_discover_batch_sources_use_case__mutmut['_mutmut_orig'] = x_build_discover_batch_sources_use_case__mutmut_orig # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_1'] = x_build_discover_batch_sources_use_case__mutmut_1 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_2'] = x_build_discover_batch_sources_use_case__mutmut_2 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_3'] = x_build_discover_batch_sources_use_case__mutmut_3 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_4'] = x_build_discover_batch_sources_use_case__mutmut_4 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_5'] = x_build_discover_batch_sources_use_case__mutmut_5 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_6'] = x_build_discover_batch_sources_use_case__mutmut_6 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_7'] = x_build_discover_batch_sources_use_case__mutmut_7 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_8'] = x_build_discover_batch_sources_use_case__mutmut_8 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_9'] = x_build_discover_batch_sources_use_case__mutmut_9 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_10'] = x_build_discover_batch_sources_use_case__mutmut_10 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_11'] = x_build_discover_batch_sources_use_case__mutmut_11 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_12'] = x_build_discover_batch_sources_use_case__mutmut_12 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_13'] = x_build_discover_batch_sources_use_case__mutmut_13 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_14'] = x_build_discover_batch_sources_use_case__mutmut_14 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_15'] = x_build_discover_batch_sources_use_case__mutmut_15 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_16'] = x_build_discover_batch_sources_use_case__mutmut_16 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_17'] = x_build_discover_batch_sources_use_case__mutmut_17 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_18'] = x_build_discover_batch_sources_use_case__mutmut_18 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_19'] = x_build_discover_batch_sources_use_case__mutmut_19 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_20'] = x_build_discover_batch_sources_use_case__mutmut_20 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_21'] = x_build_discover_batch_sources_use_case__mutmut_21 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_22'] = x_build_discover_batch_sources_use_case__mutmut_22 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_23'] = x_build_discover_batch_sources_use_case__mutmut_23 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_24'] = x_build_discover_batch_sources_use_case__mutmut_24 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_25'] = x_build_discover_batch_sources_use_case__mutmut_25 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_26'] = x_build_discover_batch_sources_use_case__mutmut_26 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_27'] = x_build_discover_batch_sources_use_case__mutmut_27 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_28'] = x_build_discover_batch_sources_use_case__mutmut_28 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_29'] = x_build_discover_batch_sources_use_case__mutmut_29 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_30'] = x_build_discover_batch_sources_use_case__mutmut_30 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_31'] = x_build_discover_batch_sources_use_case__mutmut_31 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_32'] = x_build_discover_batch_sources_use_case__mutmut_32 # type: ignore # mutmut generated
mutants_x_build_discover_batch_sources_use_case__mutmut['x_build_discover_batch_sources_use_case__mutmut_33'] = x_build_discover_batch_sources_use_case__mutmut_33 # type: ignore # mutmut generated
