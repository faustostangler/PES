"""Adapter factory functions for media ingestion, Obsidian vault, and preflight health.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-002: Presentation CLI & Humble Object
- ADR-004: Native Media Ingestion Decommissioning
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from cresmo.application.ports import (
    ChannelTaxonomyPort,
    LLMTransformationPort,
    PromptProviderPort,
)
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.bootstrap.factories.settings_factory import resolve_shared_settings
from cresmo.infrastructure.adapters.media.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.obsidian import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.prompts import (
    JsonPromptProvider,
    JsonTaxonomyCatalogAdapter,
    LangfusePromptProvider,
)
from cresmo.infrastructure.adapters.scrapers.header_generator import RandomHeaderGenerator
from cresmo.infrastructure.adapters.system.preflight_probe_adapter import PreflightProbeAdapter
from cresmo.infrastructure.config import CresmoSettings

if TYPE_CHECKING:
    from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter


def _resolve_cookie_file(settings: CresmoSettings) -> Path | None:
    """Resolve active cookie file from settings or default data directory.

    Decoupled per ADR-000 and ADR-002: does not invoke browser extraction at startup.
    Explicit extraction is governed exclusively by the export-cookies CLI command.
    """
    cookie_file = getattr(settings, "cookies_file", None)
    if cookie_file is not None and Path(cookie_file).exists():
        return Path(cookie_file)

    data_dir = getattr(settings, "data_dir", None) or Path("data")
    target_cookie_path = data_dir / "cookies.txt"
    if target_cookie_path.exists():
        return target_cookie_path

    return None


def build_taxonomy_adapter(
    settings: CresmoSettings | None = None,
) -> ChannelTaxonomyPort:
    """Instantiate ChannelTaxonomyPort backed by bundled or custom taxonomy JSON."""
    settings = resolve_shared_settings(settings)
    raw_path = getattr(settings, "taxonomy_path", None)
    taxonomy_path = raw_path if isinstance(raw_path, Path) else None
    return JsonTaxonomyCatalogAdapter(taxonomy_path=taxonomy_path)


def build_media_ingestion_adapter(
    settings: CresmoSettings | None = None,
) -> NativeMediaIngestionAdapter:
    """Instantiate and wire NativeMediaIngestionAdapter with resolved settings and active cookies."""
    settings = resolve_shared_settings(settings)
    headers_path = getattr(settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    cookie_file = _resolve_cookie_file(settings)
    whisper_concurrency_limit = getattr(settings, "whisper_workers", 1)
    taxonomy_port = build_taxonomy_adapter(settings)

    return NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_concurrency_limit,
        cookie_file=cookie_file,
        taxonomy_port=taxonomy_port,
    )


def build_vault_adapter(
    settings: CresmoSettings | None = None,
) -> ObsidianVaultAdapter:
    """Instantiate and wire ObsidianVaultAdapter from application settings."""
    settings = resolve_shared_settings(settings)
    return ObsidianVaultAdapter(
        vault_dir=settings.vault_dir,
        raw_dir=settings.raw_dir,
        enriched_dir=settings.enriched_dir,
        fluid_dir=settings.fluid_dir,
        master_dir=settings.master_dir,
        data_dir=settings.data_dir,
        mocs_dir=settings.mocs_dir,
        index_path=settings.index_path,
    )


def build_preflight_checker(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings."""
    settings = resolve_shared_settings(settings)
    return PreflightHealthChecker(
        gemini_api_key=settings.gemini_api_key,
        vault_dir=settings.vault_dir,
        sqlite_ledger_path=settings.sqlite_ledger_path,
        probe_port=PreflightProbeAdapter(),
        check_ffmpeg=check_ffmpeg,
        langfuse_host=settings.langfuse_host,
        ollama_base_url=settings.ollama_base_url,
    )


def build_prompt_provider(
    settings: CresmoSettings | None = None,
    langfuse_client: Any | None = None,
) -> PromptProviderPort:
    """Instantiate PromptProviderPort with Langfuse decorator and local Json fallback."""
    settings = resolve_shared_settings(settings)
    fallback_provider = JsonPromptProvider(
        prompts_path=settings.prompts_path,
        skills_dir=settings.skills_dir,
        language=settings.language,
        settings=settings,
    )
    return LangfusePromptProvider(
        langfuse_client=langfuse_client,
        fallback_provider=fallback_provider,
        label=settings.langfuse_prompt_label,
    )


def build_gemini_synthesis_adapter(
    settings: CresmoSettings | None = None,
    langfuse_client: Any | None = None,
) -> GeminiLLMAdapter:
    """Instantiate and wire GeminiLLMAdapter for core synthesis workflows."""
    from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter

    settings = resolve_shared_settings(settings)
    api_keys = [k.get_secret_value() for k in settings.gemini_api_keys]
    return GeminiLLMAdapter(
        api_keys=api_keys,
        model_name=settings.gemini_model,
        fallback_model_name=settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
        default_temperature=settings.llm_synthesis_temperature,
    )


def build_indexing_adapter(
    settings: CresmoSettings | None = None,
    synthesis_adapter: LLMTransformationPort | None = None,
    web_index: bool = False,
    model_override: str | None = None,
    langfuse_client: Any | None = None,
    api_keys: list[str] | None = None,
) -> LLMTransformationPort:
    """Instantiate LLM adapter for indexing, selecting between local Ollama and Gemini API."""
    from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter

    settings = resolve_shared_settings(settings)
    if web_index or settings.indexing_provider == "gemini":
        if (
            synthesis_adapter is not None
            and isinstance(synthesis_adapter, GeminiLLMAdapter)
            and model_override is None
        ):
            return synthesis_adapter
        api_keys = api_keys or [k.get_secret_value() for k in settings.gemini_api_keys]
        return GeminiLLMAdapter(
            api_keys=api_keys,
            model_name=model_override or settings.gemini_model,
            fallback_model_name=settings.gemini_fallback_model,
            langfuse_client=langfuse_client,
            default_temperature=settings.llm_indexing_temperature,
        )

    from cresmo.infrastructure.adapters.llm.ollama_llm_adapter import OllamaLLMAdapter

    return OllamaLLMAdapter(
        base_url=settings.ollama_base_url,
        model=model_override or settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
        default_temperature=settings.llm_indexing_temperature,
        num_predict=settings.ollama_num_predict,
        langfuse_client=langfuse_client,
        keep_alive=settings.ollama_keep_alive,
        warmup_timeout_seconds=settings.ollama_warmup_timeout_seconds,
    )
