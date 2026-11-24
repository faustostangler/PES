"""Hermetic unit tests for infrastructure environment helpers and protocols."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cresmo.infrastructure.config import CresmoSettings, StorageSettings
from cresmo.infrastructure.environment import (
    StorageSettingsProtocol,
    discover_cookies_file,
    ensure_runtime_directories,
)


@dataclass
class _StubStorage:
    """Lightweight stub satisfying StorageSettingsProtocol without Pydantic."""

    data_dir: Path
    vault_dir: Path
    mocs_dir: Path
    raw_dir: Path
    fluid_dir: Path
    gap_filler_dir: Path
    enriched_dir: Path
    master_dir: Path
    priority_texts_dir: Path


def _build_stub_storage(root: Path) -> _StubStorage:
    data_dir = root / "data"
    vault_dir = root / "vault"
    return _StubStorage(
        data_dir=data_dir,
        vault_dir=vault_dir,
        mocs_dir=vault_dir / "MOCs",
        raw_dir=data_dir / "raw",
        fluid_dir=data_dir / "fluid_prose",
        gap_filler_dir=data_dir / "gap_filler",
        enriched_dir=data_dir / "enriched",
        master_dir=data_dir / "master",
        priority_texts_dir=data_dir / "priority",
    )


class TestStorageSettingsProtocol:
    """Validate runtime_checkable StorageSettingsProtocol compliance."""

    def test_protocol_is_runtime_checkable_and_satisfied_by_settings(self) -> None:
        storage = StorageSettings()
        cresmo = CresmoSettings(_env_file=None)

        assert isinstance(storage, StorageSettingsProtocol)
        assert isinstance(cresmo.storage, StorageSettingsProtocol)
        assert not isinstance(object(), StorageSettingsProtocol)

    def test_protocol_is_satisfied_by_lightweight_stub(self, tmp_path: Path) -> None:
        stub = _build_stub_storage(tmp_path / "stub_root")

        assert isinstance(stub, StorageSettingsProtocol)


class TestEnsureRuntimeDirectories:
    """Validate idempotent directory creation for StorageSettings and stubs."""

    def test_creates_all_nine_directories_from_storage_settings(self, tmp_path: Path) -> None:
        storage = StorageSettings(
            data_dir=tmp_path / "nested" / "data",
            vault_dir=tmp_path / "nested" / "vault",
        )
        assert not (tmp_path / "nested").exists()

        ensure_runtime_directories(storage)

        expected_dirs = (
            storage.data_dir,
            storage.vault_dir,
            storage.mocs_dir,
            storage.raw_dir,
            storage.fluid_dir,
            storage.gap_filler_dir,
            storage.enriched_dir,
            storage.master_dir,
            storage.priority_texts_dir,
        )
        assert len(expected_dirs) == 9
        for directory in expected_dirs:
            assert directory.exists()
            assert directory.is_dir()

    def test_creates_all_nine_directories_from_stub_object(self, tmp_path: Path) -> None:
        stub = _build_stub_storage(tmp_path / "stub_env")
        assert isinstance(stub, StorageSettingsProtocol)

        ensure_runtime_directories(stub)

        for directory in (
            stub.data_dir,
            stub.vault_dir,
            stub.mocs_dir,
            stub.raw_dir,
            stub.fluid_dir,
            stub.gap_filler_dir,
            stub.enriched_dir,
            stub.master_dir,
            stub.priority_texts_dir,
        ):
            assert directory.exists()
            assert directory.is_dir()

    def test_is_idempotent_without_disturbing_existing_files(self, tmp_path: Path) -> None:
        storage = StorageSettings(
            data_dir=tmp_path / "data",
            vault_dir=tmp_path / "vault",
        )
        ensure_runtime_directories(storage)

        raw_file = storage.raw_dir / "transcript.txt"
        moc_file = storage.mocs_dir / "overview.md"
        raw_file.write_text("preserved raw content", encoding="utf-8")
        moc_file.write_text("# Preserved MOC", encoding="utf-8")

        ensure_runtime_directories(storage)

        assert raw_file.read_text(encoding="utf-8") == "preserved raw content"
        assert moc_file.read_text(encoding="utf-8") == "# Preserved MOC"


class TestDiscoverCookiesFile:
    """Validate pure cookie file discovery precedence and zero-byte filtering."""

    def test_configured_file_takes_precedence_over_candidates(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "custom_data"
        workspace_dir = tmp_path / "workspace"
        data_dir.mkdir(parents=True)
        (workspace_dir / "data").mkdir(parents=True)

        configured = tmp_path / "explicit_cookies.txt"
        configured.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
        (data_dir / "cookies.txt").write_text("data cookies\n", encoding="utf-8")
        (workspace_dir / "data" / "cookies.txt").write_text("ws data cookies\n", encoding="utf-8")
        (workspace_dir / ".yt_dlp_cookies.txt").write_text("yt_dlp cookies\n", encoding="utf-8")

        resolved = discover_cookies_file(data_dir, workspace_dir, configured=configured)

        assert resolved == configured

    def test_fallback_checks_strict_order_when_configured_is_none(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "custom_data"
        workspace_dir = tmp_path / "workspace"
        data_dir.mkdir(parents=True)
        (workspace_dir / "data").mkdir(parents=True)

        first = data_dir / "cookies.txt"
        second = workspace_dir / "data" / "cookies.txt"
        third = workspace_dir / ".yt_dlp_cookies.txt"
        first.write_text("first\n", encoding="utf-8")
        second.write_text("second\n", encoding="utf-8")
        third.write_text("third\n", encoding="utf-8")

        resolved = discover_cookies_file(data_dir, workspace_dir, configured=None)

        assert resolved == first

    def test_fallback_when_configured_missing_picks_workspace_data_cookies(
        self, tmp_path: Path
    ) -> None:
        data_dir = tmp_path / "custom_data"
        workspace_dir = tmp_path / "workspace"
        data_dir.mkdir(parents=True)
        (workspace_dir / "data").mkdir(parents=True)

        missing_configured = tmp_path / "nonexistent.txt"
        second = workspace_dir / "data" / "cookies.txt"
        third = workspace_dir / ".yt_dlp_cookies.txt"
        second.write_text("second\n", encoding="utf-8")
        third.write_text("third\n", encoding="utf-8")

        resolved = discover_cookies_file(data_dir, workspace_dir, configured=missing_configured)

        assert resolved == second

    def test_fallback_when_configured_is_directory_picks_yt_dlp_cookies(
        self, tmp_path: Path
    ) -> None:
        data_dir = tmp_path / "custom_data"
        workspace_dir = tmp_path / "workspace"
        configured_dir = tmp_path / "cookies_dir"
        data_dir.mkdir(parents=True)
        workspace_dir.mkdir(parents=True)
        configured_dir.mkdir(parents=True)

        third = workspace_dir / ".yt_dlp_cookies.txt"
        third.write_text("third\n", encoding="utf-8")

        resolved = discover_cookies_file(data_dir, workspace_dir, configured=configured_dir)

        assert resolved == third

    def test_skips_zero_byte_first_candidate_and_picks_second(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "custom_data"
        workspace_dir = tmp_path / "workspace"
        data_dir.mkdir(parents=True)
        (workspace_dir / "data").mkdir(parents=True)

        (data_dir / "cookies.txt").write_text("", encoding="utf-8")
        second = workspace_dir / "data" / "cookies.txt"
        second.write_text("valid cookie\n", encoding="utf-8")
        (workspace_dir / ".yt_dlp_cookies.txt").write_text("third cookie\n", encoding="utf-8")

        resolved = discover_cookies_file(data_dir, workspace_dir)

        assert resolved == second

    def test_skips_zero_byte_candidates_up_to_third(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "custom_data"
        workspace_dir = tmp_path / "workspace"
        data_dir.mkdir(parents=True)
        (workspace_dir / "data").mkdir(parents=True)

        (data_dir / "cookies.txt").write_text("", encoding="utf-8")
        (workspace_dir / "data" / "cookies.txt").write_text("", encoding="utf-8")
        third = workspace_dir / ".yt_dlp_cookies.txt"
        third.write_text("third valid\n", encoding="utf-8")

        resolved = discover_cookies_file(data_dir, workspace_dir)

        assert resolved == third

    def test_returns_none_when_no_non_empty_cookie_file_exists(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "custom_data"
        workspace_dir = tmp_path / "workspace"
        data_dir.mkdir(parents=True)
        (workspace_dir / "data").mkdir(parents=True)

        assert discover_cookies_file(data_dir, workspace_dir) is None

        (data_dir / "cookies.txt").write_text("", encoding="utf-8")
        (workspace_dir / "data" / "cookies.txt").write_text("", encoding="utf-8")
        (workspace_dir / ".yt_dlp_cookies.txt").write_text("", encoding="utf-8")

        assert (
            discover_cookies_file(
                data_dir,
                workspace_dir,
                configured=tmp_path / "missing.txt",
            )
            is None
        )
