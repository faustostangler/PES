# ADR-027: SOTA-KISS Unified Telemetry Vocabulary & Langfuse Semantic Conventions

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | PROPOSED                                                           |
| **Date**    | 2026-09-30                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Cross-Cutting Telemetry & Observability — Domain, Application, Infrastructure, Presentation |
| **Relates** | ADR-011, ADR-014, ADR-016, ADR-018, ADR-021, ADR-023, ADR-025, ADR-026 |

---

## 1. Context & Architectural Motivation

In Cresmo's multi-stage cognitive synthesis pipeline, observability across OpenTelemetry, Langfuse, Prometheus, and Grafana Loki is essential for developer experience (DX), FinOps attribution, and SRE incident management.

An architectural audit of current telemetry attributes revealed fragmentation and conceptual collision across telemetry dimensions:

1. **User Identity Conflation (`user_id`):**
   - In earlier use cases (`index_raw_transcripts.py`), raw channel names (`Marcelo Andrade`) were passed as `user_id`.
   - In root pipeline sessions, unauthenticated runs defaulted to `anonymous`.
   - In synthesis use cases (`fill_gaps.py`, `synthesize_atomic_batch.py`), `ChannelTenantId.value` (`channel:UCP3CtEXi5nxbhei_aBfIOVA`) was injected as `user_id` to force Langfuse Users view to display channel tokens.
   - **Deficit:** Conflating the **Actor/Principal** (`user`) with the **Cost Center/Media Source** (`channel/tenant`) corrupts IAM auditability and prevents distinguishing automated worker pipelines from interactive CLI runs or authenticated operators.

2. **Fragmented Session Replays (`session_id`):**
   - Use cases like `index_raw_transcripts` hardcoded `session_id = f"raw_index_{ch}"`, aggregating disparate videos into a channel-wide pseudo-session.
   - Other use cases used `content:{channel}:{content_id}`.
   - `reconcile_mocs` hardcoded `session_id = "reconcile_mocs"`.
   - **Deficit:** Langfuse's **Session Replay** was unable to reconstruct the holistic end-to-end cognitive synthesis of a single video item from raw indexing to MOC reconciliation.

3. **Inconsistent Trace Identification (`trace_id`):**
   - Individual LLM generations passed ad-hoc domain strings (e.g. `{video_id}_concepts`, `mocs_reconciliation`) into `trace_id` fields instead of leveraging native OpenTelemetry 128-bit hex UUIDs, creating trace tree decoupling in distributed backends.

4. **Hardcoded Trace Names (`trace_name`):**
   - The root span name was hardcoded as `"synthesize_content"`, lacking clear domain alignment with the root use case operation (`cresmo.pipeline.execution`).

5. **Dispersed Contextual Metadata (`metadata`):**
   - Metadata keys (`channel_id`, `channel_name`, `content_id`, `title`, `source_url`, `version`) lacked a single standardized contextual dictionary contract across layers.

---

## 2. Decision: The SOTA-KISS Telemetry Canon

We formally standardize the telemetry vocabulary and semantics across all Cresmo layers according to 5 orthogonal pillars:

```
+---------------------------------------------------------------------------------------------------+
|                                  SOTA-KISS TELEMETRY CONVENTIONS                                  |
+---------------------------------------------------------------------------------------------------+
|  1. User Identity   --> user = IAM Authenticated | Local Anonymous (CLI) | Scheduled Workers      |
|  2. Session Replay  --> session_id = {channel_id}:{video_id} (Each session is exactly one video)  |
|  3. Trace ID        --> trace_id = OpenTelemetry 128-bit UUID (32-char hex execution trace)       |
|  4. Trace Name      --> trace_name = Canonical root operation (e.g. 'cresmo.pipeline.execution')  |
|  5. Trace Metadata  --> metadata = Contextual Dict (channel_id, channel_name, video_id, tags)    |
+---------------------------------------------------------------------------------------------------+
```

### Pillar 1: User Identity (`user`)
User represents the **acting principal/operator** executing the pipeline. Formatted via `UserIdentity` Value Object:
1. **Authenticated IAM Users:** `user:iam:{username}` or `user:oauth:{subject}` (created via `UserIdentity.identified(subject, provider="iam")`).
2. **Local Anonymous (CLI):** `anonymous` (created via `UserIdentity.anonymous()`).
3. **Scheduled Workers (Daemons / Background Sync):** `system:worker` (created via `UserIdentity.worker(name="worker")`).

*Invariant:* Channels/tenants are **never** passed as `user_id`. Channel attribution belongs strictly to metadata, tags, and tenant attributes (`cresmo.channel`, `cresmo.channel.id`, `cresmo.tenant_id`).

### Pillar 2: Session Replay (`session_id`)
Every session represents **exactly one video** across its entire cognitive synthesis lifecycle:
- **Canonical Format:** `{channel_id}:{video_id}` (e.g. `UCP3CtEXi5nxbhei_aBfIOVA:9IbNJ0EsTxI`).
- If `channel_id` is unavailable (e.g. text lake sources), falls back gracefully to `{channel_name}:{video_id}` (e.g. `Marcelo Andrade:9IbNJ0EsTxI`).
- Encapsulated by `PipelineSessionId` Value Object.
- Every stage (`raw_indexing`, `fluid_prose`, `expansion`, `inventory`, `atomic_batch`, `mocs`, `duplicate_unification`) within the pipeline binds to this identical `session_id`, giving full chronological Session Replay in Langfuse.

