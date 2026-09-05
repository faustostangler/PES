#!/usr/bin/env python3
"""Audio transcriber script using OpenAI Whisper with CUDA acceleration and caching."""

import atexit
import gc
import glob
import os
import sys
import threading
from pathlib import Path
from typing import Any

_MODEL_CACHE: dict[tuple[str, str], Any] = {}
_CACHE_LOCK = threading.Lock()


def get_whisper_model(model_name: str = "base", device: str = "cuda") -> Any:
    """Retrieve a cached Whisper model instance or load it thread-safely.

    Args:
        model_name: Whisper model identifier (e.g. 'tiny', 'base', 'small', 'medium', 'large').
        device: Target execution device ('cuda' or 'cpu').

    Returns:
        Loaded Whisper model instance.
    """
    cache_key = (model_name, device)
    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    with _CACHE_LOCK:
        if cache_key in _MODEL_CACHE:
            return _MODEL_CACHE[cache_key]

        import whisper

        model = whisper.load_model(model_name, device=device)
        _MODEL_CACHE[cache_key] = model
        return model


def unload_whisper_models() -> None:
    """Evacuate all cached Whisper models and reclaim CPU/GPU VRAM."""
    global _MODEL_CACHE
    with _CACHE_LOCK:
        _MODEL_CACHE.clear()
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass


atexit.register(unload_whisper_models)


def transcribe_audio_to_text(
    audio_path: str,
    model_name: str = "base",
    language: str | None = None,
    device: str | None = None,
    fp16: bool | None = None,
) -> dict:
    """Transcribe an audio file to text using Whisper with caching and FP16 support.

    Args:
        audio_path: Path to the audio file (e.g. .ogg).
        model_name: The Whisper model size/name to use (e.g., 'tiny', 'base', 'small', 'medium', 'large').
        language: Optional language code to force Whisper to use (e.g., 'pt', 'en').
        device: Optional execution device ('cuda' or 'cpu'). Defaults to CUDA if available.
        fp16: Optional boolean enabling FP16 half precision. Defaults to True on CUDA and False on CPU.

    Returns:
        A dictionary containing the transcription text and other metadata segments.
    """
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if device is None:
        try:
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"

    if fp16 is None:
        fp16 = device == "cuda"

    model = get_whisper_model(model_name, device=device)
    result = model.transcribe(str(path), fp16=fp16, language=language)

    return result


if __name__ == "__main__":
    # Quick CLI invocation test if run directly
    audio_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not audio_path:
        print("No audio file path provided via command line.")

        # Scan for existing audio files to make selection easy
        downloads_dir = Path(__file__).parent / "downloads"
        if not downloads_dir.exists():
            downloads_dir = Path("./downloads")

        files = []
        if downloads_dir.exists():
            for ext in ("*.ogg", "*.mp3", "*.wav", "*.m4a"):
                files.extend(glob.glob(str(downloads_dir / ext)))

        if files:
            print(f"Available audio files in {downloads_dir}:")
            for i, f in enumerate(files):
                print(f"  [{i}] {Path(f).name}")
            try:
                choice = input(f"Select file index (0-{len(files)-1}) or enter custom path: ").strip()
                if choice.isdigit() and 0 <= int(choice) < len(files):
                    audio_path = files[int(choice)]
                elif choice:
                    audio_path = choice
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)
        else:
            try:
                audio_path = input("Enter path to audio file: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)

    if not audio_path or not os.path.exists(audio_path):
        print(f"Error: Invalid or non-existent audio file: {audio_path}")
        sys.exit(1)

    res = transcribe_audio_to_text(audio_path)
    print("\nTranscription Result:")
    print(res.get("text", ""))
