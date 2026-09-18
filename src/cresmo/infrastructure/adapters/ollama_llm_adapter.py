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
import urllib.error
import urllib.request
from typing import Any

from cresmo.application.ports import LLMTransformationPort
from cresmo.domain.exceptions import LLMInfrastructureError

logger = logging.getLogger(__name__)


class OllamaLLMAdapter(LLMTransformationPort):
    """Hexagonal Adapter connecting to a local Ollama daemon for offline LLM transformation.

    Acts as an Anti-Corruption Layer (ACL) shielding domain and application layers from
    urllib HTTP transport anomalies, translating raw socket errors into domain LLMInfrastructureError.

    Attributes:
        base_url: Root endpoint URL of the Ollama server (e.g. 'http://localhost:11434').
        model: Model tag identifier (e.g. 'qwen2.5:7b').
        timeout_seconds: HTTP socket timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b",
        timeout_seconds: float = 60.0,
    ) -> None:
        """Initialize Ollama LLM adapter.

        Args:
            base_url: Ollama daemon HTTP base endpoint.
            model: Model tag to execute for generation tasks.
            timeout_seconds: Maximum time to wait for generation response before raising.
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

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

        Args:
            prompt: Text content or prompt for generation.
            system_instruction: Optional system instruction directive.
            temperature: Sampling temperature parameter. Defaults to 0.2.

        Returns:
            Generated text string from the model.

        Raises:
            LLMInfrastructureError: If Ollama daemon is unreachable or returns HTTP error.
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