### Pillar 3: Execution Trace ID (`trace_id`)
- OpenTelemetry 128-bit trace UUID (`32-hex` string format, e.g. `f"{span.get_span_context().trace_id:032x}"`).
- Serves as the single root correlation key across Prometheus exemplars, Loki log lines, and Langfuse trace trees.
- Internal LLM calls do not invent custom `trace_id` strings; they inherit the trace ID from the active OpenTelemetry context, passing domain qualifiers as span names or span attributes (e.g., `cresmo.stage_name`, `cresmo.operation`).

### Pillar 4: Root Operation Name (`trace_name`)
- Configurable root span / trace name representing the entrypoint operation.
- Default canonical root name: **`cresmo.pipeline.execution`**.
- Child stages use standardized sub-span names: `cresmo.stage.{stage_name}`.
- LLM generation spans use: `cresmo.llm.generation`.

### Pillar 5: Contextual Metadata (`metadata`)
Structured contextual dictionary (`dict[str, Any]`) attached at root span and propagated down:
- `cresmo.channel.id`: Platform channel ID (e.g. `UCP3CtEXi5nxbhei_aBfIOVA`).
- `cresmo.channel.name`: Display channel name (e.g. `Marcelo Andrade`).
- `cresmo.content.id` / `cresmo.video.id`: Video / content identifier.
- `cresmo.content.title`: Video title.
- `cresmo.source_url`: Media URL.
- `cresmo.pipeline_version`: Active pipeline semver.
- `langfuse.trace.tags`: `[channel_name, f"auth:{user.provider}", pipeline_version]`.

---

## 3. Langfuse Ingestion Strategy & Compliance Gate

| Telemetry Dimension | Langfuse Target Attribute | Standardized Value |
|---------------------|---------------------------|-------------------|
| **User ID** | `trace.userId` / `langfuse.user.id` | `anonymous` \| `user:iam:...` \| `system:worker` |
| **Session ID** | `trace.sessionId` / `langfuse.session.id` | `{channel_id}:{video_id}` |
| **Trace ID** | Native OTel `trace_id` | 32-hex character UUID |
| **Trace Name** | Root Span Name | `cresmo.pipeline.execution` |
| **Tags** | `trace.tags` | `[channel_name, f"auth:{provider}", version]` |
| **Channel FinOps** | `metadata.channel_id`, `metadata.channel_name` | Attached to session/trace metadata |

---

## 4. Consequences & Trade-offs

### Positive
1. **Pristine Langfuse Users Dashboard:** Cleanses the Users view, separating humans (`user:iam:...`), CLI users (`anonymous`), and automation (`system:worker`).
2. **Unified Video Session Replays:** Viewing a session in Langfuse displays the complete chronological journey of a single video across all 7 synthesis stages.
3. **Trace Tree Integrity:** Using native OTel UUIDs prevents disconnected traces in Langfuse and OpenTelemetry backends.
4. **Architectural Purity (DDD):** Domain Value Objects (`UserIdentity`, `PipelineSessionId`) strictly enforce invariant formats.

### Negative & Mitigations
- **Existing Traces in Langfuse:** Previous traces generated with legacy IDs will remain in historical storage. Mitigated by forward-clean partitioning starting with this release.
- **SessionId Format Migration:** Legacy format was `content:{channel}:{content_id}`. `PipelineSessionId` will accept the legacy 3-part syntax in `__post_init__` for backward compatibility while generating the canonical 2-part `{channel_id}:{video_id}` format.

---

## 5. Implementation Scope

1. **Domain (`src/cresmo/domain/entities.py`):**
   - Update `UserIdentity`: add `UserIdentity.worker(name: str = "worker") -> UserIdentity` generating `system:worker`.
   - Update `PipelineSessionId`: canonical format `{channel_id}:{video_id}`, with parsing and property accessors (`channel_token`, `video_id`/`content_id`).
2. **Application Ports (`src/cresmo/application/ports/`):**
   - Update `TelemetryPort.start_pipeline_session` signature to accept `trace_name: str | None = None`.
3. **Application Orchestrator (`src/cresmo/application/pipeline/`):**
   - Set root `trace_name="cresmo.pipeline.execution"`.
   - Pass `session_id` and canonical `user_id` down to child stages.
4. **Use Cases (`src/cresmo/application/use_cases/`):**
   - `index_raw_transcripts.py`: replace `raw_index_{ch}` with `PipelineSessionId`, replace `ch` with `UserIdentity`.
   - `fill_gaps.py`, `expand_compendium.py`, `discover_atomic_inventory.py`, `synthesize_atomic_batch.py`: pass `user_identity` (not `ChannelTenantId`).
   - `reconcile_mocs.py`: accept optional `session_id` and `user_id`.
   - `sync_channel.py`: pass `user=UserIdentity.worker()` when calling `pipeline.run_for_video`.
5. **Infrastructure (`src/cresmo/infrastructure/adapters/opentelemetry_adapter.py`):**
   - Implement `trace_name` in `start_pipeline_session`.
   - Bind `session_id`, `user_id`, `trace_name`, and metadata attributes conforming to this ADR.
6. **Tests:**
   - Update unit tests in `test_entities.py`, `test_opentelemetry_adapter.py`, `test_pipeline.py`, etc., validating the new invariants.
