"""Hermetic cross-layer integration tests for Cresmo SQLite, Obsidian Vault, and Pipeline."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

from cresmo.application.pipeline.coordinator import CresmoPipeline
from cresmo.application.pipeline.stage_factory import StageFactory
from cresmo.application.pipeline.stage_runner import PipelineStageRunner
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
    ChannelName,
    CriterionScore,
    EvaluationContext,
    JudgeEvaluation,
    LedgerEntry,
    PipelineStatus,
)
from cresmo.infrastructure.adapters.judges.preflight_decorator import (
    MechanicalPreflightJudgeDecorator,
)
from cresmo.infrastructure.adapters.prompts.json_provider import JsonPromptProvider
from cresmo.infrastructure.config import (
    CresmoSettings,
    JudgeSettings,
    ObservabilitySettings,
    RuntimeTelemetrySettings,
    StorageSettings,
)
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


def _valid_long_expander_markdown() -> str:
    return (
        "## Inércia Fiscal Multissecular e Soberania Monetária\n\n"
        "A consolidação dos bancos centrais decorreu de restrições fiscais e ciclos creditícios "
        "acumulados desde as repúblicas mercantis italianas e as bolsas de Antuérpia e Amsterdã.\n\n"
        "Ao longo dos séculos, o controle parlamentar da dívida pública transformou tributos de guerra "
        "temporários em infraestrutura estatal permanente.\n\n"
        "### Extra Info\n\n"
        "1. O Banco de Amsterdã em 1609 padronizou compensações cambiais em moeda bancária.\n"
        "2. O estatuto de 1694 instituiu o Banco da Inglaterra mediante subscrição de títulos de dívida."
    )


def _valid_wide_expander_markdown() -> str:
    return (
        "## Sincronias Cambiais Globais e Regimes Fiscais Paralelos\n\n"
        "Na mesma conjuntura seiscentista em que Amsterdã e Londres estruturavam bancos públicos de "
        "emissão, o escoamento de prata de Potosí articulava praças europeias, rotas transpacíficas "
        "pelo Galeão de Manila e reformas tributárias na dinastia Ming.\n\n"
        "Simultaneamente, formações políticas sem contato cambial direto responderam a choques "
        "climáticos e fiscais semelhantes mediante centralização de reservas metálicas e estatutos "
        "alfandegários próprios.\n\n"
        "### Extra Info\n\n"
        "1. A Reforma do Chicote Único consolidou tributos em prata na China Ming no século XVI.\n"
        "2. O shogunato Tokugawa padronizou a cunhagem e o controle comercial em Nagasaki em 1639."
    )


def test_sqlite_vault_taxonomy_pipeline_roundtrip_and_idempotency(tmp_path: Path) -> None:
    """Verify real SQLite ledger, Obsidian vault, taxonomy, prompts, and pipeline conveyor."""
    data_dir = tmp_path / "data"
    vault_dir = tmp_path / "vault"

    settings = CresmoSettings(
        _env_file=None,
        storage=StorageSettings(data_dir=data_dir, vault_dir=vault_dir),
        judge=JudgeSettings(blocking=True, max_attempts=1),
        observability=ObservabilitySettings(
            runtime=RuntimeTelemetrySettings(enable_preflight_probes=False)
        ),
    )
    settings.ensure_directories()

    vault_adapter = build_vault_adapter(settings.storage)
    ledger_adapter = SqliteLedgerAdapter(db_path=settings.storage.sqlite_ledger_path)
    taxonomy_adapter = build_taxonomy_adapter(settings.storage)
    prompt_provider = JsonPromptProvider(
        prompts_path=settings.storage.prompts_path,
        skills_dir=settings.storage.skills_dir,
        language=settings.pipeline.language,
    )

    llm_adapter = MockLLMAdapter(
        responses=[
            _valid_fluid_prose_markdown(),
            _valid_gap_filler_markdown(),
            _valid_long_expander_markdown(),
            _valid_wide_expander_markdown(),
        ]
    )
    from cresmo.application.pipeline.models import PipelineDependencies

    stage_runner = PipelineStageRunner(
        PipelineDependencies(
            telemetry_port=NoOpTelemetryPort(),
            metrics_port=NoOpMetricsPort(),
            llm_judge=_make_passing_judge(),
            judge_blocking=True,
            judge_max_attempts=1,
            prompt_provider=prompt_provider,
            llm_transformation_port=llm_adapter,
            stage_factory=StageFactory(policy=settings.to_stage_execution_policy()),
            ledger_port=ledger_adapter,
        )
    )
    pipeline = CresmoPipeline(
        media_ingestion_port=MockMediaIngestionPort(),
        vault_port=vault_adapter,
        stage_runner=stage_runner,
        ledger_port=ledger_adapter,
        stage_policy=settings.to_stage_execution_policy(),
        taxonomy_port=taxonomy_adapter,
    )

    raw_input = tmp_path / "incoming" / "ancapsu" / "abc123xyz00.md"
    raw_input.parent.mkdir(parents=True, exist_ok=True)
    raw_input.write_text(
        "Hoje a gente vai falar sobre bancos centrais e organização fiscal.",
        encoding="utf-8",
    )

    first_result = pipeline.run_for_text_file(raw_input, expansion_max_passes=1)

    assert first_result.success is True
    assert not first_result.already_processed
    assert first_result.source_transcript is not None
    assert first_result.source_transcript.channel.name == "ancapsu"
    assert first_result.source_transcript.channel.category != "uncategorized"
    assert len(llm_adapter.call_history) == 4

    saved_fluid = vault_adapter.get_stage_transcript(StageName.FLUID_PROSE, first_result.content_id)
    saved_gap_filler = vault_adapter.get_stage_transcript(
        StageName.GAP_FILLER, first_result.content_id
    )
    saved_long_expander = vault_adapter.get_stage_transcript(
        StageName.LONG_EXPANDER, first_result.content_id
    )
    saved_wide_expander = vault_adapter.get_stage_transcript(
        StageName.WIDE_EXPANDER, first_result.content_id
    )
    assert saved_fluid is not None
    assert saved_gap_filler is not None
    assert saved_long_expander is not None
    assert saved_wide_expander is not None
    assert (data_dir / "fluid_prose" / "ancapsu" / "abc123xyz00.md").exists()
    assert (data_dir / "gap_filler" / "ancapsu" / "abc123xyz00.md").exists()
    assert (data_dir / "long_expander" / "ancapsu" / "abc123xyz00.md").exists()
    assert (data_dir / "wide_expander" / "ancapsu" / "abc123xyz00.md").exists()

    # Mark completion in real SQLite ledger and verify idempotent short-circuit reads Vault artifact
    ledger_adapter.save_entry(
        LedgerEntry(
            content_id=first_result.content_id,
            media_url="https://youtube.com/watch?v=abc123xyz00",
            title=first_result.source_transcript.content.title,
            channel_name=ChannelName(first_result.source_transcript.channel.name),
            status=PipelineStatus.COMPLETED,
            completed_at=datetime.now(UTC),
        )
    )

    second_result = pipeline.run_for_text_file(raw_input, expansion_max_passes=1)

    assert second_result.success is True
    assert second_result.already_processed is True
    assert second_result.final_transcript is not None
    assert "### Extra Info" in second_result.final_transcript.content.text
    assert len(llm_adapter.call_history) == 4
