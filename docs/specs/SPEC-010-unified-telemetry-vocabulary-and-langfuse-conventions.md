# SPEC-010: Test Specifications — Unified Telemetry Vocabulary & Langfuse Conventions

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED (PARTIALLY SUPERSEDED by ADR-033, ADR-035, ADR-037)        |
| **Date**    | 2026-09-30                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **ADR**     | [`ADR-027`](../adr/ADR-027-unified-telemetry-vocabulary-and-langfuse-conventions.md) |

---

> [!WARNING]
> ### Architectural Evolution & Partial Supersession Notice
> This specification has been refined and partially superseded by later accepted ADRs:
> 1. **`ChannelTenantId` Decommissioned (`ADR-033`)**: The standalone `ChannelTenantId` value object and the legacy session string token format (`.channel_token`) are decommissioned. Multi-tenant partitioning is directly derived from `Channel.tenant_key`.
> 2. **Canonical Session ID Format (`ADR-033`, `ADR-035`)**: The canonical session identifier format is `{channel_id}:{content_id}` (falling back to `{channel_name}:{content_id}` if no channel ID exists). The `.video_id` property/alias has been purged across the domain in favor of generic `.content_id`.
> 3. **Per-Stage Independent Traces (`ADR-035`, `ADR-037`)**: The requirement for a single monolithic 7-stage OpenTelemetry trace is superseded. In accordance with ADR-035 and ADR-037, each pipeline stage initiates an independent OpenTelemetry trace with its own root span, correlated across Langfuse using `langfuse.session.id = session_id.value`.

---

## 1. Acceptance Criteria

- **AC-001 (UserIdentity Modalities):**
  - `UserIdentity.worker(name="worker")` constructs an immutable Value Object with `value="system:worker"`, `is_anonymous=False`, `provider="system"`, `subject="worker"`.
  - `UserIdentity.identified(subject="alice", provider="iam")` produces `value="user:iam:alice"`, `is_anonymous=False`, `provider="iam"`, `subject="alice"`.
  - `UserIdentity.anonymous()` produces `value="anonymous"`, `is_anonymous=True`, `provider="anonymous"`, `subject=""`.
- **AC-002 (PipelineSessionId Format - Single Content Session Replay):**
  - Canonical format is `{channel_id}:{content_id}` (or `{channel_name}:{content_id}` if `channel_id` is None per ADR-033).
  - `PipelineSessionId.create(channel=..., content_id=content_id)` produces `{channel_id.value}:{content_id.value}`.
  - Backward compatibility: parsing legacy 3-part `content:{channel}:{content_id}` or `{channel}:{video_id}` extracts the correct channel token and content ID without raising an exception.
- **AC-003 (OpenTelemetry Root Span & Trace Name):**
  - `TelemetryPort.start_pipeline_session` accepts optional `trace_name: str | None = None`.
  - When omitted, `trace_name` defaults to `"cresmo.pipeline.execution"`.
  - The root OpenTelemetry span name is set to `trace_name`.
  - Spans attach attributes:
    - `langfuse.session.id = session_id.value` (`{channel_id}:{video_id}`)
    - `langfuse.user.id = user.value` (`anonymous`, `user:iam:...`, or `system:worker`)
    - `langfuse.observation.type = "span"`
    - `cresmo.channel.name`, `cresmo.channel.id`, `cresmo.content.id` in metadata.
- **AC-004 (Stage Span Correlation):**
  - All 7 stages (`raw_indexing`, `fluid_prose`, `expansion`, `inventory`, `atomic_batch`, `mocs`, `duplicate_unification`) inherit trace context and propagate the canonical video `session_id` and `user_id`.
  - `index_raw_transcripts.py` replaces `f"raw_index_{ch}"` with the video's canonical `PipelineSessionId`.
  - `index_raw_transcripts.py` removes `user_id = ch` and uses `UserIdentity`.
- **AC-005 (Scheduled Worker Ingestion):**
  - `SyncChannelUseCase` marks executions with `user=UserIdentity.worker()` when calling `pipeline.run_for_video`.
- **AC-006 (CLI Humble Object):**
  - CLI commands (`run_for_video`, `run_for_manifest`, `run_for_text_file`) default to `UserIdentity.anonymous()` when no auth context is passed.

---

## 2. Invariants & Boundary Conditions

- `UserIdentity`:
  - `value` must be non-empty and stripped. Empty or whitespace string raises `ValueError`.
  - Identified `UserIdentity` must have non-empty `subject`.
- `PipelineSessionId`:
  - `value` must be non-empty and stripped. Empty or whitespace string raises `ValueError`.
  - `value` must contain a colon separator (`:`). Values without colon raise `ValueError`.

---

## 3. Test Strategy

| Test File | Test Scope | Method |
|-----------|------------|--------|
| `tests/cresmo/unit/test_entities.py` | `UserIdentity` modalities & `PipelineSessionId` canonical formatting & backward compatibility | Pure Unit |
| `tests/cresmo/unit/test_opentelemetry_adapter.py` | `trace_name`, `session_id`, `user_id`, and metadata propagation | Pure Unit with OTel in-memory exporter |
| `tests/cresmo/unit/test_index_raw_transcripts_use_case.py` | Verified session and user attributes passed to LLM transform | Unit with Mock LLM |
| `tests/cresmo/unit/test_sync_channel_use_case.py` | Verified `UserIdentity.worker()` passed to pipeline | Unit with Mock Pipeline |
| `tests/cresmo/unit/test_pipeline.py` | End-to-end pipeline session context validation | Unit / Integration |
