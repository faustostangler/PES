# ADR-063: Lean Telemetry v2 — Zero Attribute Duplication, Dynamic Pipeline Versioning, and Analytical Insight Metrics

| Field       | Value                                                              |
|-------------|--------------------------------------------------------------------|
| **Status**  | ACCEPTED                                                           |
| **Date**    | 2026-11-20                                                         |
| **Authors** | Lead Architect (Fausto Stangler), Systems Architect (Doctor Stangler Committee) |
| **Scope**   | Cross-Cutting Observability & Telemetry — Application, Infrastructure, Bootstrap |
| **Relates** | ADR-000, ADR-016, ADR-026, ADR-027, ADR-034, ADR-035, ADR-036, ADR-037, ADR-062 |

---

## 1. Context & Architectural Motivation

Operational inspection of live Langfuse v4 traces produced by `OpenTelemetryAdapter` revealed three lingering telemetry defects left over from earlier iterations:

1. **Loose Vendor Input/Output Attribute Duplication:**
   - `_build_langfuse_input_payload` emitted canonical identity and input metadata both inside the serialized JSON (`input.value`, `langfuse.observation.input`, `langfuse.trace.input`) **and** as non-standard loose span attributes (`langfuse.input.content_title`, `langfuse.input.channel_name`, `langfuse.input.content_id`, `langfuse.input.channel_id`, `langfuse.input.batch_id`, `langfuse.input.video_url`, `langfuse.input.raw_characters`, `langfuse.input.raw_words`).
   - Because Langfuse v4 only consumes `langfuse.trace.input` / `langfuse.observation.input` for the Input panel, every loose `langfuse.input.*` key leaked into the trace Attributes/Metadata drawer side-by-side with `cresmo.content.title`, `cresmo.channel.name`, etc.
   - Similarly, `record_session_output` still emitted a redundant 4th JSON copy (`langfuse.output`), and `record_session_coherence` emitted loose `langfuse.output.*` keys.

2. **Legacy Static `cresmo:v2` Version Tag:**
   - While package metadata (`pyproject.toml`, `cresmo.__version__`) and prompt seeding (`seed_prompts.py`) already transitioned to dynamic SemVer + `git_sha` attribution, `CresmoSettings.pipeline_version` and `OpenTelemetryAdapter.DEFAULT_PIPELINE_VERSION` remained hardcoded to the legacy default `"cresmo:v2"`.
   - Furthermore, `git_sha` from `CresmoSettings` was not wired into `OpenTelemetryAdapter`, breaking commit-level regression traceability in Langfuse.

3. **Unstructured Analytical Insight Gaps:**
   - High-signal operational dimensions already computed in `PipelineCoordinator` and `PipelineStageRunner` — such as `gap_filler_passes`, `force_reprocess`, raw text size (`word_count`/`char_count`), stage checkpoint cache hit ratio (`cache_hit_ratio`), per-stage `expansion_ratio`, `retries`, and consolidated `judge_overall_score` — were either buried in raw string metadata (`cresmo.metadata.*`) or omitted entirely from stage summaries.
   - Canonical trace and root span identifiers (`cresmo.synthesis_pipeline`, `pipeline.coordinator`, `cresmo.llm.generate`) were duplicated as string literals across `coordinator.py`, `opentelemetry_adapter.py`, `gemini_adapter.py`, and `ollama_llm_adapter.py`, and Tier 1.1 (`pipeline.coordinator`) lacked the `cresmo.` Bounded Context prefix.

---

## 2. Banished Anti-Patterns

This ADR formally bans the following anti-patterns with **zero backward compatibility**:

* **`Loose Vendor Input/Output Attribute Duplication*`**: Emitting non-standard loose `langfuse.input.<key>`, `langfuse.output.<key>`, or legacy 4th-copy `langfuse.output` span attributes alongside canonical `cresmo.*` attributes and JSON I/O payloads.
* **`Static Legacy Pipeline Version Default*`**: Hardcoding obsolete release tags (such as `"cresmo:v2"`) as default values in settings or telemetry adapters instead of resolving distribution metadata dynamically via `importlib.metadata`.

---

## 3. Decision: Lean Telemetry v2 Standards

### Pillar 1: Single Source of Truth & 100% Bounded Context Namespace Consistency
Canonical telemetry operation identifiers are defined once in the Application Telemetry Port (`src/cresmo/application/ports/telemetry.py`) and strictly enforce the `cresmo.` Bounded Context namespace across all 4 tiers:
- **Tier 1 (Trace):** `SYNTHESIS_PIPELINE_TRACE_NAME: Final[str] = "cresmo.synthesis_pipeline"`
- **Tier 1.1 (Root Span):** `PIPELINE_ROOT_SPAN_NAME: Final[str] = "cresmo.pipeline.coordinator"` *(replaces unprefixed `pipeline.coordinator` from ADR-037)*
- **Tier 2 (Stage Span):** `cresmo.stage.{stage_name}`
- **Tier 3A (Generation Span):** `LLM_GENERATION_SPAN_NAME: Final[str] = "cresmo.llm.generate"` *(shared SSOT across `GeminiLLMAdapter` and `OllamaLLMAdapter`)*
- **Tier 3B (Evaluation Span):** `cresmo.stage.{stage_name}.evaluation`
- **CLI Entry Span:** `cresmo.run` *(tracer `cresmo.cli`)*

