"""Hermetic unit tests for pure Domain Policy Value Objects (ADR-074)."""

from __future__ import annotations

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
        assert policy.saturation_thresholds == SaturationThresholds()
        from cresmo.domain.value_objects import ConvergenceMode

        assert policy.resolve_max_passes("long_expander", ConvergenceMode.HYBRID_SEMANTIC) == 7
        assert policy.resolve_max_passes("gap_filler", ConvergenceMode.HYBRID_SEMANTIC) == 5
        assert policy.resolve_max_passes("fluid_prose", ConvergenceMode.NONE) == 1

        with pytest.raises(FrozenInstanceError):
            policy.expansion_max_passes = 3  # type: ignore[misc]

    def test_valid_boundary_values(self) -> None:
        custom_thresholds = SaturationThresholds(lexical_identity_threshold=0.9)
        low = StageExecutionPolicy(
            expansion_max_passes=1,
            long_expander_max_passes=1,
            judge_max_attempts=1,
            judge_blocking=True,
            saturation_thresholds=custom_thresholds,
        )
        assert low.expansion_max_passes == 1
        assert low.long_expander_max_passes == 1
        assert low.judge_max_attempts == 1
        assert low.judge_blocking is True
        assert low.saturation_thresholds is custom_thresholds

        high = StageExecutionPolicy(
            expansion_max_passes=10,
            long_expander_max_passes=10,
        )
        assert high.expansion_max_passes == 10
        assert high.long_expander_max_passes == 10

    @pytest.mark.parametrize(
        ("kwargs", "expected_msg"),
        [
            ({"expansion_max_passes": 0}, "expansion_max_passes must be >= 1, got 0."),
            ({"expansion_max_passes": 11}, "expansion_max_passes must be <= 10, got 11."),
            ({"expansion_max_passes": True}, "expansion_max_passes must be an integer, got True."),
            ({"expansion_max_passes": "5"}, "expansion_max_passes must be an integer, got '5'."),
            ({"long_expander_max_passes": 0}, "long_expander_max_passes must be >= 1, got 0."),
            ({"long_expander_max_passes": 11}, "long_expander_max_passes must be <= 10, got 11."),
            (
                {"long_expander_max_passes": False},
                "long_expander_max_passes must be an integer, got False.",
            ),
            ({"judge_max_attempts": 0}, "judge_max_attempts must be >= 1, got 0."),
            ({"judge_max_attempts": -1}, "judge_max_attempts must be >= 1, got -1."),
            ({"judge_max_attempts": True}, "judge_max_attempts must be an integer, got True."),
            ({"judge_blocking": 1}, "judge_blocking must be a bool, got 1."),
            ({"judge_blocking": "false"}, "judge_blocking must be a bool, got 'false'."),
            (
                {"saturation_thresholds": "invalid"},
                "saturation_thresholds must be a SaturationThresholds instance.",
            ),
            (
                {"saturation_thresholds": None},
                "saturation_thresholds must be a SaturationThresholds instance.",
            ),
        ],
    )
    def test_invalid_inputs_raise_domain_validation_error(
        self, kwargs: dict[str, Any], expected_msg: str
    ) -> None:
        with pytest.raises(DomainValidationError) as exc_info:
            StageExecutionPolicy(**kwargs)
        assert exc_info.value.args[0] == expected_msg


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
        ("kwargs", "expected_msg"),
        [
            ({"lookback_days": -1}, "lookback_days must be >= 0, got -1."),
            ({"lookback_days": False}, "lookback_days must be an integer, got False."),
            ({"lookback_days": "30"}, "lookback_days must be an integer, got '30'."),
            ({"discovery_workers": 0}, "discovery_workers must be >= 1, got 0."),
            ({"discovery_workers": True}, "discovery_workers must be an integer, got True."),
            ({"queue_maxsize": 0}, "queue_maxsize must be >= 1, got 0."),
            ({"queue_maxsize": True}, "queue_maxsize must be an integer, got True."),
            ({"enable_channel_crawler": 0}, "enable_channel_crawler must be a bool, got 0."),
            (
                {"enable_channel_crawler": "true"},
                "enable_channel_crawler must be a bool, got 'true'.",
            ),
        ],
    )
    def test_invalid_inputs_raise_domain_validation_error(
        self, kwargs: dict[str, Any], expected_msg: str
    ) -> None:
        with pytest.raises(DomainValidationError) as exc_info:
            DiscoveryPolicy(**kwargs)
        assert exc_info.value.args[0] == expected_msg


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
        ("max_words", "expected_msg"),
        [
            (0, "max_words must be >= 1, got 0."),
            (-1, "max_words must be >= 1, got -1."),
            (True, "max_words must be an integer, got True."),
            (False, "max_words must be an integer, got False."),
            (100.5, "max_words must be an integer, got 100.5."),
            ("500", "max_words must be an integer, got '500'."),
        ],
    )
    def test_invalid_max_words_raises_domain_validation_error(
        self, max_words: Any, expected_msg: str
    ) -> None:
        with pytest.raises(DomainValidationError) as exc_info:
            CompendiumRolloverPolicy(max_words=max_words)
        assert exc_info.value.args[0] == expected_msg
