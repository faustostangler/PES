"""Adapter factory functions for media ingestion, Obsidian vault, and preflight health.

Conforms to:
- ADR-001: Modular Monolith Domain Integrity
- ADR-002: Presentation CLI & Humble Object
- ADR-004: Native Media Ingestion Decommissioning
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cresmo.application.ports import (
    CritiqueSynthesizerPort,
    LLMTransformationPort,
    PromptProviderPort,
)
from cresmo.application.services.preflight import PreflightHealthChecker
from cresmo.infrastructure.adapters.cookie_extractor import ensure_cookies_file
from cresmo.infrastructure.adapters.gemini_adapter import GeminiLLMAdapter
from cresmo.infrastructure.adapters.header_generator import RandomHeaderGenerator
from cresmo.infrastructure.adapters.native_media_ingestion_adapter import (
    NativeMediaIngestionAdapter,
)
from cresmo.infrastructure.adapters.obsidian_vault_adapter import ObsidianVaultAdapter
from cresmo.infrastructure.adapters.ollama_critique_adapter import OllamaCritiqueAdapter
from cresmo.infrastructure.adapters.ollama_llm_adapter import OllamaLLMAdapter
from cresmo.infrastructure.adapters.prompt_provider import (
    JsonPromptProvider,
    LangfusePromptProvider,
)
from cresmo.infrastructure.config import CresmoSettings
from cresmo.presentation.factories.settings_factory import resolve_shared_settings


def _resolve_cookie_file(settings: CresmoSettings) -> Path | None:
    """Resolve active cookie file or attempt browser auto-extraction if enabled."""
    cookie_file = getattr(settings, "cookies_file", None)
    if (cookie_file is None or not cookie_file.exists()) and getattr(
        settings, "auto_extract_cookies", True
    ):
        data_dir = getattr(settings, "data_dir", None) or Path("data")
        target_cookie_path = data_dir / "cookies.txt"
        cookie_file = ensure_cookies_file(
            output_file=target_cookie_path,
            browser=getattr(settings, "browser_cookies", "firefox"),
            verbose=False,
        )
    return cookie_file


def build_media_ingestion_adapter(
    settings: CresmoSettings | None = None,
) -> NativeMediaIngestionAdapter:
    """Instantiate and wire NativeMediaIngestionAdapter with resolved settings and active cookies."""
    resolved_settings = resolve_shared_settings(settings)
    headers_path = getattr(resolved_settings, "browser_headers_path", None)
    header_generator = RandomHeaderGenerator(headers_path=headers_path)
    cookie_file = _resolve_cookie_file(resolved_settings)
    whisper_workers = getattr(resolved_settings, "whisper_workers", 1)

    return NativeMediaIngestionAdapter(
        header_generator=header_generator,
        whisper_concurrency_limit=whisper_workers,
        cookie_file=cookie_file,
    )


def build_vault_adapter(
    settings: CresmoSettings | None = None,
) -> ObsidianVaultAdapter:
    """Instantiate and wire ObsidianVaultAdapter from application settings."""
    resolved_settings = resolve_shared_settings(settings)
    return ObsidianVaultAdapter(
        vault_dir=resolved_settings.vault_dir,
        raw_dir=resolved_settings.raw_dir,
        enriched_dir=resolved_settings.enriched_dir,
        master_dir=resolved_settings.master_dir,
        data_dir=resolved_settings.data_dir,
        mocs_dir=resolved_settings.mocs_dir,
        index_path=resolved_settings.index_path,
    )


def build_preflight_checker(
    settings: CresmoSettings | None = None,
    check_ffmpeg: bool = True,
) -> PreflightHealthChecker:
    """Construct PreflightHealthChecker with resolved settings."""
    resolved_settings = resolve_shared_settings(settings)
    return PreflightHealthChecker(
        gemini_api_key=resolved_settings.gemini_api_key,
        vault_dir=resolved_settings.vault_dir,
        sqlite_ledger_path=resolved_settings.sqlite_ledger_path,
        check_ffmpeg=check_ffmpeg,
        langfuse_host=resolved_settings.langfuse_host,
        ollama_base_url=resolved_settings.ollama_base_url,
    )


def build_prompt_provider(
    settings: CresmoSettings | None = None,
    langfuse_client: Any | None = None,
) -> PromptProviderPort:
    """Instantiate PromptProviderPort with Langfuse decorator and local Json fallback."""
    resolved_settings = resolve_shared_settings(settings)
    json_prompt_provider = JsonPromptProvider(
        prompts_path=resolved_settings.prompts_path,
        skills_dir=resolved_settings.skills_dir,
    )
    return LangfusePromptProvider(
        langfuse_client=langfuse_client,
        fallback_provider=json_prompt_provider,
        label=getattr(resolved_settings, "langfuse_prompt_label", "production"),
    )


def build_gemini_synthesis_adapter(
    settings: CresmoSettings | None = None,
    langfuse_client: Any | None = None,
) -> GeminiLLMAdapter:
    """Instantiate and wire GeminiLLMAdapter for core synthesis workflows."""
    resolved_settings = resolve_shared_settings(settings)
    return GeminiLLMAdapter(
        api_key=resolved_settings.gemini_api_key.get_secret_value(),
        model_name=resolved_settings.gemini_model,
        fallback_model_name=resolved_settings.gemini_fallback_model,
        langfuse_client=langfuse_client,
        default_temperature=resolved_settings.llm_synthesis_temperature,
    )


def build_indexing_adapter(
    settings: CresmoSettings | None = None,
    synthesis_adapter: LLMTransformationPort | None = None,
    web_index: bool = False,
    model_override: str | None = None,
    langfuse_client: Any | None = None,
) -> LLMTransformationPort:
    """Instantiate LLM adapter for indexing, selecting between local Ollama and Gemini API."""
    resolved_settings = resolve_shared_settings(settings)
    if web_index or resolved_settings.indexing_provider == "gemini":
        if (
            synthesis_adapter is not None
            and isinstance(synthesis_adapter, GeminiLLMAdapter)
            and model_override is None
        ):
            return synthesis_adapter
        return GeminiLLMAdapter(
            api_key=resolved_settings.gemini_api_key.get_secret_value(),
            model_name=model_override or resolved_settings.gemini_model,
            fallback_model_name=resolved_settings.gemini_fallback_model,
            langfuse_client=langfuse_client,
            default_temperature=resolved_settings.llm_indexing_temperature,
        )

    return OllamaLLMAdapter(
        base_url=resolved_settings.ollama_base_url,
        model=model_override or resolved_settings.ollama_model,
        timeout_seconds=resolved_settings.ollama_timeout_seconds,
        default_temperature=resolved_settings.llm_indexing_temperature,
        num_predict=resolved_settings.ollama_num_predict,
        langfuse_client=langfuse_client,
        keep_alive=resolved_settings.ollama_keep_alive,
        warmup_timeout_seconds=resolved_settings.ollama_warmup_timeout_seconds,
    )


def build_critique_synthesizer_adapter(
    llm_transformation_port: LLMTransformationPort | None,
    prompt_provider: PromptProviderPort | None = None,
) -> CritiqueSynthesizerPort:
    """Instantiate and wire the OllamaCritiqueAdapter for directed reflection (ADR-031)."""
    return OllamaCritiqueAdapter(
        llm_transformation_port=llm_transformation_port,
        prompt_provider=prompt_provider,
    )

