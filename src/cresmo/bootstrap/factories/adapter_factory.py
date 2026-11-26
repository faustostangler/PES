"""Adapter factory functions for media ingestion, Obsidian vault, LLM, and preflight health.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-004: Native Media Ingestion Decommissioning
- ADR-074: Hierarchical Immutable Settings & Pure Domain Policies (Strict ISP)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import structlog

from cresmo.application.ports import (
    ChannelTaxonomyPort,
    LLMTransformationPort,
    MetricsPort,
    ProcessRuntimePort,
    PromptProviderPort,
    TelemetryPort,
    TextEmbeddingPort,
)
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.infrastructure.adapters.llm.metrics_decorator import (
    MetricsLLMTransformationDecorator,
)
from cresmo.infrastructure.adapters.media.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.obsidian.adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.prompts.catalog import PromptCatalog, load_prompt_catalog
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.adapters.prompts.langfuse_provider import LangfusePromptProvider
from cresmo.infrastructure.adapters.scrapers.header_generator import RandomHeaderGenerator
from cresmo.infrastructure.adapters.system.preflight_probe_adapter import PreflightProbeAdapter
from cresmo.infrastructure.adapters.system.process_runtime_adapter import (
    SystemProcessRuntimeAdapter,
)
from cresmo.infrastructure.adapters.taxonomy.json_taxonomy_adapter import JsonTaxonomyCatalogAdapter
from cresmo.infrastructure.config import (
    CresmoSettings,
    GeminiSettings,
    LlmSettings,
    StorageSettings,
    resolve_shared_settings,
)
from cresmo.infrastructure.environment import discover_cookies_file
from cresmo.infrastructure.paths import find_workspace_root

if TYPE_CHECKING:
    from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

logger = structlog.get_logger(__name__)

PROVIDER_GEMINI: Final[str] = "gemini"
PROVIDER_OLLAMA: Final[str] = "ollama"
PROVIDER_TFIDF: Final[str] = "tfidf"


def _resolve_cookie_file(storage: StorageSettings, cookies_file: Path | None) -> Path | None:
    """Resolve active cookie file via pure infrastructure environment discovery."""
    return discover_cookies_file(
        data_dir=storage.data_dir,
        workspace_dir=find_workspace_root(),
        configured=cookies_file,
    )


def build_taxonomy_adapter(
    storage: StorageSettings | None = None,
) -> ChannelTaxonomyPort:
    """Instantiate ChannelTaxonomyPort backed by bundled or custom taxonomy JSON."""
    resolved = storage if storage is not None else resolve_shared_settings(None).storage
    return JsonTaxonomyCatalogAdapter(taxonomy_path=resolved.taxonomy_path)


def build_media_ingestion_adapter(
    settings: CresmoSettings | None = None,
    *,
    metrics_port: MetricsPort | None = None,
) -> NativeMediaIngestionAdapter:
    """Instantiate and wire NativeMediaIngestionAdapter with resolved settings and active cookies."""
    resolved = resolve_shared_settings(settings)
    header_generator = RandomHeaderGenerator(headers_path=resolved.storage.browser_headers_path)
    cookie_file = _resolve_cookie_file(resolved.storage, resolved.ingestion.cookies_file)
    taxonomy_port = build_taxonomy_adapter(resolved.storage)

    return NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=resolved.ingestion.workers.whisper,
        cookie_file=cookie_file,
        metrics_port=metrics_port,
        taxonomy_port=taxonomy_port,
        whisper_device=resolved.ingestion.whisper_device,
        whisper_compute_type=resolved.ingestion.whisper_compute_type,
        whisper_vad_filter=resolved.ingestion.whisper_vad_filter,
        whisper_model=resolved.ingestion.whisper_model,
        enable_rss_fast_path=resolved.ingestion.enable_rss_fast_path,
    )


def build_vault_adapter(
    storage: StorageSettings | None = None,
) -> ObsidianVaultAdapter:
    """Instantiate and wire ObsidianVaultAdapter from storage settings."""
    resolved = storage if storage is not None else resolve_shared_settings(None).storage
    return ObsidianVaultAdapter(
        vault_dir=resolved.vault_dir,
        data_dir=resolved.data_dir,
    )


def build_preflight_checker(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings."""
    resolved = resolve_shared_settings(settings)
    return PreflightHealthChecker(
        gemini_api_key=resolved.llm.gemini.primary_api_key().get_secret_value(),
        vault_dir=resolved.storage.vault_dir,
        sqlite_ledger_path=resolved.storage.sqlite_ledger_path,
        probe_port=PreflightProbeAdapter(),
        check_ffmpeg=check_ffmpeg,
    )


