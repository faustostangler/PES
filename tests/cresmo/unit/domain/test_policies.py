"""Hermetic unit tests for pure Domain Policy Value Objects (ADR-074)."""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import (
    DEFAULT_LANGUAGE,
    CompendiumRolloverPolicy,
    DiscoveryPolicy,
    SaturationThresholds,
    StageExecutionPolicy,
)


class TestDefaultLanguage:
    """Verify canonical domain language constant."""

    def test_default_language_value(self) -> None:
        assert DEFAULT_LANGUAGE == "Português do Brasil"


class TestStageExecutionPolicy:
    """Verify invariants, immutability, and boundary validation for StageExecutionPolicy."""

    def test_defaults_and_immutability(self) -> None:
        policy = StageExecutionPolicy()
        assert policy.expansion_max_passes == 5
        assert policy.long_expander_max_passes == 7
        assert policy.judge_max_attempts == 2
        assert policy.judge_blocking is False
        assert policy.synthesis_temperature == 0.2
        assert policy.saturation_thresholds == SaturationThresholds()

        with pytest.raises(FrozenInstanceError):
            policy.expansion_max_passes = 3  # type: ignore[misc]

    def test_valid_boundary_values(self) -> None:
        custom_thresholds = SaturationThresholds(lexical_identity_threshold=0.9)
        low = StageExecutionPolicy(
            expansion_max_passes=1,
            long_expander_max_passes=1,
            judge_max_attempts=1,
            judge_blocking=True,
            synthesis_temperature=0.0,
            saturation_thresholds=custom_thresholds,
        )
        assert low.expansion_max_passes == 1
        assert low.long_expander_max_passes == 1
        assert low.judge_max_attempts == 1
        assert low.judge_blocking is True
        assert low.synthesis_temperature == 0.0
        assert low.saturation_thresholds is custom_thresholds

        high = StageExecutionPolicy(
            expansion_max_passes=10,
            long_expander_max_passes=10,
            synthesis_temperature=2.0,
        )
        assert high.expansion_max_passes == 10
        assert high.long_expander_max_passes == 10
        assert high.synthesis_temperature == 2.0

        no_temp = StageExecutionPolicy(synthesis_temperature=None)
        assert no_temp.synthesis_temperature is None

        int_temp = StageExecutionPolicy(synthesis_temperature=1)
        assert int_temp.synthesis_temperature == 1

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"expansion_max_passes": 0},
            {"expansion_max_passes": 11},
            {"expansion_max_passes": True},
            {"expansion_max_passes": "5"},
            {"long_expander_max_passes": 0},
            {"long_expander_max_passes": 11},
            {"long_expander_max_passes": False},
            {"judge_max_attempts": 0},
            {"judge_max_attempts": -1},
            {"judge_max_attempts": True},
            {"judge_blocking": 1},
            {"judge_blocking": "false"},
            {"synthesis_temperature": -0.01},
            {"synthesis_temperature": 2.01},
            {"synthesis_temperature": math.nan},
            {"synthesis_temperature": math.inf},
            {"synthesis_temperature": -math.inf},
            {"synthesis_temperature": True},
            {"synthesis_temperature": "0.2"},
            {"saturation_thresholds": "invalid"},
            {"saturation_thresholds": None},
        ],
    )
    def test_invalid_inputs_raise_domain_validation_error(self, kwargs: dict[str, Any]) -> None:
        with pytest.raises(DomainValidationError):
            StageExecutionPolicy(**kwargs)


class TestDiscoveryPolicy:
    """Verify invariants, immutability, and boundary validation for DiscoveryPolicy."""

    def test_defaults_and_immutability(self) -> None:
        policy = DiscoveryPolicy()
        assert policy.lookback_days == 365
        assert policy.discovery_workers == 10
        assert policy.queue_maxsize == 50
        assert policy.enable_channel_crawler is False

        with pytest.raises(FrozenInstanceError):
            policy.lookback_days = 7  # type: ignore[misc]

    def test_valid_boundary_values(self) -> None:
        policy = DiscoveryPolicy(
            lookback_days=0,
            discovery_workers=1,
            queue_maxsize=1,
            enable_channel_crawler=True,
        )
        assert policy.lookback_days == 0
        assert policy.discovery_workers == 1
        assert policy.queue_maxsize == 1
        assert policy.enable_channel_crawler is True

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"lookback_days": -1},
            {"lookback_days": False},
            {"lookback_days": "30"},
            {"discovery_workers": 0},
            {"discovery_workers": True},
            {"queue_maxsize": 0},
            {"queue_maxsize": True},
            {"enable_channel_crawler": 0},
            {"enable_channel_crawler": "true"},
        ],
    )
    def test_invalid_inputs_raise_domain_validation_error(self, kwargs: dict[str, Any]) -> None:
        with pytest.raises(DomainValidationError):
            DiscoveryPolicy(**kwargs)


class TestCompendiumRolloverPolicy:
    """Verify invariants, immutability, and boundary validation for CompendiumRolloverPolicy."""

    def test_defaults_and_immutability(self) -> None:
        policy = CompendiumRolloverPolicy()
        assert policy.max_words == 500_000

        with pytest.raises(FrozenInstanceError):
            policy.max_words = 100  # type: ignore[misc]

    def test_valid_minimum_boundary(self) -> None:
        policy = CompendiumRolloverPolicy(max_words=1)
        assert policy.max_words == 1

    @pytest.mark.parametrize(
        "max_words",
        [0, -1, True, False, 100.5, "500"],
    )
    def test_invalid_max_words_raises_domain_validation_error(self, max_words: Any) -> None:
        with pytest.raises(DomainValidationError):
            CompendiumRolloverPolicy(max_words=max_words)
