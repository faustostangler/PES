"""Hermetic cross-layer integration tests for Cresmo SQLite, Obsidian Vault, and Pipeline."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.pipeline import CresmoPipeline, PipelineStageRunner, StageFactory
from cresmo.application.ports import (
    LlmJudgePort,
    NoOpMetricsPort,
    NoOpTelemetryPort,
)
from cresmo.bootstrap.factories.adapter_factory import (
    build_taxonomy_adapter,
    build_vault_adapter,
)
from cresmo.domain.stage_registry import StageName
from cresmo.domain.value_objects import (
    CriterionScore,
    EvaluationContext,
    JudgeEvaluation,
    LedgerEntry,
    PipelineStatus,
)
from cresmo.infrastructure.adapters.judges.preflight_decorator import (
    MechanicalPreflightJudgeDecorator,
)
from cresmo.infrastructure.adapters.prompts import JsonPromptProvider
from cresmo.infrastructure.config import CresmoSettings
from cresmo.infrastructure.persistence.sqlite_ledger_adapter import SqliteLedgerAdapter
from tests.doubles.mock_adapters import MockLLMAdapter, MockMediaIngestionPort


def _make_passing_judge() -> MechanicalPreflightJudgeDecorator:
    """Create a mechanical-preflight-guarded judge approving mechanically valid prose."""

    def _evaluate(ctx: EvaluationContext) -> JudgeEvaluation:
        scores = tuple(
            CriterionScore(
                criterion=crit,
                score=0.95,
                passed=True,
                reasoning="Verified in hermetic integration run.",
            )
            for crit in ctx.required_criteria
        )
        return JudgeEvaluation(
            target_stage=ctx.stage_name,
            passed=True,
            overall_score=0.95,
            criteria_scores=scores,
            provider="mock",
        )

    inner = MagicMock(spec=LlmJudgePort)
    inner.evaluate.side_effect = _evaluate
    return MechanicalPreflightJudgeDecorator(inner_judge=inner)


def _valid_fluid_prose_markdown() -> str:
    return (
        "## A Formação Institucional e o Debate Público\n\n"
        "A exposição histórica examina a transição das finanças estatais e o papel "
        "exercido pelo **Banco Central** na estabilização monetária contemporânea.\n\n"
        "Ao longo do exame, os mecanismos de coordenação fiscal aparecem vinculados "
        "às instituições representativas que estruturam o orçamento nacional."
    )


def _valid_gap_filler_markdown() -> str:
    return (
        "## A Formação Institucional e a Coordenação Fiscal\n\n"
        "A consolidação das instituições fiscais modernas decorreu de tensões entre "
        "necessidades bélicas imediatas e mecanismos permanentes de tributação direta.\n\n"
        "A coordenação exercida pelo **Banco Central** passou a depender de reservas "
        "estruturais e de regras previsíveis para emissões soberanas em moeda fiduciária.\n\n"
        "### Extra Info\n\n"
        "1. O primeiro marco histórico relevante desse arranjo institucional ocorreu com "
        "a reorganização bancária inglesa no final do século XVII.\n"
        "2. O controle orçamentário parlamentar consolidou-se gradualmente como contrapeso "
        "técnico para dívidas públicas de longo prazo."
    )


def test_sqlite_vault_taxonomy_pipeline_roundtrip_and_idempotency(tmp_path: Path) -> None:
    """Verify real SQLite ledger, Obsidian vault, taxonomy, prompts, and pipeline conveyor."""
    data_dir = tmp_path / "data"
    vault_dir = tmp_path / "vault"
    sqlite_path = data_dir / "cresmo_ledger.db"

    settings = CresmoSettings(
        data_dir=data_dir,
        vault_dir=vault_dir,
        sqlite_ledger_path=sqlite_path,
        enable_preflight_probes=False,
        judge_blocking=True,
        judge_max_attempts=1,
    )
    settings.ensure_directories()

    vault_adapter = build_vault_adapter(settings)
    ledger_adapter = SqliteLedgerAdapter(db_path=settings.sqlite_ledger_path)
    taxonomy_adapter = build_taxonomy_adapter(settings)
    prompt_provider = JsonPromptProvider(settings=settings)

    llm_adapter = MockLLMAdapter(
        responses=[
            _valid_fluid_prose_markdown(),
            _valid_gap_filler_markdown(),
        ]
    )
    stage_runner = PipelineStageRunner(
        telemetry_port=NoOpTelemetryPort(),
        metrics_port=NoOpMetricsPort(),
        llm_judge=_make_passing_judge(),
        judge_blocking=True,
        judge_max_attempts=1,
        prompt_provider=prompt_provider,
        llm_transformation_port=llm_adapter,
        stage_factory=StageFactory(settings=settings),
        ledger_port=ledger_adapter,
    )
    pipeline = CresmoPipeline(
        media_ingestion_port=MockMediaIngestionPort(),
        vault_port=vault_adapter,
        stage_runner=stage_runner,
        ledger_port=ledger_adapter,
        settings=settings,
        taxonomy_port=taxonomy_adapter,
    )

    raw_input = tmp_path / "incoming" / "ancapsu" / "abc123xyz00.md"
    raw_input.parent.mkdir(parents=True, exist_ok=True)
    raw_input.write_text(
        "Hoje a gente vai falar sobre bancos centrais e organização fiscal.",
        encoding="utf-8",
    )

    first_result = pipeline.run_for_text_file(raw_input, gap_filler_passes=1)

    assert first_result.success is True
    assert not first_result.already_processed
    assert first_result.source_transcript is not None
    assert first_result.source_transcript.channel.name == "ancapsu"
    assert first_result.source_transcript.channel.category != "uncategorized"
    assert len(llm_adapter.call_history) == 2

    saved_fluid = vault_adapter.get_stage_transcript(StageName.FLUID_PROSE, first_result.content_id)
    saved_gap_filler = vault_adapter.get_stage_transcript(
        StageName.GAP_FILLER, first_result.content_id
    )
    assert saved_fluid is not None
    assert saved_gap_filler is not None
    assert (data_dir / "fluid_prose" / "ancapsu" / "abc123xyz00.md").exists()
    assert (data_dir / "gap_filler" / "ancapsu" / "abc123xyz00.md").exists()

    # Mark completion in real SQLite ledger and verify idempotent short-circuit reads Vault artifact
    ledger_adapter.save_entry(
        LedgerEntry(
            content_id=first_result.content_id,
            media_url="https://youtube.com/watch?v=abc123xyz00",
            title=first_result.source_transcript.content.title,
            channel_name=first_result.source_transcript.channel.name,
            status=PipelineStatus.COMPLETED,
            completed_at=datetime.now(UTC),
        )
    )

    second_result = pipeline.run_for_text_file(raw_input, gap_filler_passes=1)

    assert second_result.success is True
    assert second_result.already_processed is True
    assert second_result.compendium is not None
    assert "### Extra Info" in second_result.compendium.content.text
    assert len(llm_adapter.call_history) == 2