def build_prompt_provider(
    settings: CresmoSettings | None = None,
    langfuse_client: Any | None = None,
) -> PromptProviderPort:
    """Instantiate PromptProviderPort with Langfuse decorator and local Json fallback."""
    resolved = resolve_shared_settings(settings)
    fallback_provider = JsonPromptProvider(
        prompts_path=resolved.storage.prompts_path,
        skills_dir=resolved.storage.skills_dir,
        language=resolved.pipeline.language,
    )
    return LangfusePromptProvider(
        langfuse_client=langfuse_client,
        fallback_provider=fallback_provider,
        label=resolved.observability.langfuse.prompt_label,
    )


def build_gemini_credential_pool(
    gemini: GeminiSettings | None = None,
) -> GeminiCredentialPool | None:
    """Instantiate a shared GeminiCredentialPool from configured API keys and timeout."""
    from cresmo.infrastructure.adapters.llm.gemini_pool import GeminiCredentialPool

    resolved = gemini if gemini is not None else resolve_shared_settings(None).llm.gemini
    api_keys = [
        k.get_secret_value().strip() for k in resolved.api_keys if k.get_secret_value().strip()
    ]
    if not api_keys:
        return None
    return GeminiCredentialPool(
        keys=api_keys,
        timeout=resolved.timeout_seconds,
    )


def build_gemini_synthesis_adapter(
    gemini: GeminiSettings | None = None,
    telemetry_port: TelemetryPort | None = None,
    credential_pool: GeminiCredentialPool | None = None,
    metrics_port: MetricsPort | None = None,
) -> LLMTransformationPort:
    """Instantiate and wire GeminiLLMAdapter for core synthesis workflows."""
    from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter

    resolved = gemini if gemini is not None else resolve_shared_settings(None).llm.gemini
    api_keys = [k.get_secret_value() for k in resolved.api_keys]
    adapter = GeminiLLMAdapter(
        api_keys=api_keys,
        model_name=resolved.model,
        fallback_model_name=resolved.fallback_model,
        max_output_tokens=resolved.max_output_tokens,
        thinking_level=resolved.thinking_level,
        telemetry_port=telemetry_port,
        credential_pool=credential_pool,
        timeout_seconds=resolved.timeout_seconds,
    )
    if metrics_port is not None:
        return MetricsLLMTransformationDecorator(
            adapter, metrics_port=metrics_port, provider=PROVIDER_GEMINI
        )
    return adapter


