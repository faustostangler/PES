"""Faster-Whisper CTranslate2 speech-to-text transcription engine.

Conforms to:
    - ADR-053: Lazy Presentation CLI Loading (zero top-level ML imports)
    - ADR-075: High-Throughput Native Media Ingestion (FasterWhisperEngine)
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from cresmo.domain.exceptions import CresmoInfrastructureError


class FasterWhisperEngine:
    """Lazy-loaded, thread-safe CTranslate2 Whisper transcription adapter."""

    def __init__(
        self,
        concurrency_limit: int = 2,
        device: str = "auto",
        compute_type: str = "auto",
        vad_filter: bool = True,
    ) -> None:
        """Initialize FasterWhisperEngine without eagerly loading CTranslate2/faster-whisper.

        Args:
            concurrency_limit: Maximum concurrent transcription executions.
            device: Target inference device ('auto', 'cpu', or 'cuda').
            compute_type: CTranslate2 quantization/precision mode ('auto', 'int8', 'float16', etc.).
            vad_filter: Whether to enable Silero VAD filtering during transcription.
        """
        self._semaphore = threading.BoundedSemaphore(max(1, concurrency_limit))
        self._device = device
        self._compute_type = compute_type
        self._vad_filter = vad_filter
        self._cache_lock = threading.Lock()
        self._model_cache: dict[tuple[str, str, str], Any] = {}

    def resolve_device(self) -> str:
        """Resolve execution device, probing CTranslate2 CUDA count when set to 'auto'."""
        if self._device != "auto":
            return self._device
        try:
            import ctranslate2

            if int(ctranslate2.get_cuda_device_count()) > 0:
                return "cuda"
        except Exception:  # noqa: BLE001 - Graceful fallback to CPU when CUDA probe fails
            return "cpu"
        return "cpu"

    def resolve_compute_type(self, resolved_device: str) -> str:
        """Resolve CTranslate2 compute type for the target device."""
        if self._compute_type != "auto":
            return self._compute_type
        return "float16" if resolved_device == "cuda" else "int8"

    def _get_or_load_model(self, model_name: str, device: str, compute_type: str) -> Any:
        """Retrieve cached WhisperModel instance or lazily construct one under thread lock."""
        cache_key = (model_name, device, compute_type)
        with self._cache_lock:
            cached = self._model_cache.get(cache_key)
            if cached is not None:
                return cached

            from faster_whisper import WhisperModel  # Lazy ML runtime import per ADR-053/ADR-075

            model = WhisperModel(model_name, device=device, compute_type=compute_type)
            self._model_cache[cache_key] = model
            return model

    def transcribe(self, audio_path: Path, model_name: str) -> str:
        """Transcribe an audio file using a cached WhisperModel under semaphore control."""
        try:
            with self._semaphore:
                resolved_device = self.resolve_device()
                resolved_compute_type = self.resolve_compute_type(resolved_device)
                model = self._get_or_load_model(
                    model_name=model_name,
                    device=resolved_device,
                    compute_type=resolved_compute_type,
                )
                segments, _ = model.transcribe(str(audio_path), vad_filter=self._vad_filter)
                parts = [str(segment.text).strip() for segment in segments]
                return " ".join(part for part in parts if part).strip()
        except Exception as exc:
            raise CresmoInfrastructureError(f"Whisper transcription failed: {exc}") from exc
