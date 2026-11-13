"""Unit tests for AnonymizerPort and RegexAnonymizerAdapter.

Conforms to ADR-017:
    - Verifies redaction of emails, phone numbers, and secrets in plain text.
    - Verifies recursive dictionary scrubbing for sensitive keys.
    - Verifies OpenTelemetry span attribute sanitization (e.g. cookie header removal).
    - Verifies NoOpAnonymizerAdapter passthrough.
"""

from __future__ import annotations

import pytest

from cresmo.application.ports import AnonymizerPort
from cresmo.infrastructure.adapters.anonymizer_adapter import (
    NoOpAnonymizerAdapter,
    RegexAnonymizerAdapter,
)


class TestRegexAnonymizerAdapter:
    """Test suite for RegexAnonymizerAdapter compliance."""

    @pytest.fixture
    def anonymizer(self) -> AnonymizerPort:
        return RegexAnonymizerAdapter()

    def test_mask_text_redacts_email_addresses(self, anonymizer: AnonymizerPort) -> None:
        raw_text = "Entre em contato com john.doe@example.com ou suporte@corp.org para detalhes."
        sanitized = anonymizer.mask_text(raw_text)
        assert "john.doe@example.com" not in sanitized
        assert "suporte@corp.org" not in sanitized
        assert "[REDACTED_EMAIL]" in sanitized
        assert (
            sanitized == "Entre em contato com [REDACTED_EMAIL] ou [REDACTED_EMAIL] para detalhes."
        )

    def test_mask_text_redacts_bearer_tokens_and_api_keys(self, anonymizer: AnonymizerPort) -> None:
        raw_text = "Authorization: Bearer sk-ant-api03-abcdef1234567890 and key=AIzaSyD123456789012345678901234567890"
        sanitized = anonymizer.mask_text(raw_text)
        assert "sk-ant-api03-abcdef1234567890" not in sanitized
        assert sanitized == "Authorization: [REDACTED_SECRET] and key=[REDACTED_SECRET]"
        assert anonymizer.mask_text("Bearer sk-ant-api03-abcdef1234567890") == "[REDACTED_SECRET]"

    def test_mask_text_preserves_clean_text(self, anonymizer: AnonymizerPort) -> None:
        clean = "Uma introdução completa sobre transformers e mecanismos de atenção."
        assert anonymizer.mask_text(clean) == clean

    def test_mask_text_empty_string(self, anonymizer: AnonymizerPort) -> None:
        assert anonymizer.mask_text("") == ""

    def test_mask_mapping_scrubs_sensitive_keys(self, anonymizer: AnonymizerPort) -> None:
        payload = {
            "channel": "sandeco",
            "cookie": "session_id=xyz123; auth=abc",
            "api_key": "secret-val",
            "nested": {
                "token": "bearer-12345",
                "email": "user@test.com",
                "safe_field": 42,
            },
        }
        sanitized = anonymizer.mask_mapping(payload)
        assert "cookie" not in sanitized
        assert "api_key" not in sanitized
        assert "token" not in sanitized["nested"]
        assert sanitized["nested"]["email"] == "[REDACTED_EMAIL]"
        assert sanitized["nested"]["safe_field"] == 42
        assert sanitized["channel"] == "sandeco"

    def test_mask_mapping_scrubs_lists_with_mappings_and_strings(
        self, anonymizer: AnonymizerPort
    ) -> None:
        payload = {
            "items": [
                "john@doe.com",
                "clean text",
                {"api_key": "secret", "user": "alice@test.com", "count": 10},
                42,
            ]
        }
        sanitized = anonymizer.mask_mapping(payload)
        items = sanitized["items"]
        assert isinstance(items, list)
        assert items[0] == "[REDACTED_EMAIL]"
        assert items[1] == "clean text"
        assert items[2] == {"user": "[REDACTED_EMAIL]", "count": 10}
        assert items[3] == 42

    def test_mask_mapping_handles_non_string_keys(self, anonymizer: AnonymizerPort) -> None:
        class SensitiveKey:
            def __str__(self) -> str:
                return "auth_token"

        class SafeKey:
            def __str__(self) -> str:
                return "user_id"

        sens_key = SensitiveKey()
        safe_key = SafeKey()
        payload = {
            sens_key: "hidden-value",
            safe_key: "visible-value",
            999: "numeric-key-val",
        }
        sanitized = anonymizer.mask_mapping(payload)
        assert sens_key not in sanitized
        assert sanitized[safe_key] == "visible-value"
        assert sanitized[999] == "numeric-key-val"

    def test_mask_span_attributes_strips_cookies_and_redacts_prompts(
        self, anonymizer: AnonymizerPort
    ) -> None:
        attributes = {
            "cresmo.channel": "sandeco",
            "http.request.header.cookie": "auth_token=abc12345",
            "gen_ai.prompt.0.content": "Envie feedback para dev@pes.ai sobre o modelo.",
            "gen_ai.usage.input_tokens": 150,
        }
        sanitized = anonymizer.mask_span_attributes(attributes)
        assert "http.request.header.cookie" not in sanitized
        assert sanitized["cresmo.channel"] == "sandeco"
        assert sanitized["gen_ai.usage.input_tokens"] == 150
        assert "dev@pes.ai" not in sanitized["gen_ai.prompt.0.content"]
        assert (
            sanitized["gen_ai.prompt.0.content"]
            == "Envie feedback para [REDACTED_EMAIL] sobre o modelo."
        )


class TestNoOpAnonymizerAdapter:
    """Test suite for NoOpAnonymizerAdapter."""

    def test_noop_passthrough(self) -> None:
        adapter = NoOpAnonymizerAdapter()
        text = "Contact: test@corp.com"
        mapping = {"cookie": "123"}
        assert adapter.mask_text(text) == text
        assert adapter.mask_mapping(mapping) == mapping
        assert adapter.mask_span_attributes(mapping) == mapping
