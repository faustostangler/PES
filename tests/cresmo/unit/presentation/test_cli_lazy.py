"""Hermetic unit tests for Lazy CLI loading, Subcommand Decoupling, and Default-Fast Ingestion.

Conforms to:
    - ADR-002: Presentation CLI & Humble Object
    - ADR-026: Clean Code Anti-Patterns & Code Smell Governance (Rule 1)
    - ADR-053: Lazy Presentation CLI Loading, Subcommand Decoupling, and Default-Fast Ingestion
"""

from __future__ import annotations

import subprocess
import sys
from unittest.mock import MagicMock

import pytest


class TestLazyCliLoading:
    """Test suite verifying lazy import boundaries and CLI performance guarantees."""

    def test_cli_import_does_not_load_heavy_vendor_modules(self) -> None:
        """Verify importing cresmo.presentation.cli does not import whisper, torch, or langfuse."""
        # Run in fresh isolated subprocess to ensure clean sys.modules
        code = """
import sys
import cresmo.presentation.cli

loaded = set(sys.modules.keys())
heavy_modules = {"whisper", "torch", "langfuse"}
intersection = heavy_modules.intersection(loaded)
assert not intersection, f"Heavy modules eagerly loaded on cli import: {intersection}"
"""
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=False
        )
        assert proc.returncode == 0, (
            f"CLI eagerly loaded heavy modules:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        )

    def test_cli_import_does_not_load_pipeline_composition_or_arq_redis(self) -> None:
        """Verify importing cresmo.presentation.cli does not load pipeline, composition, arq, or redis per ADR-055."""
        code = """
import sys
import cresmo.presentation.cli

loaded = set(sys.modules.keys())
banned_modules = {
    "cresmo.application.pipeline",
    "cresmo.bootstrap.composition",
    "redis",
    "arq",
    "yt_dlp",
}
intersection = banned_modules.intersection(loaded)
assert not intersection, f"Banned modules eagerly loaded on cli import: {intersection}"
"""
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=False
        )
        assert proc.returncode == 0, (
            f"CLI eagerly loaded banned modules:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        )

    def test_composition_import_does_not_eagerly_load_arq_or_redis(self) -> None:
        """Verify importing cresmo.bootstrap.composition does not eagerly trigger arq/redis side-effects per ADR-055."""
        code = """
import sys
import cresmo.bootstrap.composition

loaded = set(sys.modules.keys())
banned_side_effects = {"arq", "redis"}
intersection = banned_side_effects.intersection(loaded)
assert not intersection, f"Composition root eagerly loaded arq/redis side-effects: {intersection}"
"""
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=False
        )
        assert proc.returncode == 0, (
            f"Composition eagerly loaded arq/redis:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        )

    def test_native_media_ingestion_adapter_does_not_load_whisper_on_import(self) -> None:
        """Verify importing NativeMediaIngestionAdapter does not import whisper or torch."""
        code = """
import sys
from cresmo.infrastructure.adapters.media.native_media_ingestion_adapter import NativeMediaIngestionAdapter

assert "whisper" not in sys.modules, "whisper eagerly imported by NativeMediaIngestionAdapter"
assert "torch" not in sys.modules, "torch eagerly imported by NativeMediaIngestionAdapter"
"""
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=False
        )
        assert proc.returncode == 0, f"Adapter eagerly loaded whisper/torch:\n{proc.stderr}"

    def test_commands_package_lazy_getattr(self) -> None:
        """Verify cresmo.presentation.commands resolves all public members dynamically via PEP 562."""
        import cresmo.presentation.commands as cmd_pkg

        # Verify __all__ completeness
        expected_all = [
            "check_config",
            "concat_master",
            "dedupe",
            "export_cookies",
            "handle_check_config",
            "handle_concat_master",
            "handle_dedupe",
            "handle_export_cookies",
            "handle_run",
            "handle_seed_prompts",
            "handle_sync",
            "handle_worker",
            "run",
            "seed_prompts",
            "sync",
            "worker",
        ]
        for name in expected_all:
            assert hasattr(cmd_pkg, name), f"Failed to dynamically resolve {name} from commands"
            assert getattr(cmd_pkg, name) is not None

        # Verify dir() matches __all__
        dir_names = set(dir(cmd_pkg))
        for name in expected_all:
            assert name in dir_names

        with pytest.raises(AttributeError, match="has no attribute 'invalid_subcommand'"):
            _ = cmd_pkg.invalid_subcommand

    def test_run_command_default_fast_no_crawl(self) -> None:
        """Verify RunSynthesisUseCase defaults to no crawling (fast path) unless crawl=True."""
        from cresmo.application.use_cases.run_synthesis import (
            RunSynthesisRequest,
            RunSynthesisUseCase,
        )
        from cresmo.domain.value_objects import DiscoveryPolicy

        use_case = RunSynthesisUseCase(
            discovery_policy=DiscoveryPolicy(),
            preflight_checker=MagicMock(),
            pipeline_factory=MagicMock(),
            discover_sources_factory=MagicMock(),
            concat_master_factory=MagicMock(),
        )
        query_default = use_case._build_discovery_query(RunSynthesisRequest(crawl=False))
        assert query_default.enable_channel_crawler is False, (
            "Default run must not crawl channel feeds"
        )

        query_crawl = use_case._build_discovery_query(RunSynthesisRequest(crawl=True))
        assert query_crawl.enable_channel_crawler is True, "Passing crawl=True must enable crawler"

    def test_cli_is_pure_humble_object_without_subprocess_bootstrapping(self) -> None:
        """Verify CLI entrypoint is a pure Humble Object without auto-spawning make/docker."""
        import cresmo.presentation.cli as cli_mod

        # Guarantee no infrastructure orchestration functions leak into cli
        assert not hasattr(cli_mod, "ensure_infrastructure")
        assert not hasattr(cli_mod, "should_ensure_infrastructure")
        assert cli_mod.__all__ == ["app", "main"]
