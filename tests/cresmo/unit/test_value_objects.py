"""Unit tests for Cresmo Domain Value Objects.

Derived from SPEC-001 Section 2.1 & Section 5.
Verifies construction invariants, zero primitive obsession, and boundary validation.
"""

import pytest

from cresmo.domain.exceptions import DomainValidationError, NoteTypologyError
from cresmo.domain.value_objects import (
    AtomicEntityInventory,
    CausalMatrix,
    ContentId,
    CrossContextRelations,
    NoteTitle,
    NoteType,
)


class TestContentId:
    """SPEC-001 §2.1: ContentId validation."""

    def test_valid_content_id(self) -> None:
        cid = ContentId("dQw4w9WgXcQ")
        assert cid.value == "dQw4w9WgXcQ"
        assert str(cid) == "dQw4w9WgXcQ"

    def test_empty_content_id_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            ContentId("")

    def test_whitespace_content_id_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            ContentId("   ")

    def test_invalid_characters_in_content_id_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            ContentId("invalid/id#special!")


class TestNoteTitle:
    """SPEC-001 §2.1: NoteTitle validation & sanitization."""

    def test_valid_note_title(self) -> None:
        title = NoteTitle("Teoria das Elites")
        assert title.value == "Teoria das Elites"
        assert str(title) == "Teoria das Elites"

    def test_strips_brackets_from_title(self) -> None:
        title = NoteTitle("[[Teoria das Elites]]")
        assert title.value == "Teoria das Elites"

    def test_sanitizes_illegal_filesystem_characters(self) -> None:
        title = NoteTitle("Teoria / Elites: Modelo?")
        assert "/" not in title.value
        assert ":" not in title.value
        assert "?" not in title.value

    def test_empty_title_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            NoteTitle("")

    def test_generic_placeholder_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            NoteTitle("Untitled_Note")


class TestNoteType:
    """SPEC-001 §2.1: NoteType enum parsing."""

    @pytest.mark.parametrize("raw,expected", [
        ("concept", NoteType.CONCEPT),
        ("CONCEPT", NoteType.CONCEPT),
        ("entity", NoteType.ENTITY),
        ("event", NoteType.EVENT),
        ("process", NoteType.PROCESS),
    ])
    def test_valid_note_types(self, raw: str, expected: NoteType) -> None:
        assert NoteType.from_string(raw) == expected

    def test_invalid_note_type_raises_typology_error(self) -> None:
        with pytest.raises(NoteTypologyError):
            NoteType.from_string("invalid_type")


class TestCausalMatrix:
    """SPEC-001 §2.1: CausalMatrix validation."""

    def test_valid_causal_matrix(self) -> None:
        matrix = CausalMatrix(
            cause="Centralização fiscal",
            effect="Dependência municipal",
            epistemic_attribution="Tocqueville",
        )
        assert matrix.cause == "Centralização fiscal"
        assert matrix.effect == "Dependência municipal"
        assert matrix.epistemic_attribution == "Tocqueville"

    def test_whitespace_trimmed_in_causal_matrix(self) -> None:
        matrix = CausalMatrix(
            cause="  Causa  ",
            effect="  Efeito  ",
            epistemic_attribution="  Fonte  ",
        )
        assert matrix.cause == "Causa"
        assert matrix.effect == "Efeito"
        assert matrix.epistemic_attribution == "Fonte"

    def test_empty_cause_with_effect_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            CausalMatrix(cause="", effect="Efeito")


class TestAtomicEntityInventory:
    """SPEC-001 §2.1: AtomicEntityInventory validation."""

    def test_valid_inventory(self) -> None:
        t1 = NoteTitle("Conceito A")
        t2 = NoteTitle("Conceito B")
        inv = AtomicEntityInventory(items=((t1, NoteType.CONCEPT), (t2, NoteType.ENTITY)))
        assert len(inv.items) == 2

    def test_duplicate_titles_in_inventory_raises_validation_error(self) -> None:
        t1 = NoteTitle("Conceito A")
        with pytest.raises(DomainValidationError):
            AtomicEntityInventory(items=((t1, NoteType.CONCEPT), (t1, NoteType.ENTITY)))

    def test_empty_inventory_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError):
            AtomicEntityInventory(items=())


class TestCrossContextRelations:
    """CrossContextRelations validation and stripping."""

    def test_cross_context_strips_whitespace(self) -> None:
        cc = CrossContextRelations(
            precursors="  Precursor  ",
            lateral_events="  Lateral  ",
            aftermath="  Aftermath  ",
        )
        assert cc.precursors == "Precursor"
        assert cc.lateral_events == "Lateral"
        assert cc.aftermath == "Aftermath"
