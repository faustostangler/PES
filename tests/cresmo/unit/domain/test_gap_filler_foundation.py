"""Unit tests for Gap Filler domain criteria, mechanical invariants, and post-processor.

Conforms to:
    - ADR-028: Decoupling Fluid Prose and Gap Filler
    - ADR-031: Standardized StageConfig and Reflection Quality Fabric
    - ADR-039: Canonical Quality Gates and Two-Layered Topology
"""

from __future__ import annotations

from cresmo.domain.entities.transcripts import StageTranscript
from cresmo.domain.services.convergence_evaluator import evaluate_semantic_convergence
from cresmo.domain.services.prose_syntax_guard import validate_expanded_prose_syntax
from cresmo.domain.services.stage_post_processor import post_process_expanded_transcript
from cresmo.domain.stage_registry import StageRegistry
from cresmo.domain.value_objects import (
    CandidateText,
    Channel,
    Content,
    ContentId,
    JudgeCriterion,
    MediaProvenance,
    PromptKey,
    SaturationReason,
    SaturationThresholds,
)


def test_gap_filler_judge_criteria_enum() -> None:
    """Verify specialized gap_filler criteria are registered in JudgeCriterion."""
    assert JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION == "epistemic_grounding_segregation"
    assert (
        JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION == "conceptual_mechanical_decomposition"
    )
    assert JudgeCriterion.BRAUDELIAN_STRATIFICATION == "braudelian_stratification"
    assert JudgeCriterion.GENEALOGY_HIDDEN_AGENCY == "genealogy_hidden_agency"
    assert JudgeCriterion.COMPETING_HYPOTHESES == "competing_hypotheses"
    assert JudgeCriterion.EXTRA_INFO_GRANULARITY == "extra_info_granularity"
    assert JudgeCriterion.LINEAR_STYLE_NATURALISM == "linear_style_naturalism"


def test_gap_filler_scoring_policy_and_weights() -> None:
    """Verify gap_filler scoring policy returns 7 canonical weights summing to 1.0 and 2 vetoes."""
    from cresmo.domain.value_objects import (
        GAP_FILLER_CANONICAL_WEIGHTS,
        GAP_FILLER_MECHANICAL_VETO_CRITERIA,
        resolve_stage_scoring_policy,
    )

    weights, vetoes = resolve_stage_scoring_policy("gap_filler")
    assert weights == GAP_FILLER_CANONICAL_WEIGHTS
    assert len(weights) == 7
    assert round(sum(weights.values()), 6) == 1.0
    assert vetoes == GAP_FILLER_MECHANICAL_VETO_CRITERIA
    assert JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION in vetoes
    assert JudgeCriterion.EXTRA_INFO_GRANULARITY in vetoes


def test_gap_filler_mechanical_invariants_valid() -> None:
    """Verify clean gap_filler output produces zero mechanical violations."""
    valid_text = (
        "## O Surgimento do Condado Portucalense\n\n"
        "Em 1096, o rei **Afonso VI de Leão** concedeu o governo a **Henrique de Borgonha**, "
        "recompensando o auxílio militar prestado contra os mouros. "
        "A autonomia política emergiu das tensões entre a nobreza local e a aristocracia galega.\n\n"
        "### Extra Info\n\n"
        "1. **Henrique de Borgonha** (1066-1112) pertencia à linhagem capetiana da Borgonha, "
        "tendo liderado contingentes cruzados no âmbito da Reconquista ibérica.\n"
        "2. A doação régia de 1096 estabeleceu laços de vassalagem estrita com a coroa leonesa."
    )
    violations = validate_expanded_prose_syntax(valid_text)
    assert violations == []


def test_gap_filler_mechanical_invariants_missing_complementary_section() -> None:
    """Verify missing '### Extra Info' triggers a mechanical violation."""
    invalid_text = "## O Surgimento de Portugal\n\nTexto corrido sem seção complementar alguma."
    violations = validate_expanded_prose_syntax(invalid_text)
    assert any("Extra Info" in v for v in violations)


def test_gap_filler_mechanical_invariants_empty_complementary_section() -> None:
    """Verify empty complementary section triggers a mechanical violation."""
    invalid_text = "## O Surgimento de Portugal\n\nTexto corrido principal.\n\n### Extra Info\n"
    violations = validate_expanded_prose_syntax(invalid_text)
    assert any("empty" in v.lower() for v in violations)


def test_gap_filler_mechanical_invariants_prohibits_em_dash_and_tables() -> None:
    """Verify em-dashes and markdown tables are rejected by mechanical preflight."""
    text_with_em_dash = (
        "## Título\n\nO rei — figura central — viajou.\n\n### Extra Info\n\n1. Detalhes."
    )
    assert any("em-dash" in v.lower() for v in validate_expanded_prose_syntax(text_with_em_dash))

    text_with_table = (
        "## Título\n\n| Col1 | Col2 |\n| --- | --- |\n| A | B |\n\n### Extra Info\n\n1. Detalhes."
    )
    assert any("table" in v.lower() for v in validate_expanded_prose_syntax(text_with_table))


