"""Local Ollama LLM Infrastructure Adapter.

Implements LLMTransformationPort using local Ollama REST API endpoints (/api/chat, /api/generate, /api/ps)
without external dependencies, providing zero-quota offline conceptual synthesis with actionable
diagnostics when the local daemon is not running.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - ADR-065: Hierarchical Stage-Scoped Telemetry Nomenclature
    - ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
    - SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from typing import Any, Final

import structlog

from cresmo.application.ports import (
    LLMTransformationPort,
    NoOpTelemetryPort,
    SpanKind,
    TelemetryPort,
    resolve_llm_generation_span_name,
)
from cresmo.domain.exceptions import LLMInfrastructureError
from cresmo.domain.value_objects import ChatPrompt
from cresmo.infrastructure.adapters.telemetry.genai import build_genai_attributes

__all__ = ["OllamaLLMAdapter"]

logger = structlog.get_logger(__name__)

DEFAULT_HEALTHCHECK_TIMEOUT_SECONDS: Final[float] = 2.0
DEFAULT_OLLAMA_BASE_URL: Final[str] = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL: Final[str] = "qwen2.5:7b"
DEFAULT_OLLAMA_TIMEOUT_SECONDS: Final[float] = 60.0
DEFAULT_OLLAMA_TEMPERATURE: Final[float] = 0.2
DEFAULT_OLLAMA_KEEP_ALIVE: Final[str] = "1h"
DEFAULT_OLLAMA_WARMUP_TIMEOUT_SECONDS: Final[float] = 300.0
_URL_TRAILING_SLASH: Final[str] = "/"
_OLLAMA_PS_PATH: Final[str] = "/api/ps"
_OLLAMA_GENERATE_PATH: Final[str] = "/api/generate"
_OLLAMA_CHAT_PATH: Final[str] = "/api/chat"
_HTTP_GET_METHOD: Final[str] = "GET"
_HTTP_POST_METHOD: Final[str] = "POST"
_CONTENT_TYPE_HEADER: Final[str] = "Content-Type"
_CONTENT_TYPE_JSON: Final[str] = "application/json"
_UTF8_ENCODING: Final[str] = "utf-8"
_BYTES_PER_MIB: Final[int] = 1024 * 1024
_MODEL_TAG_SEPARATOR: Final[str] = ":"
_DONE_REASON_LOAD: Final[str] = "load"
_WARMUP_THREAD_NAME_PREFIX: Final[str] = "OllamaWarmupThread-"
_OLLAMA_SYSTEM_NAME: Final[str] = "ollama"
_KEY_MODELS: Final[str] = "models"
_KEY_NAME: Final[str] = "name"
_KEY_SIZE_VRAM: Final[str] = "size_vram"
_KEY_MODEL: Final[str] = "model"
_KEY_KEEP_ALIVE: Final[str] = "keep_alive"
_KEY_DONE_REASON: Final[str] = "done_reason"
_KEY_TEMPERATURE: Final[str] = "temperature"
_KEY_NUM_PREDICT: Final[str] = "num_predict"
_KEY_MESSAGES: Final[str] = "messages"
_KEY_STREAM: Final[str] = "stream"
_KEY_OPTIONS: Final[str] = "options"
_KEY_MESSAGE: Final[str] = "message"
_KEY_CONTENT: Final[str] = "content"
_KEY_PROMPT_EVAL_COUNT: Final[str] = "prompt_eval_count"
_KEY_EVAL_COUNT: Final[str] = "eval_count"


class OllamaLLMAdapter(LLMTransformationPort):
    """Hexagonal Adapter connecting to a local Ollama daemon for offline LLM transformation.

    Acts as an Anti-Corruption Layer (ACL) shielding domain and application layers from
    urllib HTTP transport anomalies, translating raw socket errors into domain LLMInfrastructureError
    and recording generation telemetry spans through TelemetryPort.

    Attributes:
        base_url: Root endpoint URL of the Ollama server (e.g. 'http://localhost:11434').
        model: Model tag identifier (e.g. 'qwen2.5:7b').
        timeout_seconds: HTTP socket timeout in seconds.
        default_temperature: Default sampling temperature when not overridden.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        model: str = DEFAULT_OLLAMA_MODEL,
        timeout_seconds: float = DEFAULT_OLLAMA_TIMEOUT_SECONDS,
        default_temperature: float = DEFAULT_OLLAMA_TEMPERATURE,
        num_predict: int = 0,
        telemetry_port: TelemetryPort | None = None,
        keep_alive: str = DEFAULT_OLLAMA_KEEP_ALIVE,
        warmup_timeout_seconds: float = DEFAULT_OLLAMA_WARMUP_TIMEOUT_SECONDS,
    ) -> None:
        """Initialize Ollama LLM adapter with model settings and injected TelemetryPort.

        Args:
            base_url: Ollama daemon HTTP base endpoint.
            model: Model tag to execute for generation tasks.
            timeout_seconds: Maximum time to wait for generation response before raising.
            default_temperature: Default generation sampling temperature.
            num_predict: Maximum tokens predicted by model (0 means unconstrained / model default).
            telemetry_port: Optional injected Hexagonal TelemetryPort (defaults to NoOpTelemetryPort).
            keep_alive: Duration to keep model in VRAM/RAM (e.g. '1h', '60m', '-1' for indefinite).
            warmup_timeout_seconds: Extended socket timeout in seconds for initial model preload.
        """
        self.base_url = base_url.rstrip(_URL_TRAILING_SLASH)
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.default_temperature = default_temperature
        self.num_predict = num_predict
        self.keep_alive = keep_alive
        self.warmup_timeout_seconds = warmup_timeout_seconds
        self._is_warmed_up = False
        self._warmup_event = threading.Event()
        self._warmup_lock = threading.RLock()
        self._warmup_thread: threading.Thread | None = None
        self._warmup_error: Exception | None = None
        self._telemetry: TelemetryPort = telemetry_port or NoOpTelemetryPort()

    @property
    def is_warmed_up(self) -> bool:
        """Return True if model weights are confirmed to be loaded in memory."""
        with self._warmup_lock:
            return self._is_warmed_up

    def _probe_gpu_status(self) -> None:
        """Probe /api/ps to detect CPU-only inference and emit an actionable WARNING.

        Queries the Ollama process-status endpoint immediately after warmup to inspect
        ``size_vram`` for the active model. A value of 0 indicates the model is running
        entirely on CPU RAM, which will cause significantly longer inference times.

        Why: NVIDIA driver failures (e.g. broken nvidia-smi, missing kernel module) silently
        demote Ollama to CPU-only mode without any error at the API level. This probe surfaces
        that degradation proactively so operators can act before inference timeouts occur.
        """
        endpoint = f"{self.base_url}{_OLLAMA_PS_PATH}"
        req = urllib.request.Request(endpoint, method=_HTTP_GET_METHOD)
        try:
            with urllib.request.urlopen(
                req, timeout=DEFAULT_HEALTHCHECK_TIMEOUT_SECONDS
            ) as response:
                if response.status != HTTPStatus.OK:
                    return
                ps_data: dict[str, Any] = json.loads(response.read().decode(_UTF8_ENCODING))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            logger.debug("[OllamaLLMAdapter] GPU status probe failed (non-fatal): %s", exc)
            return

        models: list[dict[str, Any]] = ps_data.get(_KEY_MODELS, [])
        active = next(
            (
                m
                for m in models
                if m.get(_KEY_NAME, "").startswith(self.model.split(_MODEL_TAG_SEPARATOR)[0])
            ),
            None,
        )
        if active is None:
            # Model may not appear in /api/ps if it just finished loading; skip silently.
            return

        size_vram: int = active.get(_KEY_SIZE_VRAM, 0)
        if size_vram == 0:
            logger.warning(
                "[OllamaLLMAdapter] ⚠️  GPU probe: model '%s' is running on CPU RAM only "
                "(size_vram=0). Inference will be significantly slower (300 s+ per request). "
                "Fix NVIDIA drivers with 'sudo nvidia-smi' and restart Ollama to re-enable GPU.",
                self.model,
            )
        else:
            logger.info(
                "[OllamaLLMAdapter] ✅ GPU probe: model '%s' loaded in VRAM (%.1f MB).",
                self.model,
                size_vram / _BYTES_PER_MIB,
            )

    def _execute_warmup(self, effective_timeout: float) -> bool:
        """Execute synchronous model preload against /api/generate."""
        with self._warmup_lock:
            if self._is_warmed_up:
                return True

        endpoint = f"{self.base_url}{_OLLAMA_GENERATE_PATH}"
        payload: dict[str, Any] = {
            _KEY_MODEL: self.model,
            _KEY_KEEP_ALIVE: self.keep_alive,
        }
        data = json.dumps(payload).encode(_UTF8_ENCODING)
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={_CONTENT_TYPE_HEADER: _CONTENT_TYPE_JSON},
            method=_HTTP_POST_METHOD,
        )

        start_time = time.perf_counter()
        logger.info(
            "[OllamaLLMAdapter] Preloading model '%s' at %s (keep_alive: %s, timeout: %.0fs)...",
            self.model,
            self.base_url,
            self.keep_alive,
            effective_timeout,
        )

        try:
            with urllib.request.urlopen(req, timeout=effective_timeout) as response:
                if response.status == HTTPStatus.OK:
                    raw_body = response.read().decode(_UTF8_ENCODING)
                    response_json = json.loads(raw_body)
                    duration = time.perf_counter() - start_time
                    done_reason = response_json.get(_KEY_DONE_REASON, _DONE_REASON_LOAD)
                    logger.info(
                        "[OllamaLLMAdapter] Model '%s' successfully loaded into memory in %.2fs (reason: %s).",
                        self.model,
                        duration,
                        done_reason,
                    )
                    with self._warmup_lock:
                        self._is_warmed_up = True
                    self._probe_gpu_status()
                    return True
                return False
        except urllib.error.HTTPError as exc:
            if exc.code == HTTPStatus.NOT_FOUND:
                msg = f"Model '{self.model}' not found in Ollama (HTTP 404) at {self.base_url}. Run 'ollama pull {self.model}'."
            else:
                msg = f"Ollama HTTP {exc.code} during warmup at {self.base_url}: {exc.reason}."
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg) from exc
        except TimeoutError as exc:
            msg = f"Ollama timed out loading model '{self.model}' after {effective_timeout:.0f}s. Check system RAM/VRAM."
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg) from exc
        except urllib.error.URLError as exc:
            if isinstance(getattr(exc, "reason", None), TimeoutError):
                msg = f"Ollama timed out loading model '{self.model}' after {effective_timeout:.0f}s. Check system RAM/VRAM."
            else:
                msg = f"Ollama unreachable at {self.base_url}. Run 'ollama serve' or pass '--web-index'."
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg) from exc
        except Exception as exc:
            msg = f"Ollama warmup error at {self.base_url}: {exc}."
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg) from exc

    def _dispatch_warmup_locked(self, timeout_seconds: float | None = None) -> None:
        """Internal helper to dispatch background thread while holding _warmup_lock."""
        if self._is_warmed_up:
            return
        if self._warmup_thread is not None and self._warmup_thread.is_alive():
            return

        effective_timeout = (
            timeout_seconds if timeout_seconds is not None else self.warmup_timeout_seconds
        )
        self._warmup_event.clear()
        self._warmup_error = None

        def _background_worker() -> None:
            try:
                self._execute_warmup(effective_timeout)
            except Exception as exc:  # noqa: BLE001
                with self._warmup_lock:
                    self._warmup_error = exc
            finally:
                self._warmup_event.set()

        self._warmup_thread = threading.Thread(
            target=_background_worker,
            name=f"{_WARMUP_THREAD_NAME_PREFIX}{self.model}",
            daemon=True,
        )
        self._warmup_thread.start()
        logger.info(
            "[OllamaLLMAdapter] Dispatched asynchronous background warmup for model '%s' (keep_alive: %s)...",
            self.model,
            self.keep_alive,
        )

    def warmup(self) -> None:
        """Asynchronously preload model weights in background daemon thread.

        Dispatches model weight preloading onto a background daemon thread without blocking,
        allowing file parsing, directory scanning, and channel crawling to execute concurrently.
        """
        with self._warmup_lock:
            self._dispatch_warmup_locked()

    def _wait_for_warmup(self, timeout_seconds: float | None = None) -> bool:
        """Wait at the rendezvous barrier until model warmup completes.

        If background warmup is currently in progress, blocks until weights are in VRAM.
        If warmup has already completed, returns immediately with zero overhead.
        If warmup was never triggered, dispatches and awaits it automatically.

        Args:
            timeout_seconds: Extended socket timeout for model loading (defaults to self.warmup_timeout_seconds).

        Returns:
            True if model was successfully loaded into memory; False otherwise.

        Raises:
            LLMInfrastructureError: If Ollama returns HTTP 404 (model missing) or daemon unreachable.
        """
        with self._warmup_lock:
            if self._is_warmed_up:
                return True
            if self._warmup_thread is None:
                self._dispatch_warmup_locked(timeout_seconds)

        effective_timeout = (
            timeout_seconds if timeout_seconds is not None else self.warmup_timeout_seconds
        )
        completed = self._warmup_event.wait(timeout=effective_timeout)
        if not completed:
            msg = (
                f"Ollama timed out waiting for background warmup of model '{self.model}' "
                f"after {effective_timeout:.0f}s. Check system RAM/VRAM."
            )
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg)

        with self._warmup_lock:
            if self._warmup_error is not None:
                raise self._warmup_error
            return self._is_warmed_up

    def transform(
        self,
        prompt: ChatPrompt,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation on local Ollama instance inside a TelemetryPort generation span.

        Args:
            prompt: Domain ChatPrompt containing sequential messages and optional system instruction.
            temperature: Sampling temperature override. Defaults to self.default_temperature.
            trace_id: Optional trace ID (e.g. ContentId).
            session_id: Pipeline session identifier.
            user_id: Operator or channel identifier.

        Returns:
            Generated text string from the model.

        Raises:
            LLMInfrastructureError: If Ollama daemon is unreachable or returns HTTP error.
        """
        span_name = resolve_llm_generation_span_name(fallback=False)

        with self._telemetry.start_span(span_name, kind=SpanKind.GENERATION) as span:
            if not self._is_warmed_up:
                self._wait_for_warmup()

            effective_temperature = (
                temperature if temperature is not None else self.default_temperature
            )
            endpoint = f"{self.base_url}{_OLLAMA_CHAT_PATH}"
            options: dict[str, Any] = {_KEY_TEMPERATURE: effective_temperature}
            if self.num_predict > 0:
                options[_KEY_NUM_PREDICT] = self.num_predict

            messages = prompt.to_dict_list()
            span.set_input(messages)

            payload: dict[str, Any] = {
                _KEY_MODEL: self.model,
                _KEY_MESSAGES: messages,
                _KEY_STREAM: False,
                _KEY_KEEP_ALIVE: self.keep_alive,
                _KEY_OPTIONS: options,
            }

            data = json.dumps(payload).encode(_UTF8_ENCODING)
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={_CONTENT_TYPE_HEADER: _CONTENT_TYPE_JSON},
                method=_HTTP_POST_METHOD,
            )

            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                    raw_body = response.read().decode(_UTF8_ENCODING)
                    response_json = json.loads(raw_body)
                    msg_obj = response_json.get(_KEY_MESSAGE)
                    generated_text = (
                        str(msg_obj.get(_KEY_CONTENT, "")).strip()
                        if isinstance(msg_obj, dict)
                        else ""
                    )

                    total_prompt_words = sum(len(m.content.split()) for m in prompt.messages)
                    prompt_tokens = response_json.get(_KEY_PROMPT_EVAL_COUNT) or total_prompt_words
                    candidate_tokens = response_json.get(_KEY_EVAL_COUNT) or len(
                        generated_text.split()
                    )

                    span.set_attributes(
                        build_genai_attributes(
                            system=_OLLAMA_SYSTEM_NAME,
                            model=self.model,
                            prompt_tokens=prompt_tokens,
                            candidate_tokens=candidate_tokens,
                            session_id=session_id,
                            user_id=user_id,
                            trace_id=trace_id,
                        )
                    )
                    span.set_output(generated_text)
                    return generated_text

            except TimeoutError as exc:
                msg = (
                    f"Ollama timed out at {self.base_url} ({self.timeout_seconds:.0f}s). "
                    "Run 'ollama serve' or pass '--web-index'."
                )
                logger.warning("[OllamaLLMAdapter] %s", msg)
                raise LLMInfrastructureError(msg) from exc
            except urllib.error.HTTPError as exc:
                msg = (
                    f"Ollama HTTP {exc.code} at {self.base_url}: {exc.reason}. "
                    "Run 'ollama list' to verify model."
                )
                logger.warning("[OllamaLLMAdapter] %s", msg)
                raise LLMInfrastructureError(msg) from exc
            except urllib.error.URLError as exc:
                if isinstance(getattr(exc, "reason", None), TimeoutError):
                    msg = (
                        f"Ollama timed out at {self.base_url} ({self.timeout_seconds:.0f}s). "
                        "Run 'ollama serve' or pass '--web-index'."
                    )
                else:
                    msg = (
                        f"Ollama unreachable at {self.base_url}. "
                        "Run 'ollama serve' or pass '--web-index'."
                    )
                logger.warning("[OllamaLLMAdapter] %s", msg)
                raise LLMInfrastructureError(msg) from exc
            except Exception as exc:
                msg = (
                    f"Ollama error at {self.base_url}: {exc}. "
                    "Run 'ollama serve' or pass '--web-index'."
                )
                logger.warning("[OllamaLLMAdapter] %s", msg)
                raise LLMInfrastructureError(msg) from exc
