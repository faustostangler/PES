"""Unit tests for transcript indexing text validation, sanitization, and parsing utilities.

Following Doctor Stangler Architecture Method (TDD Red-Green-Refactor).
Conforms to:
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
- ADR-049: Application Layer Mutation Blindage (>=99.0%)
"""

from __future__ import annotations

from cresmo.application.use_cases.indexing.validators import (
    _FORBIDDEN_PREFIX_REGEX,
    _INDICATIVE_PREFIXES,
    clean_concept_line,
    clean_text_line,
    is_valid_concepts_output,
    is_valid_synthesis_paragraph,
)


class TestForbiddenPrefixRegex:
    def test_matches_various_forbidden_prefixes(self) -> None:
        forbidden = [
            "Key Concept: Domain Modeling",
            "Key Concepts: A, B",
            "Keywords: X, Y",
            "Palavras-chave: teste",
            "Conceito: Pureza",
            "Conceitos-chave: A, B",
            "Tópicos: Alpha",
            "Termo-chave: Beta",
            "Síntese: Resumo",
            "Sintese Conceitual: Resumo",
            "Synthesis: Summary",
            "Linha 1: Conceito",
            "Line 2: Detalhe",
            "**Key Concept:** Invariante",
            "### Síntese - Texto",
            "Palavra-chave — Exemplo",
        ]
        for f in forbidden:
            assert _FORBIDDEN_PREFIX_REGEX.search(f) is not None, f"Failed to match: {f}"

    def test_does_not_match_valid_content(self) -> None:
        valid = [
            "Domain-Driven Design and Hexagonal Purity",
            "A fast distributed pipeline",
            "Arquitetura Limpa em Sistemas Complexos",
            "O conceito fundamental da teoria dos jogos",
        ]
        for v in valid:
            assert _FORBIDDEN_PREFIX_REGEX.search(v) is None, f"Unexpected match: {v}"


class TestIsValidConceptsOutput:
    def test_empty_or_whitespace_is_invalid(self) -> None:
        assert is_valid_concepts_output("") is False
        assert is_valid_concepts_output("   \n\t  ") is False

    def test_forbidden_prefix_is_invalid(self) -> None:
        assert is_valid_concepts_output("Key Concepts: Hexagonal Architecture") is False
        assert is_valid_concepts_output("## Conceitos-chave: DDD, TDD") is False
        assert is_valid_concepts_output('"Keywords:" Event Sourcing') is False
        assert is_valid_concepts_output("*Key Concept:* Event Sourcing") is False
        assert is_valid_concepts_output("`Key Concept:` Event Sourcing") is False
        assert is_valid_concepts_output("_Key Concept:_ Event Sourcing") is False

    def test_clean_concept_string_is_valid(self) -> None:
        assert (
            is_valid_concepts_output("Domain Entities, Value Objects, Hexagonal Architecture")
            is True
        )
        assert is_valid_concepts_output("Idempotency, Outbox Pattern") is True


class TestIsValidSynthesisParagraph:
    def test_empty_or_whitespace_is_invalid(self) -> None:
        assert is_valid_synthesis_paragraph("") is False
        assert is_valid_synthesis_paragraph("   \n\t  ") is False

    def test_forbidden_prefix_is_invalid(self) -> None:
        assert is_valid_synthesis_paragraph("Síntese: " + "word " * 30) is False
        assert is_valid_synthesis_paragraph("**Synthesis:** " + "word " * 30) is False

    def test_multiple_paragraphs_separated_by_blank_line_is_invalid(self) -> None:
        p1 = "word " * 15
        p2 = "word " * 15
        assert is_valid_synthesis_paragraph(f"{p1}\n\n{p2}") is False

    def test_bullet_or_numbered_list_is_invalid(self) -> None:
        content = "Intro\n- Point A\n- Point B\n" + ("word " * 20)
        assert is_valid_synthesis_paragraph(content) is False
        content_star = "Intro\n* Point A\n" + ("word " * 20)
        assert is_valid_synthesis_paragraph(content_star) is False
        content_num = "Intro\n1. Point A\n" + ("word " * 20)
        assert is_valid_synthesis_paragraph(content_num) is False
        content_num2 = "Intro\n2. Point B\n" + ("word " * 20)
        assert is_valid_synthesis_paragraph(content_num2) is False
        content_bullet = "Intro\n• Point A\n" + ("word " * 20)
        assert is_valid_synthesis_paragraph(content_bullet) is False

    def test_word_count_boundaries(self) -> None:
        # Default min=20, max=120
        words_19 = " ".join(["token"] * 19)
        assert is_valid_synthesis_paragraph(words_19) is False

        words_20 = " ".join(["token"] * 20)
        assert is_valid_synthesis_paragraph(words_20) is True

        words_120 = " ".join(["token"] * 120)
        assert is_valid_synthesis_paragraph(words_120) is True

        words_121 = " ".join(["token"] * 121)
        assert is_valid_synthesis_paragraph(words_121) is False

    def test_custom_word_count_limits(self) -> None:
        words_5 = "one two three four five"
        assert is_valid_synthesis_paragraph(words_5, min_words=5, max_words=10) is True
        assert is_valid_synthesis_paragraph(words_5, min_words=6, max_words=10) is False


class TestCleanTextLine:
    def test_strips_markdown_formatting_and_quotes(self) -> None:
        assert clean_text_line('**"Domain Models"**') == "Domain Models"
        assert clean_text_line("`#_Hexagonal Architecture_#`") == "Hexagonal Architecture"

    def test_strips_indicative_prefixes(self) -> None:
        for prefix in _INDICATIVE_PREFIXES:
            sample = f"{prefix} Clean Target String"
            assert clean_text_line(sample) == "Clean Target String"

        # Chained indicative prefixes in order
        assert clean_text_line("Conceito: Síntese: Chained Clean Text") == "Chained Clean Text"


class TestCleanConceptLine:
    def test_strips_forbidden_prefixes_and_joins_concepts(self) -> None:
        raw = "Key Concepts: Entity, Value Object, Aggregate Root"
        cleaned = clean_concept_line(raw)
        assert cleaned == "Entity, Value Object, Aggregate Root"

    def test_splits_and_ignores_empty_parts(self) -> None:
        raw = "Concept Alpha, , Concept Beta, ***"
        cleaned = clean_concept_line(raw)
        assert cleaned == "Concept Alpha, Concept Beta"

    def test_empty_concept_line_falls_back_to_default(self) -> None:
        assert clean_concept_line("") == "Síntese Conceitual"
        assert clean_concept_line("Key Concepts:") == "Síntese Conceitual"
        assert clean_concept_line(":::") == "Síntese Conceitual"
        assert clean_concept_line('***"""___') == "Síntese Conceitual"
