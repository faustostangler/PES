"""Unit tests for BatchId Domain Value Object.

Conforms to ADR-035:
- 1 Trace = 1 Work Item.
- Batch correlation via canonical SOTA-KISS batch_id: YYYYMMDD_HHMMSS_[UUID6].
- Domain validation invariants, regex checks, factory method, and immutability.
"""

from __future__ import annotations

import datetime
import re
from dataclasses import FrozenInstanceError

import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import BatchId

CANONICAL_BATCH_ID_REGEX = re.compile(r"^\d{8}_\d{6}_[a-f0-9]{6}$")


class TestBatchId:
    """SPEC / ADR-035: BatchId domain Value Object contracts and invariants."""

    def test_valid_batch_id(self) -> None:
        raw_val = "20261003_203603_a1b2c3"
        batch_id = BatchId(f"  {raw_val}  ")
        assert batch_id.value == raw_val
        assert str(batch_id) == raw_val

    def test_generate_factory_creates_canonical_format(self) -> None:
        batch_id = BatchId.generate()
        assert isinstance(batch_id, BatchId)
        assert CANONICAL_BATCH_ID_REGEX.match(batch_id.value) is not None

    def test_generate_uses_utc_timezone(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import cresmo.domain.value_objects.identity as id_mod

        called_tz: list[datetime.tzinfo | None] = []

        class FakeDatetime:
            UTC = datetime.UTC

            class datetime:
                @staticmethod
                def now(tz: datetime.tzinfo | None = None) -> datetime.datetime:
                    called_tz.append(tz)
                    if tz is not datetime.UTC:
                        raise ValueError(f"Expected UTC, got {tz}")
                    return datetime.datetime(2026, 10, 8, 12, 0, 0, tzinfo=tz)

        monkeypatch.setattr(id_mod, "datetime", FakeDatetime)
        b = BatchId.generate()
        assert b.value.startswith("20261008_120000_")
        assert called_tz == [datetime.UTC]

    def test_generate_produces_unique_identifiers(self) -> None:
        batch_id_1 = BatchId.generate()
        batch_id_2 = BatchId.generate()
        assert batch_id_1 != batch_id_2
        assert batch_id_1.value != batch_id_2.value

    def test_empty_batch_id_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match=r"^BatchId cannot be empty\.$"):
            BatchId("")

    def test_whitespace_batch_id_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match=r"^BatchId cannot be empty\.$"):
            BatchId("   ")

    def test_invalid_format_raises_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match="Invalid BatchId format"):
            BatchId("invalid-format-without-timestamp")

        with pytest.raises(DomainValidationError, match="Invalid BatchId format"):
            BatchId("20261003_203603")  # missing uuid6 suffix

        with pytest.raises(DomainValidationError, match="Invalid BatchId format"):
            BatchId("20261003_203603_toolonguuid123")  # suffix not 6 chars

    def test_immutability(self) -> None:
        batch_id = BatchId("20261003_203603_a1b2c3")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            batch_id.value = "20261003_203603_ffffff"  # type: ignore
