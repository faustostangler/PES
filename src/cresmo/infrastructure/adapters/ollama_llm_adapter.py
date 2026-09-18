"""Local Ollama LLM Infrastructure Adapter.

Implements LLMTransformationPort using local Ollama REST API endpoints (/api/generate, /api/tags)
without external dependencies, providing zero-quota offline conceptual synthesis with actionable
diagnostics when the local daemon is not running.

Conforms to:
    - ADR-001: Modular Monolith Domain Integrity
    - SPEC-001: Core Knowledge Synthesis Specifications
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

from langfuse import Langfuse, observe

from cresmo.application.ports import LLMTransformationPort
from cresmo.domain.exceptions import LLMInfrastructureError

logger = logging.getLogger(__name__)


class OllamaLLMAdapter(LLMTransformationPort):
    """Hexagonal Adapter connecting to a local Ollama daemon for offline LLM transformation.

    Acts as an Anti-Corruption Layer (ACL) shielding domain and application layers from
    urllib HTTP transport anomalies, translating raw socket errors into domain LLMInfrastructureError
    and transmitting telemetry spans to Langfuse.

    Attributes:
        base_url: Root endpoint URL of the Ollama server (e.g. 'http://localhost:11434').
        model: Model tag identifier (e.g. 'qwen2.5:7b').
        timeout_seconds: HTTP socket timeout in seconds.
        default_temperature: Default sampling temperature when not overridden.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b",
        timeout_seconds: float = 60.0,
        default_temperature: float = 0.2,
        num_predict: int = 0,
        langfuse_client: Langfuse | None = None,
    ) -> None:
        """Initialize Ollama LLM adapter.

        Args:
            base_url: Ollama daemon HTTP base endpoint.
            model: Model tag to execute for generation tasks.
            timeout_seconds: Maximum time to wait for generation response before raising.
            default_temperature: Default generation sampling temperature.
            num_predict: Maximum tokens predicted by model (0 means unconstrained / model default).
            langfuse_client: Optional injected Langfuse telemetry client.
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.default_temperature = default_temperature
        self.num_predict = num_predict

        if langfuse_client is not None:
            self._langfuse: Langfuse | None = langfuse_client
        elif os.environ.get("LANGFUSE_PUBLIC_KEY"):
            try:
                self._langfuse = Langfuse()
            except Exception:  # noqa: BLE001
                self._langfuse = None
        else:
            self._langfuse = None

    def is_available(self) -> bool:
        """Check whether local Ollama daemon is reachable and responding.

        Returns:
            True if the /api/tags endpoint responds with HTTP 200 within 2 seconds; False otherwise.
        """
        endpoint = f"{self.base_url}/api/tags"
        req = urllib.request.Request(endpoint, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:  # noqa: BLE001
            return False

    @observe(as_type="generation")
    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Execute text transformation on local Ollama instance with Langfuse telemetry.

        Walkthrough:
            1. Construct JSON payload with model, prompt, system prompt, and options.
            2. Post payload to /api/generate endpoint.
            3. Catch network/connection errors and translate to LLMInfrastructureError with
               an actionable warning instructing the user to run 'ollama serve' or use '--web-index'.
            4. Extract generated response text and emit token usage to Langfuse.

        Args:
            prompt: Text content or prompt for generation.
            system_instruction: Optional system instruction directive.
            temperature: Sampling temperature override. Defaults to self.default_temperature.
            trace_id: Optional trace ID (e.g. ContentId).
            session_id: Pipeline session identifier.
            user_id: Operator or channel identifier.

        Returns:
            Generated text string from the model.

        Raises:
            LLMInfrastructureError: If Ollama daemon is unreachable or returns HTTP error.
        """
        eff_temperature = temperature if temperature is not None else self.default_temperature
        endpoint = f"{self.base_url}/api/generate"
        options: dict[str, Any] = {
            "temperature": eff_temperature,
        }
        if self.num_predict > 0:
            options["num_predict"] = self.num_predict

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        }
        if system_instruction:
            payload["system"] = system_instruction

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
                res_json = json.loads(raw_body)
                generated_text = str(res_json.get("response", "")).strip()

                prompt_tokens = res_json.get("prompt_eval_count") or len(prompt.split())
                candidate_tokens = res_json.get("eval_count") or len(generated_text.split())

                if self._langfuse is not None:
                    try:
                        metadata: dict[str, Any] = {
                            "provider": "ollama",
                            "base_url": self.base_url,
                        }
                        if "total_duration" in res_json:
                            metadata["total_duration_ms"] = res_json["total_duration"] / 1_000_000
                        if "eval_duration" in res_json:
                            metadata["eval_duration_ms"] = res_json["eval_duration"] / 1_000_000
                        if trace_id:
                            metadata["trace_id"] = trace_id
                        if session_id:
                            metadata["session_id"] = session_id
                        if user_id:
                            metadata["user_id"] = user_id

                        self._langfuse.update_current_generation(
                            model=self.model,
                            output=generated_text,
                            usage_details={
                                "input": prompt_tokens,
                                "output": candidate_tokens,
                                "total": prompt_tokens + candidate_tokens,
                            },
                            metadata=metadata,
                        )
                    except Exception as exc:  # noqa: BLE001
                        logger.debug("[OllamaLLMAdapter] Langfuse span update skipped: %s", exc)

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
            raise LLMInfrastructureError(msg) from exc
        except Exception as exc:
            msg = (
                f"Ollama error at {self.base_url}: {exc}. Run 'ollama serve' or pass '--web-index'."
            )
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg) from exc
