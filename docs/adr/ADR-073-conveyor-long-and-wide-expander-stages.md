# ADR-073: Sequential Conveyor Integration of Long and Wide Expander Stages

- **Status:** Accepted
- **Date:** 2026-11-23
- **Bounded Context:** Cresmo (`Domain`, `Application/Pipeline`, `Application/Evals`, `Application/UseCases`, `Infrastructure/Prompts`, `Infrastructure/Judges`, `Infrastructure/Obsidian`, `Infrastructure/Config`)
- **Supersedes / Refines:** Refines `ADR-029`, `ADR-031`, `ADR-039`, `ADR-040`, `ADR-046`, `ADR-057`, `ADR-058`, `ADR-060`, `ADR-071`; enforces `ADR-010` zero-backward-compatibility cleanup

## Context

The Cresmo conveyor pipeline previously terminated narrative expansion at `gap_filler` (`raw -> fluid_prose -> gap_filler`), while multi-secular longitudinal expansion (`cresmo-long-expander` — Braudelian *longue durée*, 3-tier causal stratification, and historical palimpsest analysis) and synchronic comparative expansion (`cresmo-wide-expander` — Karl Jaspers' *Achsenzeit*, connected global history, and parallel civilizational analysis) remained stranded in a legacy standalone use case (`ExpandCompendiumUseCase`) with incompatible variable contracts (`{{compendium_body}}`, `{{complementary_info}}`, `{{current_text}}`), missing `cresmo-style-guide` wiring, no judge rubrics, and no iterative multi-pass saturation control.

Integrating `long_expander` and `wide_expander` directly into `CresmoPipeline` sequentially (`raw -> fluid_prose -> gap_filler -> long_expander -> wide_expander`) unlocks deep multi-pass epistemic saturation across all three expansion stages using the exact same stage-agnostic engine (`HybridSaturationEvaluator`, `convergence_evaluator`, and `generate_stage_candidate`), while eliminating accumulated legacy `"compendium"` / `"gap_filler_passes"` naming debt per `ADR-010`.

## Decision

1. **Sequential Conveyor Topology (`CONVEYOR_STAGES`):**
   - `CresmoPipeline.execute` runs stages sequentially via `StageRegistry`:
     `raw -> fluid_prose -> gap_filler -> long_expander -> wide_expander`.
   - Stage transitions execute identically via `StageConfig.build_transform_prompt()`, `generate_stage_candidate` (`BUILD` on Pass 1, `REFINE` with `<NO_NEW_GAPS/>` early-exit token on Pass 2+), `HybridSaturationEvaluator`, `post_process_expanded_transcript`, `MechanicalPreflightJudgeDecorator` + `LlmJudgePort`, and unified `VaultRepositoryPort.save_stage_transcript(stage, artifact)`.
   - Saturation evaluation (`HybridSaturationEvaluator`, `convergence_evaluator.py`, `stage_execution.py`) remains strictly stage-agnostic. Only per-stage `max_passes` budgets differ:
     - `gap_filler`: default `max_passes = 5` (`PipelineSettingsProtocol.expansion_max_passes`)
     - `long_expander`: default `max_passes = 7` (`PipelineSettingsProtocol.long_expander_max_passes`, `CRESMO_LONG_EXPANDER_MAX_PASSES`)
     - `wide_expander`: default `max_passes = 5` (`PipelineSettingsProtocol.expansion_max_passes`)
   - Explicit CLI `--passes N` / `expansion_max_passes=N` defaults to `None` (allowing per-stage settings `5`/`7`/`5` to govern) and overrides all `HYBRID_SEMANTIC` expansion stages only when explicitly specified.

2. **Zero-Backward-Compatibility Domain & Application Cleanup (`ADR-010`):**
   Legacy identifiers tied to `EnrichedCompendium` or single-expansion `gap_filler` assumptions are replaced directly with zero deprecation shims or aliases:
   - `CompendiumStructureError` -> `StageTranscriptStructureError`
   - `src/cresmo/domain/services/compendium.py` (`post_process_enriched_compendium`) -> `src/cresmo/domain/services/stage_post_processor.py` (`post_process_expanded_transcript`, also honoring `candidate.metadata["passes_executed"]`)
   - `validate_gap_filler_syntax` -> `validate_expanded_prose_syntax`
   - `PipelineResult.{fluid_transcript, compendium}` -> `PipelineResult.stage_artifacts: Mapping[StageName, StageTranscript]` (frozen via `MappingProxyType`) and `PipelineResult.final_transcript: StageTranscript | None`
   - `gap_filler_passes` (`PipelineSettingsProtocol`, `Coordinator`, `SessionTelemetrySpec`, `IngestionSettings`, `.env.example`, telemetry attributes) -> `expansion_max_passes` (global cap / override, `int | None = None` where optional) and `long_expander_max_passes` (7 default for `long_expander`)
   - `PromptVariableSchema.gap_filler_draft` -> `PromptVariableSchema.iterative_draft`
   - `VaultRepositoryPort.get_enriched_files_for_channel(channel)` -> `VaultRepositoryPort.get_stage_files_for_channel(stage_name, channel)` (`ConcatMasterUseCase` targets terminal stage `StageName.WIDE_EXPANDER`)
   - `ExpandCompendiumUseCase` (`src/cresmo/application/use_cases/expand_compendium.py`) deleted permanently.

3. **Gold-Standard Skill & Prompt Parity (`ADR-040`, `ADR-071`):**
   - `.agents/skills/cresmo-long-expander/SKILL.md` and `.agents/skills/cresmo-wide-expander/SKILL.md` are refactored to match `cresmo-gap-filler/SKILL.md` structural conventions (`Overview`, `Passo 1` diagnostic axis & implicit framing prohibition, `Passo 2: Resposta Escrita` iterative saturation & `### Extra Info`, with zero `file:///` links or legacy directory paths).
   - `prompts.json` binds `"cresmo-style-guide"` in `skills` for both `long_expander` and `wide_expander`, plus registers `judge_long_expander` and `judge_wide_expander`.
   - `long_expander/{system,user}.md` and `wide_expander/{system,user}.md` mirror `gap_filler/{system,user}.md` 1:1 using unified stage artifacts (`{{raw_text}}{{draft_section}}`), removing `{{compendium_body}}`, `{{complementary_info}}`, and `{{current_text}}` (preventing multi-pass `prompt_context["current_text"]` collisions in `stage_execution.py`).

4. **Judge Criteria & Evaluation Matrix (`JudgeCriterion` & `resolve_stage_scoring_policy`):**
   Six new canonical `JudgeCriterion` members are introduced alongside a dictionary-based `resolve_stage_scoring_policy` lookup:
   - Shared across both new expansion stages: `empirical_historical_grounding`, `implicit_framing_style`
   - **`long_expander` (`PromptKey.JUDGE_LONG_EXPANDER`):**
     - `longue_duree_stratification`: `0.35` *(primary architectural priority)*
     - `empirical_historical_grounding`: `0.25` *(Mechanical Veto)*
     - `historical_palimpsest`: `0.20`
     - `extra_info_granularity`: `0.10` *(Mechanical Veto, reused)*
     - `implicit_framing_style`: `0.10`
   - **`wide_expander` (`PromptKey.JUDGE_WIDE_EXPANDER`):**
     - `synchronic_connectivity`: `0.30`
     - `comparative_parallelism`: `0.30`
     - `empirical_historical_grounding`: `0.20` *(Mechanical Veto)*
     - `extra_info_granularity`: `0.10` *(Mechanical Veto, reused)*
     - `implicit_framing_style`: `0.10`
   - Both stages reuse `validate_expanded_prose_syntax` mapped to `JudgeCriterion.EXTRA_INFO_GRANULARITY` in `MechanicalPreflightJudgeDecorator` and are registered in `evals/specs.py`.

5. **Langfuse Prompt Seeding Strategy:**
   Because prompt templates live in `src/cresmo/infrastructure/resources/prompts/<key>/{system,user}.md` and `prompts.json` (`ADR-071`), updated prompts for `long_expander`, `wide_expander`, `judge_long_expander`, and `judge_wide_expander` are published to Langfuse Cloud via `uv run cresmo seed-prompts` with zero code duplication.

## Consequences

- **Positive:** Unifies all three epistemic expansion stages under one stage-agnostic iterative saturation engine, removes legacy naming drift cleanly per `ADR-010`, prevents multi-pass `current_text` template collisions, guarantees 1:1 local/remote Langfuse variable parity, and establishes weighted judge gates with mechanical vetoes for structural quality and empirical grounding.
- **Negative / Trade-offs:** Removes `PipelineResult.{fluid_transcript, compendium}`, `gap_filler_passes`, `ExpandCompendiumUseCase`, and `get_enriched_files_for_channel` immediately with no backward-compatibility adapters; any downstream consumer or operator must migrate to `stage_artifacts`/`final_transcript`, `expansion_max_passes`, `get_stage_files_for_channel`, and re-seed prompts via `uv run cresmo seed-prompts`. Running four LLM conveyor stages sequentially increases per-content token budget and wall-clock latency unless intermediate artifacts already exist in cache (`data/{stage}/{channel}/{id}.md`).
