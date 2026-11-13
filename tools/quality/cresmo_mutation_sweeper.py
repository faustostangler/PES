"""SOTA Mutation Sweeper for Cresmo (Phase 4: Treatment).

Executes targeted, wave-based mutation testing across all layers of Cresmo
following the Doctor Stangler Architecture Method:
- Domain Core: 0 Survivors (100% Kill Rate)
- Application: 0 Survivors (100% Kill Rate)
- Infrastructure: < 5% Survivors (>95% Kill Rate)
- Presentation: Regression coverage

Features:
- Automated source tree synchronization to prevent stale cache drift
- Dynamic test-to-module mapping to eliminate mutmut 'No Tests' false positives
- Isolated per-module or wave-based execution
- Fail-safe pyproject.toml configuration management
- Detailed survivor diff inspection

Usage:
    uv run python tools/quality/cresmo_mutation_sweeper.py --wave domain
    uv run python tools/quality/cresmo_mutation_sweeper.py --file src/cresmo/domain/entities/identity.py
    uv run python tools/quality/cresmo_mutation_sweeper.py --file src/cresmo/domain/entities/identity.py --show-survivors
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, Any

import click
import typer

# Mapping of source modules/patterns to their mirrored unit test suites
MODULE_TEST_MAP: dict[str, list[str]] = {
    # Wave 1: Domain Entities & Services
    "src/cresmo/domain/entities/identity.py": [
        "tests/cresmo/unit/domain/test_entities.py",
    ],
    "src/cresmo/domain/entities/transcripts.py": [
        "tests/cresmo/unit/domain/test_entities.py",
        "tests/cresmo/unit/domain/test_monomorphic_stage_transcript.py",
        "tests/cresmo/unit/domain/test_stage_foundation.py",
    ],
    "src/cresmo/domain/entities/notes.py": [
        "tests/cresmo/unit/domain/test_entities.py",
    ],
    "src/cresmo/domain/exceptions.py": [
        "tests/cresmo/unit/domain/test_entities.py",
        "tests/cresmo/unit/domain/test_value_objects.py",
    ],
    "src/cresmo/domain/services/compendium.py": [
        "tests/cresmo/unit/domain/test_compendium.py",
        "tests/cresmo/unit/domain/test_entities.py",
        "tests/cresmo/unit/domain/test_gap_filler_foundation.py",
    ],
    # Wave 1: Domain Value Objects
    "src/cresmo/domain/value_objects/identity.py": [
        "tests/cresmo/unit/domain/test_value_objects.py",
        "tests/cresmo/unit/domain/test_batch_id.py",
        "tests/cresmo/unit/domain/test_channel_sync_vo.py",
    ],
    "src/cresmo/domain/value_objects/sync.py": [
        "tests/cresmo/unit/domain/test_channel_sync_vo.py",
        "tests/cresmo/unit/domain/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/prompt.py": [
        "tests/cresmo/unit/domain/test_chat_prompt_vo.py",
        "tests/cresmo/unit/domain/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/media.py": [
        "tests/cresmo/unit/domain/test_channel_sync_vo.py",
        "tests/cresmo/unit/domain/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/ledger.py": [
        "tests/cresmo/unit/domain/test_channel_sync_vo.py",
        "tests/cresmo/unit/domain/test_raw_index_entry_vo.py",
        "tests/cresmo/unit/domain/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/notes.py": [
        "tests/cresmo/unit/domain/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/quality.py": [
        "tests/cresmo/unit/domain/test_quality_vo.py",
        "tests/cresmo/unit/domain/test_value_objects.py",
    ],
    "src/cresmo/domain/value_objects/constants.py": [
        "tests/cresmo/unit/domain/test_domain_constants.py",
        "tests/cresmo/unit/domain/test_value_objects.py",
    ],
    "src/cresmo/domain/stage_registry.py": [
        "tests/cresmo/unit/domain/test_stage_registry.py",
    ],
    "src/cresmo/domain/taxonomy.py": [
        "tests/cresmo/unit/domain/test_taxonomy.py",
    ],
    "src/cresmo/domain/services/mechanical_validator.py": [
        "tests/cresmo/unit/domain/test_mechanical_validator.py",
        "tests/cresmo/unit/domain/test_gap_filler_foundation.py",
    ],
    # Wave 2: Application Pipeline Engine
    "src/cresmo/application/pipeline/quarantine.py": [
        "tests/cresmo/unit/application/test_stage_runner_quarantine.py",
    ],
    "src/cresmo/application/pipeline/stage_runner.py": [
        "tests/cresmo/unit/application/test_stage_runner.py",
        "tests/cresmo/unit/application/test_stage_runner_quarantine.py",
    ],
    "src/cresmo/application/pipeline/stage_descriptor.py": [
        "tests/cresmo/unit/application/test_stage_descriptor_runner.py",
        "tests/cresmo/unit/application/test_gap_filler_stage_runner.py",
    ],
    "src/cresmo/application/pipeline/stage_factory.py": [
        "tests/cresmo/unit/application/test_stage_factory.py",
    ],
    "src/cresmo/application/pipeline/transcript_loader.py": [
        "tests/cresmo/unit/application/test_transcript_loader.py",
    ],
    "src/cresmo/application/pipeline/coordinator.py": [
        "tests/cresmo/unit/application/test_pipeline.py",
        "tests/cresmo/unit/application/test_pipeline_telemetry.py",
        "tests/cresmo/unit/application/test_pipeline_coordinator.py",
    ],
    "src/cresmo/application/pipeline/context.py": [
        "tests/cresmo/unit/application/test_pipeline_execution_context.py",
        "tests/cresmo/unit/domain/test_stage_foundation.py",
        "tests/cresmo/unit/application/test_stage_runner.py",
    ],
    "src/cresmo/application/pipeline/models.py": [
        "tests/cresmo/unit/application/test_pipeline_models.py",
        "tests/cresmo/unit/domain/test_stage_foundation.py",
    ],
    # Wave 2: Application Core Utilities, Evals & Services
    "src/cresmo/application/evals/calibration_metrics.py": [
        "tests/cresmo/unit/application/test_calibration_metrics.py",
        "tests/cresmo/unit/application/test_calibrate_judges.py",
    ],
    "src/cresmo/application/evals/calibration_runner.py": [
        "tests/cresmo/unit/application/test_calibration_runner.py",
        "tests/cresmo/unit/application/test_calibrate_judges.py",
    ],
    "src/cresmo/application/services/json_parser.py": [
        "tests/cresmo/unit/application/test_json_parser.py",
    ],
    "src/cresmo/application/services/preflight.py": [
        "tests/cresmo/unit/application/test_preflight_checker.py",
        "tests/cresmo/unit/infrastructure/test_preflight_decorator.py",
    ],
    # Wave 3: Application Use Cases
    "src/cresmo/application/use_cases/concat_master.py": [
        "tests/cresmo/unit/application/test_concat_master_use_case.py",
    ],
    "src/cresmo/application/use_cases/expand_compendium.py": [
        "tests/cresmo/unit/application/test_use_cases.py",
    ],
    "src/cresmo/application/use_cases/unify_duplicate_notes.py": [
        "tests/cresmo/unit/application/test_unify_duplicates.py",
    ],
    "src/cresmo/application/use_cases/discover_atomic_inventory.py": [
        "tests/cresmo/unit/application/test_discover_atomic_inventory_use_case.py",
    ],
    "src/cresmo/application/use_cases/discovery/discover_batch_sources.py": [
        "tests/cresmo/unit/application/test_discover_batch_sources.py",
    ],
    "src/cresmo/application/use_cases/indexing/index_raw_transcripts.py": [
        "tests/cresmo/unit/application/test_index_raw_transcripts_use_case.py",
    ],
    "src/cresmo/application/use_cases/ingest_raw_transcript.py": [
        "tests/cresmo/unit/application/test_ingest_raw_transcript_use_case.py",
    ],
    "src/cresmo/application/use_cases/reconcile_mocs.py": [
        "tests/cresmo/unit/application/test_reconcile_mocs_use_case.py",
    ],
    "src/cresmo/application/use_cases/sync_channel.py": [
        "tests/cresmo/unit/application/test_sync_channel_use_case.py",
    ],
    "src/cresmo/application/use_cases/synthesize_atomic_batch.py": [
        "tests/cresmo/unit/application/test_synthesize_atomic_batch_use_case.py",
    ],
    # Wave 4: Infrastructure
    "src/cresmo/infrastructure/adapters/obsidian/adapter.py": [
        "tests/cresmo/unit/infrastructure/test_vault_adapter.py",
        "tests/cresmo/unit/infrastructure/test_unified_stage_persistence.py",
    ],
    "src/cresmo/infrastructure/adapters/obsidian/notes.py": [
        "tests/cresmo/unit/infrastructure/test_vault_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/obsidian/transcripts.py": [
        "tests/cresmo/unit/infrastructure/test_vault_adapter.py",
        "tests/cresmo/unit/infrastructure/test_unified_stage_persistence.py",
    ],
    "src/cresmo/infrastructure/adapters/obsidian/mocs.py": [
        "tests/cresmo/unit/infrastructure/test_vault_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/telemetry/opentelemetry_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_opentelemetry_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/metrics/prometheus_metrics_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_prometheus_adapter.py",
        "tests/cresmo/unit/infrastructure/test_metrics_port.py",
    ],
    "src/cresmo/infrastructure/adapters/anonymization/anonymizer_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_anonymizer_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/scrapers/cookie_extractor.py": [
        "tests/cresmo/unit/infrastructure/test_cookie_extractor.py",
    ],
    "src/cresmo/infrastructure/adapters/system/preflight_probe_adapter.py": [
        "tests/cresmo/unit/application/test_preflight_checker.py",
        "tests/cresmo/unit/bootstrap/test_bootstrap_factories.py",
    ],
    "src/cresmo/infrastructure/paths.py": [
        "tests/cresmo/unit/infrastructure/test_paths.py",
    ],
    "src/cresmo/infrastructure/system.py": [
        "tests/cresmo/unit/infrastructure/test_system.py",
    ],
    "src/cresmo/infrastructure/logging_config.py": [
        "tests/cresmo/unit/infrastructure/test_logging_config.py",
    ],
    "src/cresmo/infrastructure/config.py": [
        "tests/cresmo/unit/infrastructure/test_config.py",
    ],
    "src/cresmo/infrastructure/persistence/sqlite_ledger_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_sqlite_ledger_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/scrapers/header_generator.py": [
        "tests/cresmo/unit/infrastructure/test_header_generator.py",
    ],
    "src/cresmo/infrastructure/adapters/llm/gemini_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_gemini_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/media/native_media_ingestion_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_native_media_ingestion_adapter.py",
    ],
    # Wave 5: Bootstrap & Presentation
    "src/cresmo/bootstrap/composition.py": [
        "tests/cresmo/unit/bootstrap/test_composition.py",
        "tests/cresmo/unit/presentation/test_cli.py",
    ],
    "src/cresmo/bootstrap/factories/adapter_factory.py": [
        "tests/cresmo/unit/bootstrap/test_composition.py",
        "tests/cresmo/unit/bootstrap/test_bootstrap_factories.py",
    ],
    "src/cresmo/bootstrap/factories/judge_factory.py": [
        "tests/cresmo/unit/bootstrap/test_composition.py",
        "tests/cresmo/unit/bootstrap/test_bootstrap_factories.py",
        "tests/cresmo/unit/infrastructure/test_llm_judge.py",
    ],
    "src/cresmo/bootstrap/factories/settings_factory.py": [
        "tests/cresmo/unit/bootstrap/test_composition.py",
        "tests/cresmo/unit/bootstrap/test_bootstrap_factories.py",
    ],
    "src/cresmo/bootstrap/factories/telemetry_factory.py": [
        "tests/cresmo/unit/bootstrap/test_composition.py",
        "tests/cresmo/unit/bootstrap/test_bootstrap_factories.py",
    ],
    "src/cresmo/bootstrap/factories/use_case_factory.py": [
        "tests/cresmo/unit/bootstrap/test_composition.py",
        "tests/cresmo/unit/bootstrap/test_bootstrap_factories.py",
    ],
    "src/cresmo/presentation/cli.py": [
        "tests/cresmo/unit/presentation/test_cli.py",
        "tests/cresmo/unit/presentation/test_cli_lazy.py",
    ],
    "src/cresmo/presentation/commands/check_config.py": [
        "tests/cresmo/unit/presentation/test_cli.py",
        "tests/cresmo/unit/application/test_preflight_checker.py",
    ],
    "src/cresmo/presentation/commands/dedupe.py": [
        "tests/cresmo/unit/presentation/test_cli.py",
        "tests/cresmo/unit/application/test_unify_duplicates.py",
    ],
    "src/cresmo/presentation/commands/run.py": [
        "tests/cresmo/unit/presentation/test_run_command.py",
        "tests/cresmo/unit/presentation/test_cli.py",
    ],
    "src/cresmo/presentation/commands/sync.py": [
        "tests/cresmo/unit/presentation/test_sync_command.py",
        "tests/cresmo/unit/presentation/test_cli.py",
        "tests/cresmo/unit/application/test_sync_channel_use_case.py",
    ],
    "src/cresmo/presentation/commands/worker.py": [
        "tests/cresmo/unit/presentation/test_worker_command.py",
        "tests/cresmo/unit/presentation/test_cli.py",
    ],
    "src/cresmo/presentation/commands/concat_master.py": [
        "tests/cresmo/unit/presentation/test_concat_master_command.py",
        "tests/cresmo/unit/presentation/test_cli.py",
        "tests/cresmo/unit/application/test_concat_master_use_case.py",
    ],
    "src/cresmo/presentation/commands/seed_prompts.py": [
        "tests/cresmo/unit/presentation/test_seed_prompts.py",
        "tests/cresmo/unit/presentation/test_cli.py",
    ],
    "src/cresmo/presentation/commands/export_cookies.py": [
        "tests/cresmo/unit/presentation/test_export_cookies.py",
        "tests/cresmo/unit/presentation/test_cli.py",
        "tests/cresmo/unit/infrastructure/test_cookie_extractor.py",
    ],
    # Wave 6: Discovery Modules
    "src/cresmo/application/use_cases/discovery/channel_crawler.py": [
        "tests/cresmo/unit/application/test_channel_crawler.py",
        "tests/cresmo/unit/application/test_discover_batch_sources.py",
    ],
    "src/cresmo/application/use_cases/discovery/lake_scanner.py": [
        "tests/cresmo/unit/application/test_lake_scanner.py",
        "tests/cresmo/unit/application/test_zero_read_lake_scanner.py",
        "tests/cresmo/unit/application/test_discover_batch_sources.py",
    ],
    "src/cresmo/application/use_cases/discovery/manifests.py": [
        "tests/cresmo/unit/application/test_discovery_manifests.py",
        "tests/cresmo/unit/application/test_discover_batch_sources.py",
    ],
    "src/cresmo/application/use_cases/discovery/models.py": [
        "tests/cresmo/unit/application/test_discovery_models.py",
        "tests/cresmo/unit/application/test_discover_batch_sources.py",
    ],
    # Wave 6: Indexing Modules
    "src/cresmo/application/use_cases/indexing/distiller.py": [
        "tests/cresmo/unit/application/test_indexing_distiller.py",
        "tests/cresmo/unit/application/test_index_raw_transcripts_use_case.py",
        "tests/cresmo/unit/application/test_indexing_validators.py",
    ],
    "src/cresmo/application/use_cases/indexing/validators.py": [
        "tests/cresmo/unit/application/test_indexing_validators.py",
        "tests/cresmo/unit/application/test_index_raw_transcripts_use_case.py",
    ],
    # Wave 6: Judges Adapters
    "src/cresmo/infrastructure/adapters/judges/composite_judge.py": [
        "tests/cresmo/unit/infrastructure/test_llm_judge.py",
    ],
    "src/cresmo/infrastructure/adapters/judges/gemini_judge.py": [
        "tests/cresmo/unit/infrastructure/test_llm_judge.py",
    ],
    "src/cresmo/infrastructure/adapters/judges/langfuse_decorator.py": [
        "tests/cresmo/unit/infrastructure/test_llm_judge.py",
    ],
    "src/cresmo/infrastructure/adapters/judges/ollama_judge.py": [
        "tests/cresmo/unit/infrastructure/test_llm_judge.py",
    ],
    "src/cresmo/infrastructure/adapters/judges/preflight_decorator.py": [
        "tests/cresmo/unit/infrastructure/test_preflight_decorator.py",
        "tests/cresmo/unit/infrastructure/test_llm_judge.py",
    ],
    "src/cresmo/infrastructure/adapters/judges/typesafe_judge.py": [
        "tests/cresmo/unit/infrastructure/test_llm_judge.py",
    ],
    # Wave 6: Media Adapters
    "src/cresmo/infrastructure/adapters/media/feed.py": [
        "tests/cresmo/unit/infrastructure/test_native_media_ingestion_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/media/subtitles.py": [
        "tests/cresmo/unit/infrastructure/test_native_media_ingestion_adapter.py",
    ],
    # Wave 6: Metrics & Obsidian Helpers
    "src/cresmo/infrastructure/adapters/metrics/noop_metrics_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_metrics_port.py",
    ],
    "src/cresmo/infrastructure/adapters/obsidian/catalog.py": [
        "tests/cresmo/unit/infrastructure/test_vault_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/obsidian/utils.py": [
        "tests/cresmo/unit/infrastructure/test_vault_adapter.py",
    ],
    # Wave 6: Ollama & Prompt Adapters
    "src/cresmo/infrastructure/adapters/llm/ollama_critique_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_critique_synthesizer.py",
    ],
    "src/cresmo/infrastructure/adapters/llm/ollama_llm_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_ollama_llm_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/prompts/builders.py": [
        "tests/cresmo/unit/infrastructure/test_prompt_provider.py",
    ],
    "src/cresmo/infrastructure/adapters/prompts/json_provider.py": [
        "tests/cresmo/unit/infrastructure/test_prompt_provider.py",
        "tests/cresmo/unit/infrastructure/test_prompt_description_ssot.py",
    ],
    "src/cresmo/infrastructure/adapters/prompts/langfuse_provider.py": [
        "tests/cresmo/unit/infrastructure/test_langfuse_prompt_provider.py",
    ],
    "src/cresmo/infrastructure/adapters/prompts/catalog.py": [
        "tests/cresmo/unit/infrastructure/test_prompt_catalog.py",
    ],
    "src/cresmo/infrastructure/adapters/prompts/taxonomy_catalog.py": [
        "tests/cresmo/unit/domain/test_taxonomy.py",
        "tests/cresmo/unit/infrastructure/test_prompt_catalog.py",
    ],
    # Wave 6: Telemetry
    "src/cresmo/infrastructure/adapters/telemetry/noop.py": [
        "tests/cresmo/unit/infrastructure/test_opentelemetry_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/telemetry/thread_naming.py": [
        "tests/cresmo/unit/infrastructure/test_opentelemetry_adapter.py",
    ],
    # Wave 0 (ADR-048) & Deferred Infrastructure Modules
    "src/cresmo/infrastructure/adapters/data/polars_batch_processor.py": [
        "tests/cresmo/unit/infrastructure/test_polars_batch_processor.py",
    ],
    "src/cresmo/infrastructure/persistence/postgres_ledger_adapter.py": [
        "tests/cresmo/unit/infrastructure/test_postgres_ledger_adapter.py",
    ],
    "src/cresmo/infrastructure/adapters/llm/gemini_pool.py": [
        "tests/cresmo/unit/infrastructure/test_gemini_pool.py",
    ],
    "src/cresmo/infrastructure/adapters/judges/criterion_parser.py": [
        "tests/cresmo/unit/infrastructure/test_criterion_parser.py",
    ],
    "src/cresmo/infrastructure/adapters/scrapers/selectolax_html_parser.py": [
        "tests/cresmo/unit/infrastructure/test_selectolax_html_parser.py",
    ],
    "src/cresmo/infrastructure/persistence/models.py": [
        "tests/cresmo/unit/infrastructure/test_postgres_ledger_adapter.py",
    ],
    # Shared Kernel Context
    "src/shared_kernel/security.py": [
        "tests/shared_kernel/unit/test_security.py",
    ],
    # IAM Identity Bounded Context
    "src/identity/domain/entities.py": [
        "tests/identity/unit/test_domain.py",
    ],
    "src/identity/domain/value_objects.py": [
        "tests/identity/unit/test_domain.py",
    ],
    "src/identity/domain/exceptions.py": [
        "tests/identity/unit/test_domain.py",
    ],
    "src/identity/application/dtos.py": [
        "tests/identity/unit/test_use_cases.py",
    ],
    "src/identity/application/use_cases/register_user.py": [
        "tests/identity/unit/test_use_cases.py",
        "tests/identity/unit/test_dependencies_and_routes.py",
    ],
    "src/identity/application/use_cases/authenticate_user.py": [
        "tests/identity/unit/test_use_cases.py",
        "tests/identity/unit/test_dependencies_and_routes.py",
    ],
    "src/identity/application/use_cases/manage_pat.py": [
        "tests/identity/unit/test_use_cases.py",
        "tests/identity/unit/test_dependencies_and_routes.py",
    ],
    "src/identity/application/use_cases/validate_token.py": [
        "tests/identity/unit/test_use_cases.py",
        "tests/identity/unit/test_dependencies_and_routes.py",
    ],
    "src/identity/infrastructure/settings.py": [
        "tests/identity/unit/test_adapters.py",
    ],
    "src/identity/infrastructure/adapters/argon2_hasher_adapter.py": [
        "tests/identity/unit/test_adapters.py",
    ],
    "src/identity/infrastructure/adapters/jwt_token_adapter.py": [
        "tests/identity/unit/test_adapters.py",
    ],
    "src/identity/infrastructure/adapters/sqlite_user_repository.py": [
        "tests/identity/integration/test_sqlite_repositories.py",
    ],
    "src/identity/presentation/composition.py": [
        "tests/identity/unit/test_dependencies_and_routes.py",
        "tests/identity/integration/test_auth_api.py",
    ],
    "src/identity/presentation/dependencies.py": [
        "tests/identity/unit/test_dependencies_and_routes.py",
        "tests/identity/integration/test_auth_api.py",
    ],
    "src/identity/presentation/routes.py": [
        "tests/identity/unit/test_dependencies_and_routes.py",
        "tests/identity/integration/test_auth_api.py",
    ],
}

WAVE_DEFINITIONS: dict[str, list[str]] = {
    "completeness": [
        "src/cresmo/application/use_cases/discovery/channel_crawler.py",
        "src/cresmo/application/use_cases/discovery/lake_scanner.py",
        "src/cresmo/application/use_cases/discovery/manifests.py",
        "src/cresmo/application/use_cases/discovery/models.py",
        "src/cresmo/application/use_cases/indexing/distiller.py",
        "src/cresmo/application/use_cases/indexing/validators.py",
        "src/cresmo/infrastructure/adapters/judges/composite_judge.py",
        "src/cresmo/infrastructure/adapters/judges/gemini_judge.py",
        "src/cresmo/infrastructure/adapters/judges/langfuse_decorator.py",
        "src/cresmo/infrastructure/adapters/judges/ollama_judge.py",
        "src/cresmo/infrastructure/adapters/judges/preflight_decorator.py",
        "src/cresmo/infrastructure/adapters/judges/typesafe_judge.py",
        "src/cresmo/infrastructure/adapters/media/feed.py",
        "src/cresmo/infrastructure/adapters/media/subtitles.py",
        "src/cresmo/infrastructure/adapters/metrics/noop_metrics_adapter.py",
        "src/cresmo/infrastructure/adapters/obsidian/catalog.py",
        "src/cresmo/infrastructure/adapters/obsidian/utils.py",
        "src/cresmo/infrastructure/adapters/llm/ollama_critique_adapter.py",
        "src/cresmo/infrastructure/adapters/llm/ollama_llm_adapter.py",
        "src/cresmo/infrastructure/adapters/prompts/builders.py",
        "src/cresmo/infrastructure/adapters/prompts/json_provider.py",
        "src/cresmo/infrastructure/adapters/prompts/langfuse_provider.py",
        "src/cresmo/infrastructure/adapters/prompts/catalog.py",
        "src/cresmo/infrastructure/adapters/prompts/taxonomy_catalog.py",
        "src/cresmo/infrastructure/adapters/telemetry/noop.py",
        "src/cresmo/infrastructure/adapters/telemetry/thread_naming.py",
        "src/cresmo/bootstrap/factories/adapter_factory.py",
        "src/cresmo/bootstrap/factories/judge_factory.py",
        "src/cresmo/bootstrap/factories/settings_factory.py",
        "src/cresmo/bootstrap/factories/telemetry_factory.py",
        "src/cresmo/bootstrap/factories/use_case_factory.py",
    ],
    "domain": [
        "src/cresmo/domain/entities/identity.py",
        "src/cresmo/domain/entities/transcripts.py",
        "src/cresmo/domain/entities/notes.py",
        "src/cresmo/domain/exceptions.py",
        "src/cresmo/domain/services/compendium.py",
        "src/cresmo/domain/value_objects/identity.py",
        "src/cresmo/domain/value_objects/sync.py",
        "src/cresmo/domain/value_objects/prompt.py",
        "src/cresmo/domain/value_objects/media.py",
        "src/cresmo/domain/value_objects/ledger.py",
        "src/cresmo/domain/value_objects/notes.py",
        "src/cresmo/domain/value_objects/quality.py",
        "src/cresmo/domain/value_objects/constants.py",
        "src/cresmo/domain/stage_registry.py",
        "src/cresmo/domain/services/mechanical_validator.py",
        "src/cresmo/domain/taxonomy.py",
    ],
    "pipeline": [
        "src/cresmo/application/pipeline/quarantine.py",
        "src/cresmo/application/pipeline/stage_runner.py",
        "src/cresmo/application/pipeline/stage_descriptor.py",
        "src/cresmo/application/pipeline/stage_factory.py",
        "src/cresmo/application/pipeline/transcript_loader.py",
        "src/cresmo/application/pipeline/coordinator.py",
        "src/cresmo/application/pipeline/context.py",
        "src/cresmo/application/pipeline/models.py",
        "src/cresmo/application/evals/calibration_metrics.py",
        "src/cresmo/application/evals/calibration_runner.py",
        "src/cresmo/application/services/json_parser.py",
        "src/cresmo/application/services/preflight.py",
    ],
    "use_cases": [
        "src/cresmo/application/use_cases/concat_master.py",
        "src/cresmo/application/use_cases/expand_compendium.py",
        "src/cresmo/application/use_cases/unify_duplicate_notes.py",
        "src/cresmo/application/use_cases/discover_atomic_inventory.py",
        "src/cresmo/application/use_cases/discovery/discover_batch_sources.py",
        "src/cresmo/application/use_cases/indexing/index_raw_transcripts.py",
        "src/cresmo/application/use_cases/ingest_raw_transcript.py",
        "src/cresmo/application/use_cases/reconcile_mocs.py",
        "src/cresmo/application/use_cases/sync_channel.py",
        "src/cresmo/application/use_cases/synthesize_atomic_batch.py",
    ],
    "infra": [
        "src/cresmo/infrastructure/adapters/obsidian/adapter.py",
        "src/cresmo/infrastructure/adapters/obsidian/notes.py",
        "src/cresmo/infrastructure/adapters/obsidian/transcripts.py",
        "src/cresmo/infrastructure/adapters/obsidian/mocs.py",
        "src/cresmo/infrastructure/adapters/telemetry/opentelemetry_adapter.py",
        "src/cresmo/infrastructure/adapters/metrics/prometheus_metrics_adapter.py",
        "src/cresmo/infrastructure/adapters/anonymization/anonymizer_adapter.py",
        "src/cresmo/infrastructure/adapters/scrapers/cookie_extractor.py",
        "src/cresmo/infrastructure/adapters/system/preflight_probe_adapter.py",
        "src/cresmo/infrastructure/paths.py",
        "src/cresmo/infrastructure/system.py",
        "src/cresmo/infrastructure/logging_config.py",
        "src/cresmo/infrastructure/config.py",
        "src/cresmo/infrastructure/persistence/sqlite_ledger_adapter.py",
        "src/cresmo/infrastructure/adapters/llm/gemini_adapter.py",
        "src/cresmo/infrastructure/adapters/scrapers/header_generator.py",
        "src/cresmo/infrastructure/adapters/media/native_media_ingestion_adapter.py",
        "src/cresmo/infrastructure/adapters/data/polars_batch_processor.py",
        "src/cresmo/infrastructure/persistence/postgres_ledger_adapter.py",
        "src/cresmo/infrastructure/adapters/llm/gemini_pool.py",
        "src/cresmo/infrastructure/adapters/judges/criterion_parser.py",
        "src/cresmo/infrastructure/adapters/scrapers/selectolax_html_parser.py",
        "src/cresmo/infrastructure/persistence/models.py",
    ],
    "cresmo_unmapped_infra": [
        "src/cresmo/infrastructure/adapters/data/polars_batch_processor.py",
        "src/cresmo/infrastructure/persistence/postgres_ledger_adapter.py",
        "src/cresmo/infrastructure/adapters/llm/gemini_pool.py",
        "src/cresmo/infrastructure/adapters/judges/criterion_parser.py",
        "src/cresmo/infrastructure/adapters/scrapers/selectolax_html_parser.py",
        "src/cresmo/infrastructure/persistence/models.py",
    ],
    "presentation": [
        "src/cresmo/bootstrap/composition.py",
        "src/cresmo/presentation/cli.py",
        "src/cresmo/presentation/commands/check_config.py",
        "src/cresmo/presentation/commands/dedupe.py",
        "src/cresmo/presentation/commands/run.py",
        "src/cresmo/presentation/commands/sync.py",
        "src/cresmo/presentation/commands/worker.py",
        "src/cresmo/presentation/commands/concat_master.py",
        "src/cresmo/presentation/commands/seed_prompts.py",
        "src/cresmo/presentation/commands/export_cookies.py",
    ],
    "shared_kernel": [
        "src/shared_kernel/security.py",
    ],
    "identity_domain": [
        "src/identity/domain/entities.py",
        "src/identity/domain/value_objects.py",
        "src/identity/domain/exceptions.py",
    ],
    "identity_application": [
        "src/identity/application/dtos.py",
        "src/identity/application/use_cases/register_user.py",
        "src/identity/application/use_cases/authenticate_user.py",
        "src/identity/application/use_cases/manage_pat.py",
        "src/identity/application/use_cases/validate_token.py",
    ],
    "identity_infrastructure": [
        "src/identity/infrastructure/settings.py",
        "src/identity/infrastructure/adapters/argon2_hasher_adapter.py",
        "src/identity/infrastructure/adapters/jwt_token_adapter.py",
        "src/identity/infrastructure/adapters/sqlite_user_repository.py",
    ],
    "identity_presentation": [
        "src/identity/presentation/composition.py",
        "src/identity/presentation/dependencies.py",
        "src/identity/presentation/routes.py",
    ],
}


def ensure_mutmut_dataclass_support() -> None:
    """Ensure mutmut libcst visitor supports @dataclass decorated classes."""
    try:
        import mutmut.mutation.file_mutation as fm

        fm_path = Path(fm.__file__)
        code = fm_path.read_text(encoding="utf-8")
        target_check = "if isinstance(node, cst.ClassDef) and len(node.decorators):"
        if target_check in code and "is_dc = all(" not in code:
            old_block = "        if isinstance(node, cst.ClassDef) and len(node.decorators):\n            return True"
            new_block = (
                "        if isinstance(node, cst.ClassDef) and len(node.decorators):\n"
                "            is_dc = all(\n"
                '                (isinstance(d.decorator, cst.Name) and d.decorator.value == "dataclass")\n'
                "                or (\n"
                "                    isinstance(d.decorator, cst.Call)\n"
                "                    and isinstance(d.decorator.func, cst.Name)\n"
                '                    and d.decorator.func.value == "dataclass"\n'
                "                )\n"
                "                for d in node.decorators\n"
                "            )\n"
                "            if is_dc:\n"
                "                return False\n"
                "            return True"
            )
            if old_block in code:
                fm_path.write_text(code.replace(old_block, new_block), encoding="utf-8")
    except Exception:  # noqa: BLE001, S110
        pass


def sync_source_to_mutants() -> int:
    """Synchronize src/ files to mutants/src/ and prune orphaned files."""
    ensure_mutmut_dataclass_support()
    src_dir = Path("src")
    mutants_dir = Path("mutants/src")
    count = 0
    for src_file in src_dir.glob("**/*"):
        if src_file.is_file() and not src_file.name.endswith((".pyc", ".pyo")):
            rel = src_file.relative_to(src_dir)
            target = mutants_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or src_file.read_bytes() != target.read_bytes():
                shutil.copy2(src_file, target)
                count += 1

    # Prune orphaned code files in mutants/src to prevent import shadowing
    if mutants_dir.exists():
        for p in list(mutants_dir.glob("**/*")):
            if p.is_file() and not p.name.endswith((".meta", ".spans", ".pyc", ".pyo")):
                rel = p.relative_to(mutants_dir)
                if not (src_dir / rel).exists():
                    p.unlink(missing_ok=True)

    # Also sync tests/
    tests_dir = Path("tests")
    mutants_tests_dir = Path("mutants/tests")
    for t_file in tests_dir.glob("**/*"):
        if t_file.is_file() and not t_file.name.endswith((".pyc", ".pyo")):
            rel = t_file.relative_to(tests_dir)
            target = mutants_tests_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or t_file.read_bytes() != target.read_bytes():
                shutil.copy2(t_file, target)
                count += 1

    # Prune orphaned test files in mutants/tests
    if mutants_tests_dir.exists():
        for p in list(mutants_tests_dir.glob("**/*")):
            if p.is_file() and not p.name.endswith((".meta", ".spans", ".pyc", ".pyo")):
                rel = p.relative_to(mutants_tests_dir)
                if not (tests_dir / rel).exists():
                    p.unlink(missing_ok=True)

    # Sync only runtime .agents/skills/cresmo*/SKILL.md files needed by PromptProvider
    agents_skills_dir = Path(".agents/skills")
    mutants_agents_dir = Path("mutants/.agents")
    if agents_skills_dir.exists():
        for skill_md in agents_skills_dir.glob("cresmo*/SKILL.md"):
            rel = skill_md.relative_to(Path(".agents"))
            target = mutants_agents_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or skill_md.read_bytes() != target.read_bytes():
                shutil.copy2(skill_md, target)
                count += 1

    # Sync evals/datasets artifacts needed by golden-set invariant tests in mutants/
    evals_datasets_dir = Path("evals/datasets")
    mutants_evals_datasets_dir = Path("mutants/evals/datasets")
    if evals_datasets_dir.exists():
        for dataset_file in evals_datasets_dir.rglob("*"):
            if dataset_file.is_file():
                rel = dataset_file.relative_to(evals_datasets_dir)
                target = mutants_evals_datasets_dir / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or dataset_file.read_bytes() != target.read_bytes():
                    shutil.copy2(dataset_file, target)
                    count += 1
    return count


def collect_pytest_nodes(test_files: Sequence[str]) -> list[str]:
    """Collect pytest test node IDs for given test files."""
    cmd = [sys.executable, "-m", "pytest", *test_files, "--collect-only", "-q"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    nodes: list[str] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if "::" in line and not line.startswith("="):
            nodes.append(line)
    return nodes


def extract_function_keys(source_path: Path) -> list[str]:
    """Parse python source file and return exact mutmut mangled function keys."""
    keys: list[str] = []
    # 1. Extract directly via AST using mutmut's canonical format_utils
    try:
        from mutmut.utils.format_utils import get_mutant_name, make_mutant_key

        content = source_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                mangled = make_mutant_key(node.name)
                keys.append(get_mutant_name(source_path, mangled))
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        mangled = make_mutant_key(item.name, class_name=node.name)
                        keys.append(get_mutant_name(source_path, mangled))
    except Exception:  # noqa: BLE001, S110
        pass

    # 2. Also check if metadata already has any additional keys
    try:
        from mutmut.__main__ import SourceFileMutationData  # type: ignore[attr-defined]
        from mutmut.utils.format_utils import get_mutant_name

        data = SourceFileMutationData(path=source_path)
        data.load()
        if data.hash_by_function_name:
            for f in data.hash_by_function_name:
                keys.append(get_mutant_name(source_path, f))
    except Exception:  # noqa: BLE001, S110
        pass

    return sorted(set(keys))


def seed_mutmut_stats(source_path: Path, test_nodes: Sequence[str]) -> None:
    """Seed mutants/mutmut-stats.json with test mappings for all functions in the module."""
    stats_file = Path("mutants/mutmut-stats.json")
    data: dict[str, Any] = {}
    if stats_file.exists():
        try:
            data = json.loads(stats_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            data = {}

    tests_map = data.setdefault("tests_by_mangled_function_name", {})
    durations = data.setdefault("duration_by_test", {})
    func_hashes = data.setdefault("function_hashes", {})
    data.setdefault("stats_time", 1700000000.0)
    data.setdefault("function_dependencies", {})
    data.setdefault("config_fingerprint", {})
    data.setdefault("watched_file_hashes", {})
    data.setdefault("git_commit", None)

    for t in test_nodes:
        # Enforce safe duration floor (5.0s) to prevent false SIGXCPU (-24) in mutmut per ADR-048
        durations.setdefault(t, 5.0)

    fn_keys = extract_function_keys(source_path)
    for k in fn_keys:
        existing = set(tests_map.get(k, []))
        existing.update(test_nodes)
        tests_map[k] = sorted(existing)
        func_hashes[k] = "dummy_hash_for_mapping"

    stats_file.parent.mkdir(parents=True, exist_ok=True)
    stats_file.write_text(json.dumps(data, indent=4), encoding="utf-8")


def set_pyproject_only_mutate(target_path: str, test_files: Sequence[str] | None = None) -> str:
    """Set only_mutate and mutmut v3 pytest test selection in pyproject.toml."""
    pyproject = Path("pyproject.toml")
    original = pyproject.read_text(encoding="utf-8")

    # Clean any stale only_mutate / runner / pytest_add_cli_args_test_selection entries first
    clean_original = re.sub(r"only_mutate\s*=\s*\[.*?\]\n?", "", original, flags=re.DOTALL)
    clean_original = re.sub(r'runner\s*=\s*".*?"\n?', "", clean_original)
    clean_original = re.sub(
        r"pytest_add_cli_args_test_selection\s*=\s*\[.*?\]\n?",
        "",
        clean_original,
        flags=re.DOTALL,
    )

    mutmut_section = '[tool.mutmut]\nsource_paths = ["src"]\n'
    if mutmut_section in clean_original:
        selected_tests = (
            list(test_files)
            if test_files
            else ["tests/shared_kernel", "tests/identity", "tests/cresmo"]
        )
        tests_toml = json.dumps(selected_tests)
        new_content = clean_original.replace(
            mutmut_section,
            f'{mutmut_section}only_mutate = ["{target_path}"]\n'
            f"pytest_add_cli_args_test_selection = {tests_toml}\n",
        )
        pyproject.write_text(new_content, encoding="utf-8")
    return clean_original


def restore_pyproject(original_content: str) -> None:
    """Restore pyproject.toml to its original state."""
    Path("pyproject.toml").write_text(original_content, encoding="utf-8")


def run_mutation_on_module(
    source_path_str: str,
    reset: bool = True,
    show_survivors: bool = False,
) -> dict[str, int]:
    """Execute mutmut run on a single module with clean sync and mapped tests."""
    source_path = Path(source_path_str)
    if not source_path.exists():
        print(f"❌ Error: File not found: {source_path_str}")
        return {"total": 0, "killed": 0, "survived": 0}

    print("\n================================================================================")
    print(f"🎯 MUTATING MODULE: {source_path_str}")
    print("================================================================================")

    # 1. Sync
    synced = sync_source_to_mutants()
    if synced > 0:
        print(f"  ⚡ Synchronized {synced} source/test files to mutants/ tree.")

    # 2. Identify tests
    test_files = MODULE_TEST_MAP.get(source_path_str)
    if not test_files:
        # Fallback to layer test matching basename across layered unit suites
        layer_candidates = [
            Path(f"tests/cresmo/unit/{layer}/test_{source_path.name}")
            for layer in ("domain", "application", "infrastructure", "bootstrap", "presentation")
        ]
        existing = [str(c) for c in layer_candidates if c.exists()]
        if existing:
            test_files = existing
        else:
            test_files = [
                "tests/cresmo/unit/domain/test_entities.py",
                "tests/cresmo/unit/domain/test_value_objects.py",
            ]

    print(f"  🧪 Mirrored Test Suites: {', '.join(test_files)}")
    nodes = collect_pytest_nodes(test_files)
    print(f"  🔍 Collected {len(nodes)} test nodes for mapping.")

    # 3. Seed stats
    seed_mutmut_stats(source_path, nodes)

    # 4. Handle reset
    meta_path = Path("mutants") / f"{source_path_str}.meta"
    mutant_code_path = Path("mutants") / source_path
    if reset:
        mutant_code_path.unlink(missing_ok=True)
        if meta_path.exists():
            meta_path.unlink(missing_ok=True)
        print("  🔄 Cleared previous mutant artifacts for fresh generation.")

    # 5. Configure pyproject.toml & run
    original_pyproject = set_pyproject_only_mutate(source_path_str, test_files=test_files)
    try:
        mod_parts = Path(source_path_str)
        if mod_parts.parts and mod_parts.parts[0] == "src":
            mod_parts = Path(*mod_parts.parts[1:])
        pattern = f"*{str(mod_parts.with_suffix('')).replace('/', '.')}*"
        cmd = [sys.executable, "-m", "mutmut", "run", pattern]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            print(f"  ⚠️ mutmut warning / returncode {res.returncode}:")
            print(res.stdout[-500:] if res.stdout else res.stderr[-500:])
    finally:
        restore_pyproject(original_pyproject)

    # 6. Report stats
    if not meta_path.exists():
        print(f"  ❌ No meta output generated for {source_path_str}!")
        return {"total": 0, "killed": 0, "survived": 0}

    data = json.loads(meta_path.read_text(encoding="utf-8"))
    exit_codes = data.get("exit_code_by_key", {})
    killed = sum(1 for c in exit_codes.values() if c in (1, 2, 3, 37))
    survived = sum(1 for c in exit_codes.values() if c == 0)
    no_tests = sum(1 for c in exit_codes.values() if c in (None, 5, 33, 34))
    total = len(exit_codes)
    rate = (killed / total * 100) if total else 0.0

    status_icon = "🎉" if survived == 0 and total > 0 else "⚠️"
    print(
        f"\n  {status_icon} RESULT: Total={total} | Killed={killed} ({rate:.1f}%) | Survived={survived} | NoTests={no_tests}"
    )

    if show_survivors and survived > 0:
        survived_keys = [k for k, v in exit_codes.items() if v == 0]
        print(f"\n  🔍 SURVIVING MUTANT DIFFS ({len(survived_keys)}):")
        for k in survived_keys:
            diff_proc = subprocess.run(
                [sys.executable, "-m", "mutmut", "show", k],
                capture_output=True,
                text=True,
                check=False,
            )
            print(diff_proc.stdout)

    return {"total": total, "killed": killed, "survived": survived}


app = typer.Typer(
    name="cresmo-mutation-sweeper",
    help="SOTA Mutation Sweeper for Cresmo.",
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def sweep(
    file_path: Annotated[
        str | None,
        typer.Option(
            "--file",
            help="Single file to mutate.",
        ),
    ] = None,
    wave: Annotated[
        str | None,
        typer.Option(
            "--wave",
            help="Execution wave: completeness, domain, pipeline, use_cases, infra, presentation, all",
        ),
    ] = None,
    no_reset: Annotated[
        bool,
        typer.Option(
            "--no-reset",
            help="Do not reset mutant statuses.",
        ),
    ] = False,
    show_survivors: Annotated[
        bool,
        typer.Option(
            "--show-survivors",
            help="Print diff of surviving mutants.",
        ),
    ] = False,
) -> None:
    reset = not no_reset

    if file_path:
        targets = [file_path]
    elif wave:
        if wave == "all":
            targets = [f for wave_files in WAVE_DEFINITIONS.values() for f in wave_files]
        elif wave in WAVE_DEFINITIONS:
            targets = WAVE_DEFINITIONS[wave]
        else:
            print(
                f"❌ Error: Invalid wave '{wave}'. Valid choices: {list(WAVE_DEFINITIONS.keys()) + ['all']}"
            )
            raise typer.Exit(code=1)
    else:
        ctx = click.get_current_context()
        print(ctx.get_help())
        raise typer.Exit(code=1)

    totals = {"total": 0, "killed": 0, "survived": 0}
    for target in targets:
        res = run_mutation_on_module(target, reset=reset, show_survivors=show_survivors)
        totals["total"] += res["total"]
        totals["killed"] += res["killed"]
        totals["survived"] += res["survived"]

    rate = (totals["killed"] / totals["total"] * 100) if totals["total"] else 0.0
    print("\n" + "=" * 80)
    print("🏁 WAVE EXECUTION COMPLETE")
    print(f"   Total Mutants:   {totals['total']}")
    print(f"   Killed:          {totals['killed']} ({rate:.1f}%)")
    print(f"   Survived:        {totals['survived']}")
    print("=" * 80 + "\n")

    if totals["survived"] != 0:
        raise typer.Exit(code=1)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute mutation sweeper entrypoint.

    Args:
        argv: Optional sequence of CLI arguments. If None, uses sys.argv[1:].

    Returns:
        Process exit code integer.
    """
    try:
        res = app(args=list(argv) if argv is not None else None, standalone_mode=False)
        return 0 if res is None else int(res)
    except typer.Exit as exc:
        return exc.exit_code
    except click.ClickException as exc:
        sys.stderr.write(f"Usage error: {exc}\n")
        return getattr(exc, "exit_code", 2)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Unexpected error: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
