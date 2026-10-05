"""Langfuse Prompt Provider Adapter.

Conforms to ADR-014 and ADR-017:
    - When Langfuse is reachable, retrieves versioned prompts and configs from Langfuse Cloud.
    - Guaranteed Availability: When Langfuse is offline, unreachable, or fails, falls back immediately
      to the injected JsonPromptProvider with zero pipeline downtime.
    - Tracks active prompt object/version for linking to LLM generation observations.
    - Uses canonical PROMPT_REGISTRY to eliminate duplicated hardcoded prompt names.
"""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

from langfuse.api.core import ApiError

from cresmo.application.ports import PromptProviderPort
from cresmo.domain.value_objects import ChannelName
from cresmo.infrastructure.adapters.prompts.registry import (
    PROMPT_REGISTRY,
    PromptKey,
)
from cresmo.infrastructure.config import CresmoSettings

logger = logging.getLogger(__name__)


def _handle_api_error(exc: ApiError, prompt_name: str, label: str) -> None:
    """Log structured warning for Langfuse API errors."""
    if exc.status_code == HTTPStatus.NOT_FOUND:
        logger.warning(
            "[LangfusePromptProvider] Prompt '%s' not found in Langfuse (404). "
            "Create it in Langfuse Cloud or use label='%s'. Using local fallback.",
            prompt_name,
            label,
        )
    else:
        logger.warning(
            "[LangfusePromptProvider] Langfuse API error fetching '%s' (HTTP %s: %s). "
            "Using local fallback.",
            prompt_name,
            exc.status_code,
            exc.body,
        )


def _extract_prompt_messages(
    compiled_messages: Any,
    kwargs: dict[str, Any],
) -> tuple[str, str]:
    """Extract system instruction and user prompt from compiled Langfuse chat messages.

    Raises:
        TypeError: If compiled_messages is not a list.
        ValueError: If compiled_messages does not contain both system and user role messages.
    """
    if not isinstance(compiled_messages, list):
        raise TypeError(
            f"Expected compiled_messages to be a list, got {type(compiled_messages).__name__}"
        )

    system_instruction: str | None = None
    user_prompt: str | None = None
    for msg in compiled_messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        content = msg.get("content")
        if content is None:
            continue
        if role == "system":
            system_instruction = str(content)
        elif role == "user":
            user_prompt = str(content)

    if system_instruction is None or user_prompt is None:
        raise ValueError(
            "Langfuse chat prompt structure must contain both 'system' and 'user' role messages"
        )

    for key, value in kwargs.items():
        user_prompt = user_prompt.replace(f"{{{key}}}", str(value))
        system_instruction = system_instruction.replace(f"{{{key}}}", str(value))

    return system_instruction, user_prompt


