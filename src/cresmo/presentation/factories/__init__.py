"""Presentation factories package for Cresmo DI container.

Re-exports settings, telemetry, adapter, and use case factory builders.
"""

from cresmo.presentation.factories.adapter_factory import (
    _resolve_cookie_file,
    build_gemini_synthesis_adapter,
    build_indexing_adapter,
    build_media_ingestion_adapter,
    build_preflight_checker,
    build_prompt_provider,
    build_vault_adapter,
)
from cresmo.presentation.factories.judge_factory import build_quality_judge_adapter
from cresmo.presentation.factories.settings_factory import (
    get_shared_settings,
    reset_shared_settings,
    resolve_shared_settings,
)
from cresmo.presentation.factories.telemetry_factory import (
    build_anonymizer_adapter,
    build_metrics_adapter,
    build_telemetry_adapter,
    probe_langfuse_ready,
    resolve_langfuse_client,
)
from cresmo.presentation.factories.use_case_factory import (
    build_concat_master_use_case,
    build_discover_batch_sources_use_case,
    build_index_raw_use_case,
    build_sync_channel_use_case,
    build_unify_duplicates_use_case,
)

__all__ = [
    "_resolve_cookie_file",
    "build_anonymizer_adapter",
    "build_concat_master_use_case",
    "build_discover_batch_sources_use_case",
    "build_gemini_synthesis_adapter",
    "build_index_raw_use_case",
    "build_indexing_adapter",
    "build_media_ingestion_adapter",
    "build_metrics_adapter",
    "build_preflight_checker",
    "build_prompt_provider",
    "build_quality_judge_adapter",
    "build_sync_channel_use_case",
    "build_telemetry_adapter",
    "build_unify_duplicates_use_case",
    "build_vault_adapter",
    "get_shared_settings",
    "probe_langfuse_ready",
    "reset_shared_settings",
    "resolve_langfuse_client",
    "resolve_shared_settings",
]
