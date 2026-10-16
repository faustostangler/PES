"""Unit tests for Gap Filler domain criteria, mechanical invariants, and post-processor.

Conforms to:
    - ADR-028: Decoupling Fluid Prose and Gap Filler
    - ADR-031: Standardized StageConfig and Reflection Quality Fabric
    - ADR-039: Canonical Quality Gates and Two-Layered Topology
"""

from __future__ import annotations

from cresmo.domain.entities.compendium import (
    EnrichedCompendium,
    post_process_enriched_compendium,
)
from cresmo.domain.entities.transcripts import FluidTranscript
from cresmo.domain.services.mechanical_validator import (
    check_complementary_mechanical_saturation,
    validate_gap_filler_mechanical_invariants,
)
from cresmo.domain.stage_registry import StageRegistry
from cresmo.domain.value_objects import (
    CandidateText,
    ContentId,
    JudgeCriterion,
    PromptKey,
)


def test_gap_filler_judge_criteria_enum() -> None:
    """Verify specialized gap_filler criteria are registered in JudgeCriterion."""
    assert JudgeCriterion.FACTUAL_GROUNDING == "factual_grounding"
    assert JudgeCriterion.SOCRATIC_EPISTEMIC_DEPTH == "socratic_epistemic_depth"
    assert JudgeCriterion.CAUSAL_STRATIFICATION_AGENCY == "causal_stratification_agency"
    assert JudgeCriterion.COMPLEMENTARY_SUBSTANCE == "complementary_substance"
    assert JudgeCriterion.AUTHORIAL_NATURALISM == "authorial_naturalism"
    assert JudgeCriterion.EPISTEMIC_SATURATION == "epistemic_saturation"


def test_gap_filler_mechanical_invariants_valid() -> None:
    """Verify clean gap_filler output produces zero mechanical violations."""
    valid_text = (
        "## O Surgimento do Condado Portucalense\n\n"
        "Em 1096, o rei **Afonso VI de Leão** concedeu o governo a **Henrique de Borgonha**, "
        "recompensando o auxílio militar prestado contra os mouros. "
        "A autonomia política emergiu das tensões entre a nobreza local e a aristocracia galega.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** (1066-1112) pertencia à linhagem capetiana da Borgonha, "
        "tendo liderado contingentes cruzados no âmbito da Reconquista ibérica.\n"
        "2. A doação régia de 1096 estabeleceu laços de vassalagem estrita com a coroa leonesa."
    )
    violations = validate_gap_filler_mechanical_invariants(valid_text)
    assert violations == []


def test_gap_filler_mechanical_invariants_missing_complementary_section() -> None:
    """Verify missing '## Informações Complementares' triggers a mechanical violation."""
    invalid_text = (
        "## O Surgimento de Portugal\n\n"
        "Texto corrido sem seção complementar alguma."
    )
    violations = validate_gap_filler_mechanical_invariants(invalid_text)
    assert any("Informações Complementares" in v for v in violations)


def test_gap_filler_mechanical_invariants_empty_complementary_section() -> None:
    """Verify empty complementary section triggers a mechanical violation."""
    invalid_text = (
        "## O Surgimento de Portugal\n\n"
        "Texto corrido principal.\n\n"
        "## Informações Complementares\n"
    )
    violations = validate_gap_filler_mechanical_invariants(invalid_text)
    assert any("empty" in v.lower() for v in violations)


def test_gap_filler_mechanical_invariants_prohibits_em_dash_and_tables() -> None:
    """Verify em-dashes and markdown tables are rejected by mechanical preflight."""
    text_with_em_dash = (
        "## Título\n\n"
        "O rei — figura central — viajou.\n\n"
        "## Informações Complementares\n\n"
        "1. Detalhes."
    )
    assert any("em-dash" in v.lower() for v in validate_gap_filler_mechanical_invariants(text_with_em_dash))

    text_with_table = (
        "## Título\n\n"
        "| Col1 | Col2 |\n| --- | --- |\n| A | B |\n\n"
        "## Informações Complementares\n\n"
        "1. Detalhes."
    )
    assert any("table" in v.lower() for v in validate_gap_filler_mechanical_invariants(text_with_table))


