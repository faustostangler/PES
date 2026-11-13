"""Unit tests for transcript indexing text validation, sanitization, and parsing utilities.

Following Doctor Stangler Architecture Method (TDD Red-Green-Refactor).
Conforms to:
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
- ADR-049: Application Layer Mutation Blindage (>=99.0%)
"""

from __future__ import annotations

import pytest

from cresmo.application.use_cases.indexing.validators import (
    _FORBIDDEN_PREFIX_REGEX,
    _INDICATIVE_PREFIXES,
    can_retry,
    clean_concept_line,
    clean_text_line,
    is_valid_concepts_output,
    is_valid_raw_index_output,
    is_valid_synthesis_paragraph,
    parse_judge_boolean,
    parse_raw_index_response,
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


class TestIsValidRawIndexOutput:
    def test_empty_or_whitespace_is_invalid(self) -> None:
        assert is_valid_raw_index_output("") is False
        assert is_valid_raw_index_output("   \n\t  ") is False

    def test_forbidden_prefix_on_first_line_is_invalid(self) -> None:
        assert is_valid_raw_index_output("Key Concept: DDD\nSíntese aqui") is False
        assert is_valid_raw_index_output("**Key Concept:** DDD\nSíntese aqui") is False
        assert is_valid_raw_index_output("Linha 1: Conceito\nLinha 2: Texto") is False

    def test_multiline_valid_output(self) -> None:
        valid_multiline = "Domain Entities, Value Objects\nThis is the paratactic synthesis describing domain logic."
        assert is_valid_raw_index_output(valid_multiline) is True

    def test_multiline_exactly_two_lines_without_comma_is_valid(self) -> None:
        exact_two_lines = "Domain Entities\nParatactic synthesis without any comma"
        assert is_valid_raw_index_output(exact_two_lines) is True

    def test_forbidden_prefix_wrapped_in_markdown_decorations_is_invalid(self) -> None:
        assert is_valid_raw_index_output('*Key Concept:* DDD\nSynthesis here') is False
        assert is_valid_raw_index_output('`Key Concept:` DDD\nSynthesis here') is False
        assert is_valid_raw_index_output('"Key Concept:" DDD\nSynthesis here') is False
        assert is_valid_raw_index_output('_Key Concept:_ DDD\nSynthesis here') is False
        assert is_valid_raw_index_output('# Key Concept: DDD\nSynthesis here') is False

    def test_single_line_with_comma_is_valid(self) -> None:
        valid_single = "Domain Entities, This is a concise synthesis."
        assert is_valid_raw_index_output(valid_single) is True

    def test_single_line_without_comma_is_invalid(self) -> None:
        invalid_single = "Single Line Without Any Comma In It"
        assert is_valid_raw_index_output(invalid_single) is False


class TestIsValidConceptsOutput:
    def test_empty_or_whitespace_is_invalid(self) -> None:
        assert is_valid_concepts_output("") is False
        assert is_valid_concepts_output("   \n\t  ") is False

    def test_forbidden_prefix_is_invalid(self) -> None:
        assert is_valid_concepts_output("Key Concepts: Hexagonal Architecture") is False
        assert is_valid_concepts_output("## Conceitos-chave: DDD, TDD") is False
        assert is_valid_concepts_output('"Keywords:" Event Sourcing') is False
        assert is_valid_concepts_output('*Key Concept:* Event Sourcing') is False
        assert is_valid_concepts_output('`Key Concept:` Event Sourcing') is False
        assert is_valid_concepts_output('_Key Concept:_ Event Sourcing') is False

    def test_clean_concept_string_is_valid(self) -> None:
        assert is_valid_concepts_output("Domain Entities, Value Objects, Hexagonal Architecture") is True
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


class TestCanRetry:
    def test_infinite_retries_when_max_rewrites_non_positive(self) -> None:
        assert can_retry(attempts=0, max_rewrites=0) is True
        assert can_retry(attempts=10, max_rewrites=0) is True
        assert can_retry(attempts=99, max_rewrites=-1) is True

    def test_bounded_retries(self) -> None:
        assert can_retry(attempts=0, max_rewrites=3) is True
        assert can_retry(attempts=1, max_rewrites=3) is True
        assert can_retry(attempts=2, max_rewrites=3) is True
        assert can_retry(attempts=3, max_rewrites=3) is False
        assert can_retry(attempts=4, max_rewrites=3) is False


class TestParseJudgeBoolean:
    def test_empty_or_whitespace_is_false(self) -> None:
        assert parse_judge_boolean("") is False
        assert parse_judge_boolean("   ") is False

    def test_true_variations(self) -> None:
        assert parse_judge_boolean("true") is True
        assert parse_judge_boolean("True") is True
        assert parse_judge_boolean("TRUE") is True
        assert parse_judge_boolean("true.") is True
        assert parse_judge_boolean("true!") is True
        assert parse_judge_boolean("true?") is True
        assert parse_judge_boolean("```\ntrue\n```") is True
        assert parse_judge_boolean("```json\ntrue\n```") is True
        assert parse_judge_boolean("```txt\nTrue.\n```") is True
        assert parse_judge_boolean("true, the output satisfies criteria") is True
        assert parse_judge_boolean("(true)") is True

    def test_false_variations(self) -> None:
        assert parse_judge_boolean("false") is False
        assert parse_judge_boolean("False") is False
        assert parse_judge_boolean("```json\nfalse\n```") is False
        assert parse_judge_boolean("not compliant") is False


class TestCleanTextLine:
    def test_strips_markdown_formatting_and_quotes(self) -> None:
        assert clean_text_line('**"Domain Models"**') == "Domain Models"
        assert clean_text_line('`#_Hexagonal Architecture_#`') == "Hexagonal Architecture"

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


class TestParseRawIndexResponse:
    def test_empty_response_uses_fallbacks(self) -> None:
        c, s = parse_raw_index_response("", fallback_title="Fallback Title")
        assert c == "Síntese Conceitual"
        assert s == "Fallback Title"

    def test_multiline_response_parsing(self) -> None:
        raw = "DDD, Hexagonal\nLine 1 of synthesis\nLine 2 of synthesis"
        c, s = parse_raw_index_response(raw, fallback_title="Fallback")
        assert c == "DDD, Hexagonal"
        assert s == "Line 1 of synthesis Line 2 of synthesis"

    def test_single_line_with_comma_parsing(self) -> None:
        raw = "Event Sourcing, Appends state transitions to ledger"
        c, s = parse_raw_index_response(raw, fallback_title="Fallback")
        assert c == "Event Sourcing"
        assert s == "Appends state transitions to ledger"

    def test_single_line_without_comma_parsing(self) -> None:
        raw = "Direct single line summary of content"
        c, s = parse_raw_index_response(raw, fallback_title="Fallback")
        assert c == "Síntese Conceitual"
        assert s == "Direct single line summary of content"

    def test_single_line_with_multiple_commas_splits_on_first_only(self) -> None:
        raw = "Concept Alpha, Synthesis clause 1, synthesis clause 2, synthesis clause 3"
        c, s = parse_raw_index_response(raw, fallback_title="Fallback")
        assert c == "Concept Alpha"
        assert s == "Synthesis clause 1, synthesis clause 2, synthesis clause 3"

    def test_single_line_with_empty_concept_or_synthesis_uses_fallbacks(self) -> None:
        c1, s1 = parse_raw_index_response(", Synthesis text here", fallback_title="Fallback")
        assert c1 == "Síntese Conceitual"
        assert s1 == "Synthesis text here"

        c2, s2 = parse_raw_index_response("Concept Only,", fallback_title="Fallback Title")
        assert c2 == "Concept Only"
        assert s2 == "Fallback Title"

    def test_multiline_with_empty_synthesis_uses_fallback(self) -> None:
        raw = "Domain Concept\n***\n___"
        c, s = parse_raw_index_response(raw, fallback_title="Fallback Title")
        assert c == "Domain Concept"
        assert s == "Fallback Title"

    def test_fallback_when_parts_empty(self) -> None:
        raw = "Key Concepts:\n"
        c, s = parse_raw_index_response(raw, fallback_title="Fallback Title")
        assert c == "Síntese Conceitual"
        assert s == "Fallback Title"
