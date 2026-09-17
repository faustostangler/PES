"""Local Ollama LLM Infrastructure Adapter.

Implements LLMTransformationPort using local Ollama REST API endpoints (/api/generate, /api/tags)
without external dependencies, providing zero-quota offline conceptual synthesis with actionable
diagnostics when the local daemon is not running.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from cresmo.application.ports import LLMTransformationPort
from cresmo.domain.exceptions import LLMInfrastructureError

logger = logging.getLogger(__name__)


class OllamaLLMAdapter(LLMTransformationPort):
    """Hexagonal Adapter connecting to a local Ollama daemon for offline LLM transformation."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        """Check whether local Ollama daemon is reachable and responding."""
        endpoint = f"{self.base_url}/api/tags"
        req = urllib.request.Request(endpoint, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:  # noqa: BLE001
            return False

    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """Execute text transformation on local Ollama instance.

        Walkthrough:
        1. Construct JSON payload with model, prompt, system prompt, and options.
        2. Post payload to /api/generate endpoint.
        3. Catch network/connection errors and translate to LLMInfrastructureError with
           an actionable warning instructing the user to run 'ollama serve' or use '--web-index'.
        4. Extract and return generated response text.
        """
        endpoint = f"{self.base_url}/api/generate"
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else 0.2,
                "num_predict": 300,
            },
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
                return str(res_json.get("response", "")).strip()
        except urllib.error.URLError as exc:
            msg = (
                f"Ollama is unreachable at {self.base_url} ({exc}). "
                "Please start the local service with 'ollama serve' (or 'ollama run <model>'), "
                "or pass '--web-index' to use the Gemini cloud API."
            )
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg) from exc
        except urllib.error.HTTPError as exc:
            msg = (
                f"Ollama HTTP error {exc.code} at {self.base_url}: {exc.reason}. "
                "Verify model exists using 'ollama list'."
            )
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg) from exc
        except Exception as exc:
            msg = f"Unexpected error communicating with Ollama at {self.base_url}: {exc}"
            logger.warning("[OllamaLLMAdapter] %s", msg)
            raise LLMInfrastructureError(msg) from exc
