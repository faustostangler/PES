"""Pure CNCF OpenTelemetry GenAI Semantic Conventions attribute builder.

Conforms to:
- ADR-011: Unified Inference Observability
- ADR-016: OpenTelemetry GenAI Semantic Conventions
- ADR-065: Multi-pass Telemetry Scoping
- ADR-070: Unified Hexagonal Telemetry Port & Typed Span Handle
"""

from __future__ import annotations

from cresmo.application.ports.telemetry import (
    TelemetryAttributeValue,
    get_active_telemetry_pass,
)


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
        "gen_ai.system": system,
        "gen_ai.request.model": model,
        "gen_ai.usage.input_tokens": prompt_tokens,
        "gen_ai.usage.output_tokens": candidate_tokens,
    }
    if session_id:
        attrs["langfuse.session.id"] = session_id
    if user_id:
        attrs["langfuse.user.id"] = user_id
    if trace_id:
        attrs["cresmo.trace_id"] = trace_id
    if temperature is not None:
        attrs["gen_ai.request.temperature"] = temperature
    if max_tokens is not None:
        attrs["gen_ai.request.max_tokens"] = max_tokens
    if thinking_level is not None:
        attrs["cresmo.thinking_level"] = thinking_level
    if thinking_tokens is not None:
        attrs["gen_ai.usage.reasoning_tokens"] = thinking_tokens

    effective_pass = pass_num if pass_num is not None else get_active_telemetry_pass()
    if effective_pass is not None:
        attrs["cresmo.pass_num"] = effective_pass
    return attrs
