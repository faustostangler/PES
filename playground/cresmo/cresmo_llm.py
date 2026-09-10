"""Hexagonal Port and Adapters for Cresmo LLM Transformations.

Defines the domain port (LLMTransformationPort) for synchronous text generation
and the infrastructure adapter (GeminiAPIAdapter) utilizing the google-genai SDK,
with fail-fast configuration validation and exponential backoff retry.
"""

from abc import ABC, abstractmethod
import os
from pathlib import Path
import time
from typing import Any

from google import genai
from google.genai import types
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

_CURRENT_DIR = Path(__file__).parent.resolve()
_WORKSPACE_DIR = _CURRENT_DIR.parent.parent


# --- Standard Non-Secret LLM Configuration (Committed to Version Control) ---
DEFAULT_GEMINI_MODEL: str = "gemini-3.5-flash"  # or gemini-3.7-flash; default: gemini-3.8-flash
DEFAULT_GEMINI_TEMPERATURE: float = 0.7  # default: 0.2; lower is more deterministic/less creative
DEFAULT_GEMINI_MAX_OUTPUT_TOKENS: int = 65536  # default: 65536; max
DEFAULT_GEMINI_REQUEST_TIMEOUT_SECONDS: float = 180.0  # default: 180.0
DEFAULT_GEMINI_ENABLE_STREAMING: bool = True  # default: True for debug; False for prod


class CresmoLLMConfig(BaseSettings):
    """Configuration for LLM Transformation Port using fail-fast validation.

    Distinguishes strictly between secrets (GEMINI_API_KEY from .env / environment)
    and behavioral configuration parameters (defaults defined as version-controlled constants).
    """

    # --- Secret: Loaded exclusively from .env or environment variable ---
    gemini_api_key: SecretStr = Field(
        ...,
        alias="GEMINI_API_KEY",
        validation_alias="GEMINI_API_KEY",
        description="Google AI Studio Gemini API Key (Secret)",
    )

    # --- Non-Secret Behavioral Configurations (Safe for Git) ---
    gemini_model: str = Field(
        default=DEFAULT_GEMINI_MODEL,
        alias="GEMINI_MODEL",
        validation_alias="GEMINI_MODEL",
        description="Target Gemini model identifier",
    )
    temperature: float = Field(
        default=DEFAULT_GEMINI_TEMPERATURE,
        alias="GEMINI_TEMPERATURE",
        validation_alias="GEMINI_TEMPERATURE",
        description="Sampling temperature for LLM generation",
    )
    max_output_tokens: int = Field(
        default=DEFAULT_GEMINI_MAX_OUTPUT_TOKENS,
        alias="GEMINI_MAX_OUTPUT_TOKENS",
        validation_alias="GEMINI_MAX_OUTPUT_TOKENS",
        description="Maximum tokens allowed in generation response",
    )
    request_timeout_seconds: float = Field(
        default=DEFAULT_GEMINI_REQUEST_TIMEOUT_SECONDS,
        alias="GEMINI_REQUEST_TIMEOUT",
        validation_alias="GEMINI_REQUEST_TIMEOUT",
        description="Client request timeout in seconds",
    )
    enable_streaming: bool = Field(
        default=DEFAULT_GEMINI_ENABLE_STREAMING,
        alias="GEMINI_ENABLE_STREAMING",
        validation_alias="GEMINI_ENABLE_STREAMING",
        description="Enable live token streaming for debug visibility into generation progress",
    )

    model_config = SettingsConfigDict(
        env_file=(
            str(_CURRENT_DIR / ".env"),
            str(_WORKSPACE_DIR / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


class LLMTransformationPort(ABC):
    """Port interface defining transformation contracts for Cresmo pipeline stages."""

    @abstractmethod
    def transform(self, prompt: str, system_instruction: str | None = None) -> str:
        """Execute text transformation contract given input prompt and optional system directive."""
        raise NotImplementedError


class MockLLMAdapter(LLMTransformationPort):
    """In-memory mock adapter for deterministic testing and decoupled unit test execution."""

    def __init__(self, canned_response: str = "") -> None:
        self.canned_response = canned_response
        self.call_history: list[dict[str, Any]] = []

    def transform(self, prompt: str, system_instruction: str | None = None) -> str:
        self.call_history.append({
            "prompt": prompt,
            "system_instruction": system_instruction,
            "timestamp": time.time(),
        })
        return self.canned_response


class GeminiAPIAdapter(LLMTransformationPort):
    """Production adapter integrating Google Gemini API via official google-genai SDK."""

    def __init__(
        self,
        config: CresmoLLMConfig | None = None,
        client: Any | None = None,
    ) -> None:
        self.config = config or CresmoLLMConfig()
        if client is not None:
            self._client = client
        else:
            self._client = genai.Client(
                api_key=self.config.gemini_api_key.get_secret_value()
            )

    def _log_retry_attempt(retry_state: Any) -> None:
        exception = retry_state.outcome.exception() if retry_state.outcome else None
        attempt = retry_state.attempt_number
        next_action = retry_state.next_action
        sleep_time = next_action.sleep if next_action else 0.0
        print(
            f"⚠️ [Gemini Retry] Attempt {attempt} failed with: {exception}. "
            f"Retrying in {sleep_time:.1f}s...",
            flush=True,
        )

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(7),
        wait=wait_exponential(multiplier=2.0, min=2, max=60),
        before_sleep=_log_retry_attempt,
        reraise=True,
    )
    def transform(self, prompt: str, system_instruction: str | None = None) -> str:
        """Transforms text using Gemini API with dual-path execution (streaming debug vs batch prod)."""
        import sys

        generate_config = types.GenerateContentConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        if system_instruction:
            generate_config.system_instruction = system_instruction

        start_time = time.time()
        prompt_preview = prompt.strip()[:20].replace("\n", " ")

        if self.config.enable_streaming:
            # Debug path: live streaming chunks to stdout for instant visibility
            print(f"\n📡 [Gemini Stream] Dispatching request to {self.config.gemini_model} ('{prompt_preview}...')", flush=True)
            chunks: list[str] = []
            chunk_count = 0
            for chunk in self._client.models.generate_content_stream(
                model=self.config.gemini_model,
                contents=prompt,
                config=generate_config,
            ):
                chunk_text = chunk.text or ""
                chunks.append(chunk_text)
                chunk_count += 1
                # Print dot indicator or live progress every few chunks
                if chunk_count % 5 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()

            text = "".join(chunks)
            elapsed = time.time() - start_time
            print(f"\n✅ [Gemini Stream] Completed in {elapsed:.2f}s ({len(text)} chars, {chunk_count} chunks)", flush=True)
        else:
            # Production path: standard batch execution
            response = self._client.models.generate_content(
                model=self.config.gemini_model,
                contents=prompt,
                config=generate_config,
            )
            elapsed = time.time() - start_time
            text = response.text or ""

        if not text.strip():
            raise ValueError(f"Gemini API returned an empty response after {elapsed:.2f}s")

        return text
