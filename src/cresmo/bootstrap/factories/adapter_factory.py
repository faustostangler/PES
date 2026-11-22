"""Adapter factory functions for media ingestion, Obsidian vault, and preflight health.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-002: Presentation CLI & Humble Object
- ADR-004: Native Media Ingestion Decommissioning
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from cresmo.application.ports import (
    ChannelTaxonomyPort,
    LLMTransformationPort,
    ProcessRuntimePort,
    PromptProviderPort,
    TextEmbeddingPort,
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
from cresmo.infrastructure.adapters.system.process_runtime_adapter import (
    SystemProcessRuntimeAdapter,
)
from cresmo.infrastructure.config import (
    CresmoSettings,
    LlmSettings,
    StorageSettings,
)
from cresmo.infrastructure.environment import discover_cookies_file
from cresmo.infrastructure.paths import find_workspace_root

if TYPE_CHECKING:
    from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter
    from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

logger = structlog.get_logger(__name__)


def _resolve_cookie_file(settings: StorageSettings) -> Path | None:
    """Resolve active cookie file via pure infrastructure environment discovery.

    Decoupled per ADR-000, ADR-002, and ADR-069: delegates candidate probing to
    ``discover_cookies_file`` without triggering browser extraction at startup.
    """
    raw_configured = getattr(settings, "cookies_file", None)
    configured = Path(raw_configured) if raw_configured is not None else None
    raw_data_dir = getattr(settings, "data_dir", None)
    data_dir = Path(raw_data_dir) if raw_data_dir is not None else Path("data")
    return discover_cookies_file(
        data_dir=data_dir,
        workspace_dir=find_workspace_root(),
        configured=configured,
    )


def build_taxonomy_adapter(
    settings: StorageSettings | None = None,
) -> ChannelTaxonomyPort:
    """Instantiate ChannelTaxonomyPort backed by bundled or custom taxonomy JSON."""
    resolved = settings if settings is not None else resolve_shared_settings(None)
    raw_path = getattr(resolved, "taxonomy_path", None)
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
    settings: StorageSettings | None = None,
) -> ObsidianVaultAdapter:
    """Instantiate and wire ObsidianVaultAdapter from storage settings."""
    resolved = settings if settings is not None else resolve_shared_settings(None)
    return ObsidianVaultAdapter(
        vault_dir=resolved.vault_dir,
        raw_dir=resolved.raw_dir,
        enriched_dir=resolved.enriched_dir,
        fluid_dir=resolved.fluid_dir,
        master_dir=resolved.master_dir,
        data_dir=resolved.data_dir,
        mocs_dir=resolved.mocs_dir,
        index_path=resolved.index_path,
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


def build_gemini_credential_pool(
    settings: LlmSettings | None = None,
) -> GeminiCredentialPool | None:
    """Instantiate a shared GeminiCredentialPool from configured API keys and timeout."""
    from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

    resolved = settings if settings is not None else resolve_shared_settings(None)
    api_keys = [
        k.get_secret_value().strip()
        for k in resolved.gemini_api_keys
        if k.get_secret_value().strip()
    ]
    if not api_keys:
        return None
    return GeminiCredentialPool(
        keys=api_keys,
        timeout=resolved.gemini_timeout_seconds,
    )


def build_gemini_synthesis_adapter(
    settings: LlmSettings | None = None,
    langfuse_client: Any | None = None,
    credential_pool: GeminiCredentialPool | None = None,
) -> GeminiLLMAdapter:
    """Instantiate and wire GeminiLLMAdapter for core synthesis workflows."""
    from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter

    resolved = settings if settings is not None else resolve_shared_settings(None)
    api_keys = [k.get_secret_value() for k in resolved.gemini_api_keys]
    return GeminiLLMAdapter(
        api_keys=api_keys,
        model_name=resolved.gemini_model,
        fallback_model_name=resolved.gemini_fallback_model,
        max_output_tokens=resolved.gemini_max_output_tokens,
        thinking_level=resolved.gemini_thinking_level,
        langfuse_client=langfuse_client,
        credential_pool=credential_pool,
        timeout_seconds=resolved.gemini_timeout_seconds,
    )


def build_indexing_adapter(
    settings: LlmSettings | None = None,
    synthesis_adapter: LLMTransformationPort | None = None,
    web_index: bool = False,
    model_override: str | None = None,
    langfuse_client: Any | None = None,
    api_keys: list[str] | None = None,
    credential_pool: GeminiCredentialPool | None = None,
) -> LLMTransformationPort:
    """Instantiate LLM adapter for indexing, selecting between local Ollama and Gemini API."""
    from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter

    resolved = settings if settings is not None else resolve_shared_settings(None)
    if web_index or resolved.indexing_provider == "gemini":
        if (
            synthesis_adapter is not None
            and isinstance(synthesis_adapter, GeminiLLMAdapter)
            and model_override is None
        ):
            return synthesis_adapter
        api_keys = api_keys or [k.get_secret_value() for k in resolved.gemini_api_keys]
        return GeminiLLMAdapter(
            api_keys=api_keys,
            model_name=model_override or resolved.gemini_model,
            fallback_model_name=resolved.gemini_fallback_model,
            max_output_tokens=resolved.gemini_max_output_tokens,
            thinking_level=resolved.gemini_thinking_level,
            langfuse_client=langfuse_client,
            credential_pool=credential_pool,
            timeout_seconds=resolved.gemini_timeout_seconds,
        )

    from cresmo.infrastructure.adapters.llm.ollama_llm_adapter import OllamaLLMAdapter

    return OllamaLLMAdapter(
        base_url=resolved.ollama_base_url,
        model=model_override or resolved.ollama_model,
        timeout_seconds=resolved.ollama_timeout_seconds,
        default_temperature=resolved.llm_indexing_temperature,
        num_predict=resolved.ollama_num_predict,
        langfuse_client=langfuse_client,
        keep_alive=resolved.ollama_keep_alive,
        warmup_timeout_seconds=resolved.ollama_warmup_timeout_seconds,
    )


def build_embedding_adapter(
    settings: CresmoSettings | None = None,
    credential_pool: GeminiCredentialPool | None = None,
) -> TextEmbeddingPort:
    """Instantiate resilient text embedding adapter configured from application settings."""
    from cresmo.infrastructure.adapters.embeddings import (
        GeminiEmbeddingAdapter,
        OllamaEmbeddingAdapter,
        ResilientEmbeddingAdapter,
        TfidfEmbeddingAdapter,
    )

    settings = resolve_shared_settings(settings)
    provider = str(getattr(settings, "embedding_provider", "gemini")).strip().lower()

    if provider == "tfidf":
        return TfidfEmbeddingAdapter()

    if provider == "ollama":
        ollama_adapter = OllamaEmbeddingAdapter(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
        return ResilientEmbeddingAdapter(ollama_adapter, TfidfEmbeddingAdapter())

    if provider == "gemini":
        api_keys = [
            k.get_secret_value().strip()
            for k in settings.gemini_api_keys
            if k.get_secret_value().strip()
        ]
        if credential_pool is None and not api_keys:
            return TfidfEmbeddingAdapter()
        gemini_adapter = GeminiEmbeddingAdapter(
            model_name=settings.gemini_embedding_model,
            dimensions=settings.gemini_embedding_dimensions,
            credential_pool=credential_pool,
            api_keys=api_keys or None,
            timeout_seconds=settings.gemini_timeout_seconds,
        )
        return ResilientEmbeddingAdapter(gemini_adapter, TfidfEmbeddingAdapter())

    logger.warning(
        "Unknown embedding_provider configured; falling back to local TF-IDF adapter.",
        embedding_provider=provider,
    )
    return TfidfEmbeddingAdapter()


def build_process_runtime_adapter() -> ProcessRuntimePort:
    """Instantiate OS-backed ProcessRuntimePort adapter."""
    return SystemProcessRuntimeAdapter()
