"""Pure CNCF OpenTelemetry GenAI Semantic Conventions attribute builder.

Conforms to:
- ADR-011: Unified Inference Observability
- ADR-016: OpenTelemetry GenAI Semantic Conventions
- ADR-065: Multi-pass Telemetry Scoping
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

from typing import Final

from cresmo.application.ports.telemetry import (
    TelemetryAttributeValue,
    get_active_telemetry_pass,
)

_ATTR_GENAI_SYSTEM: Final[str] = "gen_ai.system"
_ATTR_GENAI_MODEL: Final[str] = "gen_ai.request.model"
_ATTR_GENAI_INPUT_TOKENS: Final[str] = "gen_ai.usage.input_tokens"
_ATTR_GENAI_OUTPUT_TOKENS: Final[str] = "gen_ai.usage.output_tokens"
_ATTR_LANGFUSE_SESSION_ID: Final[str] = "langfuse.session.id"
_ATTR_LANGFUSE_USER_ID: Final[str] = "langfuse.user.id"
_ATTR_CRESMO_TRACE_ID: Final[str] = "cresmo.trace_id"
_ATTR_GENAI_TEMPERATURE: Final[str] = "gen_ai.request.temperature"
_ATTR_GENAI_MAX_TOKENS: Final[str] = "gen_ai.request.max_tokens"
_ATTR_CRESMO_THINKING_LEVEL: Final[str] = "cresmo.thinking_level"
_ATTR_GENAI_REASONING_TOKENS: Final[str] = "gen_ai.usage.reasoning_tokens"
_ATTR_CRESMO_PASS_NUM: Final[str] = "cresmo.pass_num"


def build_genai_attributes(
    *,
    system: str,
    model: str,
    prompt_tokens: int,
    candidate_tokens: int,
    session_id: str | None = None,
    user_id: str | None = None,
    trace_id: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    thinking_level: str | None = None,
    thinking_tokens: int | None = None,
    pass_num: int | None = None,
) -> dict[str, TelemetryAttributeValue]:
    """Build standardized GenAI and Cresmo span attributes for LLM generation observations."""
    attrs: dict[str, TelemetryAttributeValue] = {
        _ATTR_GENAI_SYSTEM: system,
        _ATTR_GENAI_MODEL: model,
        _ATTR_GENAI_INPUT_TOKENS: prompt_tokens,
        _ATTR_GENAI_OUTPUT_TOKENS: candidate_tokens,
    }
    if session_id:
        attrs[_ATTR_LANGFUSE_SESSION_ID] = session_id
    if user_id:
        attrs[_ATTR_LANGFUSE_USER_ID] = user_id
    if trace_id:
        attrs[_ATTR_CRESMO_TRACE_ID] = trace_id
    if temperature is not None:
        attrs[_ATTR_GENAI_TEMPERATURE] = temperature
    if max_tokens is not None:
        attrs[_ATTR_GENAI_MAX_TOKENS] = max_tokens
    if thinking_level is not None:
        attrs[_ATTR_CRESMO_THINKING_LEVEL] = thinking_level
    if thinking_tokens is not None:
        attrs[_ATTR_GENAI_REASONING_TOKENS] = thinking_tokens

    effective_pass = pass_num if pass_num is not None else get_active_telemetry_pass()
    if effective_pass is not None:
        attrs[_ATTR_CRESMO_PASS_NUM] = effective_pass
    return attrs