class LangfusePromptProvider(PromptProviderPort):
    """Hexagonal Adapter providing prompts via Langfuse with guaranteed local fallback.

    Conforms to ADR-014, ADR-017, and ADR-026 (Rule 19):
        - When Langfuse is reachable, retrieves versioned prompts and configs.
        - Strict Lazy Degradation: Fallback provider is NEVER executed on the happy path.
        - Guaranteed Availability: When Langfuse is offline or fails, falls back immediately
          to the injected JsonPromptProvider with zero pipeline downtime.
        - Tracks active prompt object/version for linking to LLM generation observations.
    """

    def __init__(
        self,
        langfuse_client: Any | None,
        fallback_provider: PromptProviderPort,
        label: str = CresmoSettings.DEFAULT_LANGFUSE_PROMPT_LABEL,
    ) -> None:
        """Initialize Langfuse prompt provider.

        Args:
            langfuse_client: Optional active Langfuse client instance.
            fallback_provider: Injected local PromptProviderPort fallback.
            label: Active prompt version label in Langfuse (e.g. 'production', 'staging').
        """
        self._client = langfuse_client
        self._fallback = fallback_provider
        self._label = label
        self._last_prompt_versions: dict[str, Any] = {}

    def get_last_prompt_version(self, prompt_name: str) -> Any | None:
        """Return the last resolved version for a given prompt identifier."""
        return self._last_prompt_versions.get(prompt_name)

    def _resolve_chat_prompt(
        self,
        prompt_name: str,
        **kwargs: Any,
    ) -> tuple[str, str]:
        """Attempt to fetch and compile Chat-Native prompt from Langfuse Cloud.

        Conforms to ADR-010, ADR-014, ADR-017, and ADR-026 (Rule 19):
            - Fetches strictly Chat Prompts (`type="chat"`).
            - Unpacks messages: `role="system"` -> system_instruction, `role="user"` -> user_prompt.
            - Raises on error so the caller can trigger lazy fallback degradation without happy-path overhead.

        Args:
            prompt_name: Identifier for the prompt registered in Langfuse.
            **kwargs: Template variable substitutions.

        Returns:
            Tuple containing (system_instruction, user_prompt).

        Raises:
            ApiError: If Langfuse Cloud API returns an HTTP error.
            ValueError: If the remote prompt does not implement compile or lacks chat structure.
            Exception: On network or transient infrastructure failures.
        """
        if self._client is None:
            raise RuntimeError("Langfuse client is not initialized")

        try:
            prompt = self._client.get_prompt(
                prompt_name,
                label=self._label,
                type="chat",
            )
            if hasattr(prompt, "version"):
                self._last_prompt_versions[prompt_name] = prompt.version

            if hasattr(prompt, "compile"):
                compiled_messages = prompt.compile(**kwargs)
                return _extract_prompt_messages(compiled_messages, kwargs)

            raise ValueError(f"Prompt '{prompt_name}' does not implement compile()")
        except ApiError as exc:
            _handle_api_error(exc, prompt_name, self._label)
            raise
        except Exception as exc:
            if not isinstance(exc, (ApiError, ValueError)):
                logger.warning(
                    "[LangfusePromptProvider] Transient error fetching prompt '%s' (%s: %s).",
                    prompt_name,
                    type(exc).__name__,
                    exc,
                )
            raise

    def get_prompt(
        self,
        key: PromptKey,
        **context: Any,
    ) -> tuple[str, str]:
        """Dispatch prompt formatting via Langfuse Cloud with strict lazy fallback.

        Conforms to ADR-014, ADR-017, and ADR-026 (Rule 19):
            - Fetches versioned Chat Prompt from Langfuse Cloud when client is active.
            - Lazy Degradation: Fallback provider is NEVER executed on the happy path.
            - Guaranteed Availability: Gracefully falls back to local provider on error or missing client.
            - Tracks resolved version for downstream generation observability.

        Args:
            key: Canonical PromptKey enum member.
            **context: Template variable substitutions.

        Returns:
            Tuple containing (system_instruction, user_prompt).
        """
        if self._client is None:
            return self._fallback.get_prompt(key, **context)

        prompt_descriptor = PROMPT_REGISTRY.get(key)
        if prompt_descriptor is None:
            logger.warning(
                "[LangfusePromptProvider] No registry descriptor found for prompt key '%s'. "
                "Triggering lazy fallback.",
                key.value,
            )
            return self._fallback.get_prompt(key, **context)

        try:
            if isinstance(context.get("channel_name"), ChannelName):
                context["channel_name"] = context["channel_name"].value

            return self._resolve_chat_prompt(
                prompt_name=prompt_descriptor.langfuse_name,
                **context,
            )
        except Exception as exc:  # noqa: BLE001 — Resilient fallback to local provider on remote/compilation failure
            logger.warning(
                "[LangfusePromptProvider] Remote fetch failed for prompt key '%s' (%s: %s). "
                "Triggering lazy fallback.",
                key.value,
                type(exc).__name__,
                exc,
            )
            return self._fallback.get_prompt(key, **context)