### Pillar 2: Zero Attribute Duplication (Strict Namespace Separation)
- **`cresmo.*` Namespace (Domain/Application Semantic Attributes):** Owns all structured, filterable, typed span attributes.
- **`langfuse.*` Namespace (Adapter Protocol Only):** Strictly restricted to official Langfuse OTel protocol keys (`langfuse.observation.type`, `langfuse.session.id`, `langfuse.user.id`, `langfuse.trace.name`, `langfuse.trace.tags`, `langfuse.trace.input`, `langfuse.observation.input`, `langfuse.trace.output`, `langfuse.observation.output`) alongside CNCF OTel `input.value` / `output.value`.
- **Complete Purge of Loose Keys:** All `langfuse.input.*`, `langfuse.output.*`, and legacy `langfuse.output` attributes are permanently eliminated.
- **Zero `cresmo.metadata.*` Shadowing:** All promoted first-class keys are registered in `_CANONICAL_ROOT_METADATA_KEYS` so they are never duplicated under `cresmo.metadata.*`.

### Pillar 3: Dynamic Pipeline Versioning & Commit Lineage
- `resolve_default_pipeline_version()` in `src/cresmo/infrastructure/config.py` resolves distribution metadata dynamically via `importlib.metadata.version("pes")` (falling back to `"0.0.0-dev"`), returning `f"cresmo:v{pkg_version}"`.
- Because it reads distribution metadata via stdlib `importlib.metadata`, infrastructure adapters never import from `cresmo.__init__`, preserving **ADR-026 Rule 9**.
- `CresmoSettings.pipeline_version` uses `default_factory=resolve_default_pipeline_version` and unifies 12-Factor environment overrides on the single Bounded Context variable `CRESMO_PIPELINE_VERSION` (eliminating the redundant unprefixed `PIPELINE_VERSION` alias).
- `build_telemetry_adapter` injects `git_sha=resolved_settings.git_sha` into `OpenTelemetryAdapter`, emitting `cresmo.pipeline.git_sha` (8-char short SHA) and tag `git:{short_sha}` whenever present.

### Pillar 4: First-Class Analytical Insight Attributes & Metrics

| Scope | Attribute / Payload Key | Type | Analytical Purpose |
| :--- | :--- | :--- | :--- |
| **Root Span (`cresmo.pipeline.*`)** | `cresmo.pipeline.version` | `str` | Compare quality, latency, and cost across releases |
| **Root Span (`cresmo.pipeline.*`)** | `cresmo.pipeline.git_sha` | `str` | Pinpoint prompt or code regressions to exact commits |
| **Root Span (`cresmo.pipeline.*`)** | `cresmo.pipeline.gap_filler_passes` | `int` | Evaluate quality/cost trade-off across pass counts |
| **Root Span (`cresmo.pipeline.*`)** | `cresmo.pipeline.force_reprocess` | `bool` | Segregate forced re-runs from normal checkpointed runs |
| **Root Span (`cresmo.content.*`)** | `cresmo.content.source` | `str` | Segment metrics by ingestion modality (`transcript`, etc.) |
| **Root Span (`cresmo.content.*`)** | `cresmo.content.word_count` | `int` | Correlate transcript length vs. tokens, latency, and judge failures |
| **Root Span (`cresmo.content.*`)** | `cresmo.content.char_count` | `int` | Character-level FinOps and context-window pressure analysis |
| **Root Span (`cresmo.content.*`)** | `cresmo.content.publication_date` | `str` | Temporal analysis of channel archive coverage |
| **Session Output (`record_session_output`)** | `stages_reused_from_cache`, `cache_hit_count`, `cache_hit_ratio` | `list[str]`, `int`, `float` | Explain fast/low-cost traces via checkpoint reuse |
| **Stage Output (`record_stage_io`)** | `expansion_ratio`, `retries`, `judge_passed`, `judge_overall_score` | `float`, `int`, `bool\|None`, `float\|None` | Measure per-stage compression/densification, retry friction, and verdict |

---

## 4. Consequences & Supersession Lineage

* **Refines / Partially Supersedes:**
  - **ADR-016 & ADR-027:** Replaces static `"cresmo:v2"` tag examples with dynamic distribution versioning.
  - **ADR-026 (Rule 9):** Upgrades `CresmoSettings.pipeline_version` default from `"cresmo:v2"` to `default_factory=resolve_default_pipeline_version`.
  - **ADR-034:** Preserves strict ID-ID and TXT-TXT parity inside `cresmo.*` and the canonical JSON input payload, while decommissioning loose `langfuse.input.*` span attributes.
  - **ADR-037:** Completes Pillar 3 (Zero-Duplication Governance) by purging residual `langfuse.input.*`, `langfuse.output.*`, and legacy `langfuse.output` attributes and formalizing SSOT trace/span constants.
* **Positive:** Clean, non-redundant Langfuse trace inspection, zero storage waste from duplicated vendor keys, accurate SemVer + Git SHA release tracking, and rich typed attributes for FinOps and LLM quality analytics.
* **Breaking:** Any downstream dashboard or query referencing `langfuse.input.*`, `langfuse.output.*`, `langfuse.output`, or the literal `"cresmo:v2"` tag must migrate to canonical `cresmo.*` attributes and dynamic SemVer tags.