def test_gap_filler_mechanical_invariants_prohibits_bullets_in_main_body() -> None:
    """Verify bullet points in main body are rejected by mechanical preflight."""
    text_with_bullets = (
        "## Título\n\n"
        "* Item 1\n* Item 2\n\n"
        "## Informações Complementares\n\n"
        "1. Detalhes."
    )
    assert any("bullet" in v.lower() for v in validate_gap_filler_mechanical_invariants(text_with_bullets))


def test_check_complementary_mechanical_saturation_detected() -> None:
    """Verify saturation detected when delta words < 5% and 100% of bold entities match."""
    prev_draft = (
        "## Corpo Principal\n\nTexto.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** nasceu em 1066 e casou com **Teresa de Leão** em 1093."
    )
    # Current draft rephrases slightly: same bold entities, word delta < 5%
    curr_draft = (
        "## Corpo Principal\n\nTexto expandido.\n\n"
        "## Informações Complementares\n\n"
        "1. O nobre **Henrique de Borgonha** nasceu no ano 1066 e casou com **Teresa de Leão** em 1093."
    )
    is_saturated = check_complementary_mechanical_saturation(prev_draft, curr_draft)
    assert is_saturated is True


def test_check_complementary_mechanical_saturation_not_detected_when_new_entities_added() -> None:
    """Verify saturation NOT triggered when new bold entities (NER) are added."""
    prev_draft = (
        "## Corpo Principal\n\nTexto.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** governou o condado."
    )
    curr_draft = (
        "## Corpo Principal\n\nTexto.\n\n"
        "## Informações Complementares\n\n"
        "1. **Henrique de Borgonha** governou o condado.\n"
        "2. **Afonso Henriques** consolidou a autonomia no **Tratado de Zamora**."
    )
    is_saturated = check_complementary_mechanical_saturation(prev_draft, curr_draft)
    assert is_saturated is False


def test_post_process_enriched_compendium() -> None:
    """Verify post_process_enriched_compendium maps FluidTranscript triad to EnrichedCompendium."""
    source_fluid = FluidTranscript.create(
        channel_name="Canal História",
        content_id="vid_123",
        title="Fundação de Portugal",
        body="## Origens\n\nTexto em prosa fluida.",
        source_url="https://youtube.com/watch?v=vid_123",
    )

    candidate_text = (
        "# Fundação de Portugal\n\n"
        "## O Condado Portucalense\n\n"
        "Prosa densa expandida sem tabelas e sem travessões.\n\n"
        "## Informações Complementares\n\n"
        "1. **Afonso Henriques** foi o primeiro rei de Portugal."
    )

    candidate = CandidateText(text=candidate_text, stage_name="gap_filler")
    compendium = post_process_enriched_compendium(candidate, source_fluid)

    assert isinstance(compendium, EnrichedCompendium)
    assert compendium.content_id == ContentId("vid_123")
    assert compendium.title.value == "Fundação de Portugal"
    assert "## Informações Complementares" not in compendium.body
    assert "Afonso Henriques" in compendium.complementary_info
    assert compendium.source_url == "https://youtube.com/watch?v=vid_123"


def test_stage_registry_contains_gap_filler() -> None:
    """Verify gap_filler is officially registered in StageRegistry."""
    assert StageRegistry.contains("gap_filler") is True
    spec = StageRegistry.get("gap_filler")
    assert spec.transform_prompt_key == PromptKey.GAP_FILLER_PASS1
    assert JudgeCriterion.FACTUAL_GROUNDING in spec.required_criteria
    assert JudgeCriterion.COMPLEMENTARY_SUBSTANCE in spec.required_criteria
    assert spec.post_processor is not None
