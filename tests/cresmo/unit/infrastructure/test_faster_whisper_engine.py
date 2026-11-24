"""Hermetic unit tests for FasterWhisperEngine (SPEC-075.4)."""

from __future__ import annotations

import sys
import threading
import time
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cresmo.domain.exceptions import CresmoInfrastructureError
from cresmo.infrastructure.adapters.media.transcriber import FasterWhisperEngine


def _make_fake_modules(
    cuda_count: int = 0,
    probe_error: Exception | None = None,
    whisper_model_cls: MagicMock | None = None,
) -> dict[str, types.ModuleType]:
    fake_ct2 = types.ModuleType("ctranslate2")
    if probe_error is not None:

        def _failing_probe() -> int:
            raise probe_error

        fake_ct2.get_cuda_device_count = _failing_probe  # type: ignore[attr-defined]
    else:
        fake_ct2.get_cuda_device_count = lambda: cuda_count  # type: ignore[attr-defined]

    fake_fw = types.ModuleType("faster_whisper")
    fake_fw.WhisperModel = whisper_model_cls or MagicMock()  # type: ignore[attr-defined]

    return {
        "ctranslate2": fake_ct2,
        "faster_whisper": fake_fw,
    }


class TestFasterWhisperEngine:
    """Unit tests covering device resolution, caching, VAD, concurrency, and errors."""

    def test_auto_device_resolution_cpu_when_no_cuda(self) -> None:
        engine = FasterWhisperEngine(device="auto", compute_type="auto")
        fake_mods = _make_fake_modules(cuda_count=0)
        with patch.dict(sys.modules, fake_mods):
            resolved_device = engine.resolve_device()
            assert resolved_device == "cpu"
            assert engine.resolve_compute_type(resolved_device) == "int8"

    def test_auto_device_resolution_cuda_when_gpu_available(self) -> None:
        engine = FasterWhisperEngine(device="auto", compute_type="auto")
        fake_mods = _make_fake_modules(cuda_count=1)
        with patch.dict(sys.modules, fake_mods):
            resolved_device = engine.resolve_device()
            assert resolved_device == "cuda"
            assert engine.resolve_compute_type(resolved_device) == "float16"

    def test_auto_device_resolution_falls_back_to_cpu_on_probe_exception(self) -> None:
        engine = FasterWhisperEngine(device="auto", compute_type="auto")
        fake_mods = _make_fake_modules(probe_error=RuntimeError("driver missing"))
        with patch.dict(sys.modules, fake_mods):
            resolved_device = engine.resolve_device()
            assert resolved_device == "cpu"
            assert engine.resolve_compute_type(resolved_device) == "int8"

    def test_explicit_device_and_compute_type_overrides_respected(self) -> None:
        engine = FasterWhisperEngine(device="cpu", compute_type="float32")
        assert engine.resolve_device() == "cpu"
        assert engine.resolve_compute_type("cpu") == "float32"

    def test_model_cache_reuses_same_key_and_separates_different_models(
        self, tmp_path: Path
    ) -> None:
        audio_file = tmp_path / "sample.m4a"
        audio_file.write_bytes(b"audio")

        seg1 = MagicMock(text="  Hello world.  ")
        seg2 = MagicMock(text="   ")
        seg3 = MagicMock(text="Second sentence.")
        mock_model_instance = MagicMock()
        mock_model_instance.transcribe.return_value = ([seg1, seg2, seg3], MagicMock())
        mock_whisper_cls = MagicMock(return_value=mock_model_instance)

        engine = FasterWhisperEngine(device="cpu", compute_type="int8", vad_filter=True)
        fake_mods = _make_fake_modules(whisper_model_cls=mock_whisper_cls)

        with patch.dict(sys.modules, fake_mods):
            text1 = engine.transcribe(audio_file, model_name="base")
            text2 = engine.transcribe(audio_file, model_name="base")
            assert text1 == "Hello world. Second sentence."
            assert text2 == "Hello world. Second sentence."
            mock_whisper_cls.assert_called_once_with("base", device="cpu", compute_type="int8")

            # Different model_name triggers a new WhisperModel load
            engine.transcribe(audio_file, model_name="small")
            assert mock_whisper_cls.call_count == 2
            mock_whisper_cls.assert_called_with("small", device="cpu", compute_type="int8")

            # clear_cache forces reload on next call
            engine.clear_cache()
            engine.transcribe(audio_file, model_name="base")
            assert mock_whisper_cls.call_count == 3

        for call in mock_model_instance.transcribe.call_args_list:
            assert call.args[0] == str(audio_file)
            assert call.kwargs["vad_filter"] is True

    def test_vad_filter_false_forwarded(self, tmp_path: Path) -> None:
        audio_file = tmp_path / "sample.m4a"
        audio_file.write_bytes(b"audio")

        mock_model_instance = MagicMock()
        mock_model_instance.transcribe.return_value = ([MagicMock(text="Raw text")], MagicMock())
        mock_whisper_cls = MagicMock(return_value=mock_model_instance)

        engine = FasterWhisperEngine(device="cpu", compute_type="int8", vad_filter=False)
        fake_mods = _make_fake_modules(whisper_model_cls=mock_whisper_cls)

        with patch.dict(sys.modules, fake_mods):
            assert engine.transcribe(audio_file, model_name="tiny") == "Raw text"
            assert mock_model_instance.transcribe.call_args.kwargs["vad_filter"] is False

    def test_concurrency_semaphore_bounds_parallel_transcriptions(self, tmp_path: Path) -> None:
        audio_file = tmp_path / "sample.m4a"
        audio_file.write_bytes(b"audio")

        active = 0
        max_active = 0
        counter_lock = threading.Lock()

        def slow_transcribe(*_args: object, **_kwargs: object) -> tuple[list[MagicMock], MagicMock]:
            nonlocal active, max_active
            with counter_lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.05)
            with counter_lock:
                active -= 1
            return ([MagicMock(text="ok")], MagicMock())

        mock_model_instance = MagicMock()
        mock_model_instance.transcribe.side_effect = slow_transcribe
        mock_whisper_cls = MagicMock(return_value=mock_model_instance)

        engine = FasterWhisperEngine(concurrency_limit=1, device="cpu", compute_type="int8")
        fake_mods = _make_fake_modules(whisper_model_cls=mock_whisper_cls)

        with patch.dict(sys.modules, fake_mods):
            threads = [
                threading.Thread(target=engine.transcribe, args=(audio_file, "base"))
                for _ in range(3)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        assert max_active == 1

    def test_transcribe_wraps_errors_in_cresmo_infrastructure_error(self, tmp_path: Path) -> None:
        audio_file = tmp_path / "broken.m4a"
        audio_file.write_bytes(b"audio")

        mock_whisper_cls = MagicMock(side_effect=RuntimeError("CUDA OOM"))
        engine = FasterWhisperEngine(device="cpu", compute_type="int8")
        fake_mods = _make_fake_modules(whisper_model_cls=mock_whisper_cls)

        with (
            patch.dict(sys.modules, fake_mods),
            pytest.raises(
                CresmoInfrastructureError, match="Whisper transcription failed: CUDA OOM"
            ),
        ):
            engine.transcribe(audio_file, model_name="base")

    def test_default_constructor_values_respected(self, tmp_path: Path) -> None:
        audio_file = tmp_path / "sample.m4a"
        audio_file.write_bytes(b"audio")

        active = 0
        max_active = 0
        counter_lock = threading.Lock()
        two_inside = threading.Event()

        def slow_transcribe(*_args: object, **_kwargs: object) -> tuple[list[MagicMock], MagicMock]:
            nonlocal active, max_active
            with counter_lock:
                active += 1
                max_active = max(max_active, active)
                if active == 2:
                    two_inside.set()
            two_inside.wait(timeout=0.5)
            time.sleep(0.03)
            with counter_lock:
                active -= 1
            return ([MagicMock(text="ok")], MagicMock())

        mock_model_instance = MagicMock()
        mock_model_instance.transcribe.side_effect = slow_transcribe
        mock_whisper_cls = MagicMock(return_value=mock_model_instance)

        engine = FasterWhisperEngine()
        fake_mods = _make_fake_modules(cuda_count=1, whisper_model_cls=mock_whisper_cls)

        with patch.dict(sys.modules, fake_mods):
            assert engine.resolve_device() == "cuda"
            assert engine.resolve_compute_type("cuda") == "float16"
            assert engine.resolve_compute_type("cpu") == "int8"

            threads = [
                threading.Thread(target=engine.transcribe, args=(audio_file, "base"))
                for _ in range(3)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        assert max_active == 2
        assert mock_model_instance.transcribe.call_args.kwargs["vad_filter"] is True