def build_indexing_adapter(
    llm: LlmSettings | None = None,
    synthesis_adapter: LLMTransformationPort | None = None,
    web_index: bool = False,
    model_override: str | None = None,
    telemetry_port: TelemetryPort | None = None,
    credential_pool: GeminiCredentialPool | None = None,
    metrics_port: MetricsPort | None = None,
) -> LLMTransformationPort:
    """Instantiate LLM adapter for indexing, selecting between local Ollama and Gemini API."""
    from cresmo.infrastructure.adapters.llm.gemini_adapter import GeminiLLMAdapter

    resolved = llm if llm is not None else resolve_shared_settings(None).llm
    gemini_cfg = resolved.gemini
    if web_index or resolved.indexing_provider == PROVIDER_GEMINI:
        if synthesis_adapter is not None and model_override is None:
            return synthesis_adapter
        resolved_keys = [k.get_secret_value() for k in gemini_cfg.api_keys]
        gemini_adapter = GeminiLLMAdapter(
            api_keys=resolved_keys,
            model_name=model_override or gemini_cfg.model,
            fallback_model_name=gemini_cfg.fallback_model,
            max_output_tokens=gemini_cfg.max_output_tokens,
            thinking_level=gemini_cfg.thinking_level,
            telemetry_port=telemetry_port,
            credential_pool=credential_pool,
            timeout_seconds=gemini_cfg.timeout_seconds,
        )
        if metrics_port is not None:
            return MetricsLLMTransformationDecorator(
                gemini_adapter, metrics_port=metrics_port, provider=PROVIDER_GEMINI
            )
        return gemini_adapter

    from cresmo.infrastructure.adapters.llm.ollama_llm_adapter import OllamaLLMAdapter

    ollama_cfg = resolved.ollama
    ollama_adapter = OllamaLLMAdapter(
        base_url=ollama_cfg.base_url,
        model=model_override or ollama_cfg.model,
        timeout_seconds=ollama_cfg.timeout_seconds,
        default_temperature=ollama_cfg.indexing_temperature,
        num_predict=ollama_cfg.num_predict,
        telemetry_port=telemetry_port,
        keep_alive=ollama_cfg.keep_alive,
        warmup_timeout_seconds=ollama_cfg.warmup_timeout_seconds,
    )
    if metrics_port is not None:
        return MetricsLLMTransformationDecorator(
            ollama_adapter, metrics_port=metrics_port, provider=PROVIDER_OLLAMA
        )
    return ollama_adapter


def build_embedding_adapter(
    settings: CresmoSettings | None = None,
    credential_pool: GeminiCredentialPool | None = None,
) -> TextEmbeddingPort:
    """Instantiate resilient text embedding adapter configured from application settings."""
    from cresmo.infrastructure.adapters.embeddings.gemini_embedding_adapter import (
        GeminiEmbeddingAdapter,
    )
    from cresmo.infrastructure.adapters.embeddings.ollama_embedding_adapter import (
        OllamaEmbeddingAdapter,
    )
    from cresmo.infrastructure.adapters.embeddings.resilient_embedding_adapter import (
        ResilientEmbeddingAdapter,
    )
    from cresmo.infrastructure.adapters.embeddings.tfidf_embedding_adapter import (
        TfidfEmbeddingAdapter,
    )

    resolved = resolve_shared_settings(settings)
    emb_cfg = resolved.embeddings
    provider = emb_cfg.provider

    if provider == PROVIDER_TFIDF:
        return TfidfEmbeddingAdapter()

    if provider == PROVIDER_OLLAMA:
        ollama_adapter = OllamaEmbeddingAdapter(
            base_url=resolved.llm.ollama.base_url,
            model=emb_cfg.ollama_model,
            timeout_seconds=resolved.llm.ollama.timeout_seconds,
        )
        return ResilientEmbeddingAdapter(ollama_adapter, TfidfEmbeddingAdapter())

    if provider == PROVIDER_GEMINI:
        gemini_cfg = resolved.llm.gemini
        api_keys = [
            k.get_secret_value().strip()
            for k in gemini_cfg.api_keys
            if k.get_secret_value().strip()
        ]
        if credential_pool is None and not api_keys:
            return TfidfEmbeddingAdapter()
        gemini_adapter = GeminiEmbeddingAdapter(
            model_name=emb_cfg.gemini_model,
            dimensions=emb_cfg.gemini_dimensions,
            credential_pool=credential_pool,
            api_keys=api_keys or None,
            timeout_seconds=gemini_cfg.timeout_seconds,
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


def build_local_prompt_provider() -> JsonPromptProvider:
    """Instantiate local manifest + Markdown JsonPromptProvider for seeding/CLI helpers."""
    return JsonPromptProvider()


def load_local_prompt_catalog() -> PromptCatalog:
    """Load validated local PromptCatalog via bootstrap boundary."""
    return load_prompt_catalog()