def test_gap_filler_mechanical_invariants_prohibits_bullets_in_main_body() -> None:
    """Verify bullet points in main body are rejected by mechanical preflight."""
    text_with_bullets = "## Título\n\n* Item 1\n* Item 2\n\n### Extra Info\n\n1. Detalhes."
    assert any("bullet" in v.lower() for v in validate_expanded_prose_syntax(text_with_bullets))


def test_semantic_convergence_plateau_detected() -> None:
    """Verify semantic plateau is detected when all candidate units match baseline vectors above threshold."""
    baseline_vectors = [[1.0, 0.0], [0.0, 1.0]]
    current_vectors = [[0.99, 0.14], [0.14, 0.99]]

    verdict = evaluate_semantic_convergence(
        baseline_vectors,
        current_vectors,
        SaturationThresholds(semantic_similarity_threshold=0.88),
        lexical_jaccard=0.45,
        word_delta_ratio=0.05,
        provider="semantic",
    )

    assert verdict.is_saturated is True
    assert verdict.reason is SaturationReason.SEMANTIC_PLATEAU
    assert verdict.preserve_baseline is False
    assert verdict.novel_paragraphs == 0
    assert verdict.total_paragraphs == 2


def test_semantic_convergence_novel_content_detected_when_new_unit_added() -> None:
    """Verify semantic saturation is NOT triggered when a candidate unit introduces orthogonal semantics."""
    baseline_vectors = [[1.0, 0.0]]
    current_vectors = [[1.0, 0.0], [0.0, 1.0]]

    verdict = evaluate_semantic_convergence(
        baseline_vectors,
        current_vectors,
        SaturationThresholds(semantic_similarity_threshold=0.88),
        lexical_jaccard=0.40,
        word_delta_ratio=0.25,
        provider="semantic",
    )

    assert verdict.is_saturated is False
    assert verdict.reason is SaturationReason.NOVEL_CONTENT
    assert verdict.preserve_baseline is False
    assert verdict.novel_paragraphs == 1
    assert verdict.total_paragraphs == 2


def test_post_process_expanded_transcript() -> None:
    """Verify post_process_expanded_transcript maps StageTranscript triad to StageTranscript."""
    source_fluid = StageTranscript(
        channel=Channel(name="Canal História"),
        provenance=MediaProvenance.create(url="https://youtube.com/watch?v=vid_123"),
        content=Content(
            id=ContentId("vid_123"),
            title="Fundação de Portugal",
            text="## Origens\n\nTexto em prosa fluida.",
        ),
    )

    candidate_text = (
        "# Fundação de Portugal\n\n"
        "## O Condado Portucalense\n\n"
        "Prosa densa expandida sem tabelas e sem travessões.\n\n"
        "### Extra Info\n\n"
        "1. **Afonso Henriques** foi o primeiro rei de Portugal."
    )

    candidate = CandidateText(text=candidate_text, stage_name="gap_filler")
    expanded = post_process_expanded_transcript(candidate, source_fluid)

    assert isinstance(expanded, StageTranscript)
    assert expanded.content.id == ContentId("vid_123")
    assert expanded.content.title == "Fundação de Portugal"
    assert "### Extra Info" in expanded.content.text
    assert "Afonso Henriques" in expanded.content.text
    assert expanded.provenance.url == "https://youtube.com/watch?v=vid_123"


def test_stage_registry_contains_gap_filler() -> None:
    """Verify gap_filler and long_expander are officially registered in StageRegistry."""
    assert StageRegistry.contains("gap_filler") is True
    spec = StageRegistry.get("gap_filler")
    assert spec.transform_prompt_key == PromptKey.GAP_FILLER

    assert StageRegistry.contains("long_expander") is True
    long_spec = StageRegistry.get("long_expander")
    assert long_spec.transform_prompt_key == PromptKey.LONG_EXPANDER
    assert long_spec.judge_prompt_key == PromptKey.JUDGE_LONG_EXPANDER
    assert len(spec.required_criteria) == 7
    assert JudgeCriterion.EPISTEMIC_GROUNDING_SEGREGATION in spec.required_criteria
    assert JudgeCriterion.CONCEPTUAL_MECHANICAL_DECOMPOSITION in spec.required_criteria
    assert JudgeCriterion.BRAUDELIAN_STRATIFICATION in spec.required_criteria
    assert JudgeCriterion.GENEALOGY_HIDDEN_AGENCY in spec.required_criteria
    assert JudgeCriterion.COMPETING_HYPOTHESES in spec.required_criteria
    assert JudgeCriterion.EXTRA_INFO_GRANULARITY in spec.required_criteria
    assert JudgeCriterion.LINEAR_STYLE_NATURALISM in spec.required_criteria
    assert spec.post_processor is not None
