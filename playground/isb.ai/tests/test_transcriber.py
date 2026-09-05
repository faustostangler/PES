import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import transcriber


@pytest.fixture(autouse=True)
def clean_whisper_cache():
    """Ensure Whisper model cache is cleared before and after each test."""
    transcriber.unload_whisper_models()
    yield
    transcriber.unload_whisper_models()


def test_get_whisper_model_caching():
    """Should load model once and return cached instance on subsequent calls."""
    mock_model = MagicMock()
    with patch("whisper.load_model", return_value=mock_model) as mock_load:
        m1 = transcriber.get_whisper_model("base", "cpu")
        m2 = transcriber.get_whisper_model("base", "cpu")

        assert m1 is mock_model
        assert m2 is mock_model
        assert mock_load.call_count == 1
        mock_load.assert_called_once_with("base", device="cpu")


def test_unload_whisper_models():
    """Should clear cached models and trigger memory garbage collection."""
    mock_model = MagicMock()
    with patch("whisper.load_model", return_value=mock_model):
        transcriber.get_whisper_model("base", "cpu")
        assert len(transcriber._MODEL_CACHE) == 1

        with patch("gc.collect") as mock_gc:
            transcriber.unload_whisper_models()
            assert len(transcriber._MODEL_CACHE) == 0
            assert mock_gc.called


def test_transcribe_audio_to_text_device_cuda_enables_fp16(tmp_path):
    """When device is cuda, fp16 should default to True for Tensor Core acceleration."""
    dummy_audio = tmp_path / "audio.ogg"
    dummy_audio.write_bytes(b"dummy ogg content")

    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "Audio transcribed"}

    with patch("transcriber.get_whisper_model", return_value=mock_model) as mock_get_model:
        result = transcriber.transcribe_audio_to_text(
            str(dummy_audio), model_name="base", device="cuda"
        )

        mock_get_model.assert_called_once_with("base", device="cuda")
        mock_model.transcribe.assert_called_once_with(
            str(dummy_audio), fp16=True, language=None
        )
        assert result["text"] == "Audio transcribed"


def test_transcribe_audio_to_text_device_cpu_disables_fp16(tmp_path):
    """When device is cpu, fp16 should default to False to prevent warnings/errors."""
    dummy_audio = tmp_path / "audio.ogg"
    dummy_audio.write_bytes(b"dummy ogg content")

    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "Audio transcribed on cpu"}

    with patch("transcriber.get_whisper_model", return_value=mock_model) as mock_get_model:
        result = transcriber.transcribe_audio_to_text(
            str(dummy_audio), model_name="base", device="cpu"
        )

        mock_get_model.assert_called_once_with("base", device="cpu")
        mock_model.transcribe.assert_called_once_with(
            str(dummy_audio), fp16=False, language=None
        )
        assert result["text"] == "Audio transcribed on cpu"


def test_transcribe_audio_to_text_explicit_fp16_override(tmp_path):
    """User should be able to explicitly override fp16 regardless of device."""
    dummy_audio = tmp_path / "audio.ogg"
    dummy_audio.write_bytes(b"dummy ogg content")

    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "Transcribed"}

    with patch("transcriber.get_whisper_model", return_value=mock_model):
        transcriber.transcribe_audio_to_text(
            str(dummy_audio), model_name="base", device="cuda", fp16=False
        )
        mock_model.transcribe.assert_called_once_with(
            str(dummy_audio), fp16=False, language=None
        )


def test_transcribe_audio_to_text_file_not_found():
    """Should raise FileNotFoundError if audio file does not exist."""
    with pytest.raises(FileNotFoundError):
        transcriber.transcribe_audio_to_text("/non/existent/file.ogg")
