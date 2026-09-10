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
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from cresmo_config import (
    CresmoConfig,
    GeminiProviderSettings,
    RetrySettings,
    get_config,
)

_CURRENT_DIR = Path(__file__).parent.resolve()
_WORKSPACE_DIR = _CURRENT_DIR.parent.parent


# --- Standard Non-Secret LLM Configuration (Sourced from Centralized Config) ---
DEFAULT_GEMINI_MODEL: str = "gemini-2.5-flash"
DEFAULT_GEMINI_TEMPERATURE: float = 0.7
DEFAULT_GEMINI_MAX_OUTPUT_TOKENS: int = 65536
DEFAULT_GEMINI_REQUEST_TIMEOUT_SECONDS: float = 180.0
DEFAULT_GEMINI_ENABLE_STREAMING: bool = True


class CresmoLLMConfig(BaseSettings):
    """Configuration for LLM Transformation Port using fail-fast validation.

    Maintained as a typed facade over centralized CresmoConfig for backward compatibility.
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
    retry: RetrySettings = Field(
        default_factory=RetrySettings,
        description="Defensive backoff retry configuration for LLM API calls",
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
    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """Execute text transformation contract given input prompt and optional system directive.

        Args:
            prompt: Text prompt payload to transform.
            system_instruction: Optional system level directive.
            temperature: Optional sampling temperature override (0.0 - 2.0). If None, uses default config.

        Returns:
            Transformed text response.
        """
        raise NotImplementedError


class MockLLMAdapter(LLMTransformationPort):
    """In-memory mock adapter for deterministic testing and decoupled unit test execution."""

    def __init__(self, canned_response: str = "") -> None:
        self.canned_response = canned_response
        self.call_history: list[dict[str, Any]] = []

    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        self.call_history.append({
            "prompt": prompt,
            "system_instruction": system_instruction,
            "temperature": temperature,
            "timestamp": time.time(),
        })
        return self.canned_response


class GeminiAPIAdapter(LLMTransformationPort):
    """Production adapter integrating Google Gemini API via official google-genai SDK."""

    def __init__(
        self,
        config: CresmoConfig | CresmoLLMConfig | GeminiProviderSettings | None = None,
        client: Any | None = None,
    ) -> None:
        if config is None:
            system_config = get_config()
            self.config = CresmoLLMConfig(
                gemini_api_key=system_config.gemini_api_key,
                gemini_model=system_config.llm.gemini.model_name,
                temperature=system_config.llm.gemini.temperature,
                max_output_tokens=system_config.llm.gemini.max_output_tokens,
                request_timeout_seconds=system_config.llm.gemini.request_timeout_seconds,
                enable_streaming=system_config.llm.gemini.enable_streaming,
                retry=system_config.llm.gemini.retry,
            )
        elif isinstance(config, CresmoConfig):
            self.config = CresmoLLMConfig(
                gemini_api_key=config.gemini_api_key,
                gemini_model=config.llm.gemini.model_name,
                temperature=config.llm.gemini.temperature,
                max_output_tokens=config.llm.gemini.max_output_tokens,
                request_timeout_seconds=config.llm.gemini.request_timeout_seconds,
                enable_streaming=config.llm.gemini.enable_streaming,
                retry=config.llm.gemini.retry,
            )
        elif isinstance(config, GeminiProviderSettings):
            system_config = get_config()
            self.config = CresmoLLMConfig(
                gemini_api_key=system_config.gemini_api_key,
                gemini_model=config.model_name,
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                request_timeout_seconds=config.request_timeout_seconds,
                enable_streaming=config.enable_streaming,
                retry=config.retry,
            )
        else:
            self.config = config

        self.total_requests: int = 0
        self.session_prompt_tokens: int = 0
        self.session_candidate_tokens: int = 0
        self.session_total_tokens: int = 0
        if client is not None:
            self._client = client
        else:
            self._client = genai.Client(
                api_key=self.config.gemini_api_key.get_secret_value()
            )

    @staticmethod
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

    def _log_usage_telemetry(
        self,
        elapsed: float,
        usage: Any | None,
        char_len: int,
    ) -> None:
        """Format and print real-time quota and token metrics for the current execution."""
        self.total_requests += 1

        def _safe_int(val: Any) -> int:
            return val if type(val) is int else 0

        raw_prompt = getattr(usage, "prompt_token_count", 0) if usage is not None else 0
        raw_candidate = getattr(usage, "candidates_token_count", 0) if usage is not None else 0
        raw_total = getattr(usage, "total_token_count", 0) if usage is not None else 0

        prompt_tokens = _safe_int(raw_prompt)
        candidate_tokens = _safe_int(raw_candidate)
        total_call_tokens = _safe_int(raw_total) or (prompt_tokens + candidate_tokens)

        self.session_prompt_tokens += prompt_tokens
        self.session_candidate_tokens += candidate_tokens
        self.session_total_tokens += total_call_tokens

        # Known daily free tier caps for visualization
        daily_cap = 1500 if "3.5" in self.config.gemini_model or "2.5" in self.config.gemini_model else 20
        pct_cap = (self.total_requests / daily_cap) * 100

        print(
            f"📊 [Gemini Telemetry] Req #{self.total_requests} ({self.config.gemini_model}) | "
            f"{elapsed:.2f}s | "
            f"Tokens: {prompt_tokens:,} in / {candidate_tokens:,} out ({char_len:,} chars) | "
            f"Session: {self.session_total_tokens:,} tokens | "
            f"Est. Free Quota: {self.total_requests}/{daily_cap} reqs ({pct_cap:.1f}%)",
            flush=True,
        )

    def transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """Transforms text using Gemini API with configurable retry policy and dual-path execution."""
        retry_cfg = getattr(self.config, "retry", None) or RetrySettings()
        retrying = Retrying(
            retry=retry_if_exception_type(Exception),
            stop=stop_after_attempt(retry_cfg.max_attempts),
            wait=wait_exponential(
                multiplier=retry_cfg.multiplier,
                min=retry_cfg.min_seconds,
                max=retry_cfg.max_seconds,
            ),
            before_sleep=self._log_retry_attempt,
            reraise=True,
        )
        return retrying(self._execute_transform, prompt, system_instruction, temperature)

    def _execute_transform(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """Internal execution routine for Gemini generation."""
        import sys

        effective_temperature = self.config.temperature if temperature is None else temperature
        generate_config = types.GenerateContentConfig(
            temperature=effective_temperature,
            max_output_tokens=self.config.max_output_tokens,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        if system_instruction:
            generate_config.system_instruction = system_instruction

        start_time = time.time()
        prompt_preview = prompt.strip()[:30].replace("\n", " ")
        last_usage_metadata: Any | None = None

        if self.config.enable_streaming:
            # Debug path: live streaming chunks to stdout for instant visibility
            print(f"\n📡 [Gemini Stream] Dispatching request #{self.total_requests + 1} to {self.config.gemini_model} ('{prompt_preview}...')", flush=True)
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
                if getattr(chunk, "usage_metadata", None):
                    last_usage_metadata = chunk.usage_metadata
                # Print dot indicator every few chunks
                if chunk_count % 5 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()

            text = "".join(chunks)
            elapsed = time.time() - start_time
            print(f"\n✅ [Gemini Stream] Completed in {elapsed:.2f}s ({len(text)} chars, {chunk_count} chunks)", flush=True)
            self._log_usage_telemetry(elapsed=elapsed, usage=last_usage_metadata, char_len=len(text))
        else:
            # Production path: standard batch execution
            response = self._client.models.generate_content(
                model=self.config.gemini_model,
                contents=prompt,
                config=generate_config,
            )
            elapsed = time.time() - start_time
            text = response.text or ""
            usage = getattr(response, "usage_metadata", None)
            self._log_usage_telemetry(elapsed=elapsed, usage=usage, char_len=len(text))

        if not text.strip():
            raise ValueError(f"Gemini API returned an empty response after {elapsed:.2f}s")

        return text


if __name__ == "__main__":
    print(f"🚀 Initializing GeminiAPIAdapter smoke test with model '{DEFAULT_GEMINI_MODEL}'...")
    adapter = GeminiAPIAdapter()
    sample_prompt = "Synthesize in one concise sentence the definition of Domain-Driven Design."
    output = adapter.transform(sample_prompt)
    print("\n--- Output ---")
    print(output.strip())

