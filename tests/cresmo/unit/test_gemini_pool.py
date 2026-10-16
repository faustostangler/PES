"""Unit tests for GeminiCredentialPool and Quota-Aware Failover Rotation.

Conforms to:
    - ADR-041: Gemini Credential Pool and Quota-Aware Failover Rotation
    - SPEC-041: Gemini Credential Pool Specifications
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from cresmo.infrastructure.adapters.gemini_pool import (
    CredentialPoolExhaustedError,
    GeminiCredentialPool,
)
from cresmo.infrastructure.config import CresmoSettings


class TestGeminiCredentialPool:
    """Hermetic unit tests for GeminiCredentialPool rotation and cooldown invariants."""

    def test_credential_pool_leases_first_key_by_default(self) -> None:
        pool = GeminiCredentialPool(
            keys=["key-primary", "key-secondary"],
            client_factory=lambda k: MagicMock(name=f"Client-{k}"),
        )
        key, _client, alias = pool.lease()
        assert key == "key-primary"
        assert alias.startswith("key#0:")
        assert "key-primary" not in alias

    def test_credential_pool_rotates_to_secondary_on_quota_exhausted(self) -> None:
        pool = GeminiCredentialPool(
            keys=["key-primary", "key-secondary"],
            client_factory=lambda k: MagicMock(name=f"Client-{k}"),
        )
        # Report primary key exhausted for 100 seconds
        pool.report_quota_exhausted("key-primary", retry_delay_seconds=100.0)

        key, _client, alias = pool.lease()
        assert key == "key-secondary"
        assert alias.startswith("key#1:")

    def test_credential_pool_reverts_to_primary_once_cooldown_expires(self) -> None:
        pool = GeminiCredentialPool(
            keys=["key-primary", "key-secondary"],
            client_factory=lambda k: MagicMock(name=f"Client-{k}"),
        )
        # Report primary key exhausted for a tiny fraction of a second
        pool.report_quota_exhausted("key-primary", retry_delay_seconds=0.02)
        assert pool.lease()[0] == "key-secondary"

        # Wait for cooldown to pass
        time.sleep(0.03)

        # Primary should be leased again immediately
        key, _client, alias = pool.lease()
        assert key == "key-primary"
        assert alias.startswith("key#0:")

    def test_credential_pool_exhausted_raises_fail_fast(self) -> None:
        pool = GeminiCredentialPool(
            keys=["key-primary", "key-secondary"],
            client_factory=lambda k: MagicMock(name=f"Client-{k}"),
        )
        pool.report_quota_exhausted("key-primary", retry_delay_seconds=10.0)
        pool.report_quota_exhausted("key-secondary", retry_delay_seconds=20.0)

        with pytest.raises(CredentialPoolExhaustedError) as exc_info:
            pool.lease()

        assert exc_info.value.retry_after_seconds > 0
        assert exc_info.value.retry_after_seconds <= 10.0

    def test_pool_requires_at_least_one_key(self) -> None:
        with pytest.raises(ValueError, match="at least one API key"):
            GeminiCredentialPool(keys=[])


class TestGeminiConfigCredentialParsing:
    """Hermetic unit tests for CresmoSettings multi-key parsing."""

    def test_settings_parses_comma_separated_keys(self) -> None:
        settings = CresmoSettings(gemini_api_keys="key1,key2,key3")
        assert len(settings.gemini_api_keys) == 3
        assert [k.get_secret_value() for k in settings.gemini_api_keys] == ["key1", "key2", "key3"]
        assert settings.gemini_api_key.get_secret_value() == "key1"

    def test_settings_falls_back_to_single_gemini_api_key(self) -> None:
        settings = CresmoSettings(gemini_api_key="single-key")
        assert len(settings.gemini_api_keys) == 1
        assert settings.gemini_api_keys[0].get_secret_value() == "single-key"
        assert settings.gemini_api_key.get_secret_value() == "single-key"


class TestGeminiQuotaAndErrorScoping:
    """Hermetic unit tests for 429 quota scoping and retryDelay extraction."""

    def test_is_quota_exhausted_identifies_429_variants(self) -> None:
        from cresmo.infrastructure.adapters.gemini_pool import is_quota_exhausted_error

        assert is_quota_exhausted_error(RuntimeError("429 Resource has been exhausted")) is True
        assert is_quota_exhausted_error(RuntimeError("ResourceExhausted: Quota exceeded for project")) is True
        assert is_quota_exhausted_error(RuntimeError("Too Many Requests: rate limit hit")) is True

    def test_is_quota_exhausted_rejects_503_and_other_errors(self) -> None:
        from cresmo.infrastructure.adapters.gemini_pool import is_quota_exhausted_error

        # 503 MUST NEVER trigger rotation (ADR-041 §2.3)
        assert is_quota_exhausted_error(RuntimeError("503 The model is overloaded. Please try again later.")) is False
        assert is_quota_exhausted_error(RuntimeError("UNAVAILABLE: Server is currently under high demand")) is False
        assert is_quota_exhausted_error(ValueError("Invalid argument")) is False

    def test_parse_retry_delay_from_error(self) -> None:
        from cresmo.infrastructure.adapters.gemini_pool import parse_retry_delay_from_error

        msg1 = "ResourceExhausted: 429 Quota exceeded. Please retry in 33968s."
        assert parse_retry_delay_from_error(RuntimeError(msg1)) == 33968.0

        msg2 = "violations { description: \"retryDelay: '45.5s'\" }"
        assert parse_retry_delay_from_error(RuntimeError(msg2)) == 45.5

        msg3 = "Unknown quota error"
        assert parse_retry_delay_from_error(RuntimeError(msg3), default_delay=120.0) == 120.0

    def test_execute_with_failover_rotates_on_429(self) -> None:
        calls: list[str] = []

        def mock_client_factory(k: str) -> MagicMock:
            client = MagicMock()
            client.name = k
            return client

        pool = GeminiCredentialPool(
            keys=["key-primary", "key-secondary"],
            client_factory=mock_client_factory,
        )

        def operation(client: Any) -> str:
            calls.append(client.name)
            if client.name == "key-primary":
                raise RuntimeError("ResourceExhausted: 429 Quota exceeded. Please retry in 60s.")
            return "success-from-secondary"

        result = pool.execute_with_failover(operation)
        assert result == "success-from-secondary"
        assert calls == ["key-primary", "key-secondary"]
        # Primary should now be in cooldown
        assert pool.lease()[0] == "key-secondary"

    def test_execute_with_failover_does_not_rotate_on_503(self) -> None:
        calls: list[str] = []

        pool = GeminiCredentialPool(
            keys=["key-primary", "key-secondary"],
            client_factory=lambda k: MagicMock(name=f"Client-{k}"),
        )

        def operation(client: Any) -> str:
            calls.append(client._extract_mock_name())
            raise RuntimeError("503 Service Unavailable: High Demand")

        with pytest.raises(RuntimeError, match="503 Service Unavailable"):
            pool.execute_with_failover(operation)

        assert len(calls) == 1
        # Primary should NOT be in cooldown
        assert pool.lease()[0] == "key-primary"

    def test_gemini_judge_rotates_on_429(self) -> None:
        import json

        from cresmo.domain.value_objects import EvaluationContext, JudgeCriterion
        from cresmo.infrastructure.adapters.judges.gemini_judge import GeminiJudgeAdapter

        client1 = MagicMock(name="client-1")
        client2 = MagicMock(name="client-2")
        client1.models.generate_content.side_effect = RuntimeError(
            "ResourceExhausted: 429 Quota limit reached. Please retry in 180s."
        )
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({
            "criteria": [{"criterion": "orality_removal", "score": 0.95, "passed": True}],
            "overall_score": 0.95,
            "passed": True,
        })
        client2.models.generate_content.return_value = mock_resp

        clients = {"k1": client1, "k2": client2}
        pool = GeminiCredentialPool(keys=["k1", "k2"], client_factory=lambda k: clients[k])

        judge = GeminiJudgeAdapter(credential_pool=pool)
        context = EvaluationContext(
            stage_name="fluid_prose",
            raw_text="raw sample",
            candidate_text="cand sample",
            required_criteria=(JudgeCriterion.ORALITY_REMOVAL,),
        )
        eval_result = judge.evaluate(context)

        assert eval_result.passed is True
        assert client1.models.generate_content.call_count == 1
        assert client2.models.generate_content.call_count == 1
        assert pool.lease()[0] == "k2"


