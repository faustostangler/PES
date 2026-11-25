"""Unit tests for ChatMessage, MessageRole, PromptKey, and ChatPrompt value objects.

Conforms to:
    - ADR-036: Multi-Turn and Few-Shot ChatPrompt Domain Architecture
    - Spec: SOTA-KISS Fail-Fast Immutable Value Objects
"""

from __future__ import annotations

import pytest

from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects.prompt import (
    ChatMessage,
    ChatPrompt,
    MessageRole,
    PromptKey,
)


class TestPromptKeyAndMessageRole:
    """Test suite verifying PromptKey and MessageRole enumerations."""

    def test_prompt_key_values(self) -> None:
        expected = {
            PromptKey.FLUID_PROSE: "fluid_prose",
            PromptKey.GAP_FILLER: "gap_filler",
            PromptKey.LONG_EXPANDER: "long_expander",
            PromptKey.WIDE_EXPANDER: "wide_expander",
            PromptKey.ATOMIC_INVENTORY: "atomic_inventory",
            PromptKey.JUDGE_ATOMIC_INVENTORY: "judge_atomic_inventory",
            PromptKey.ATOMIC_BATCH: "atomic_batch",
            PromptKey.RECONCILE_MOCS: "reconcile_mocs",
            PromptKey.RAW_INDEX_SUMMARY: "raw_index_summary",
            PromptKey.RAW_INDEX_CONCEPTS: "raw_index_concepts",
            PromptKey.RAW_INDEX_CONCEPTS_REWRITE: "raw_index_concepts_rewrite",
            PromptKey.RAW_INDEX_SYNTHESIS: "raw_index_synthesis",
            PromptKey.JUDGE_RAW_INDEX_SUMMARY: "judge_raw_index_summary",
            PromptKey.JUDGE_RAW_INDEX_CONCEPTS: "judge_raw_index_concepts",
            PromptKey.JUDGE_RAW_INDEX_SYNTHESIS: "judge_raw_index_synthesis",
            PromptKey.JUDGE_FLUID_PROSE: "judge_fluid_prose",
            PromptKey.JUDGE_GAP_FILLER: "judge_gap_filler",
            PromptKey.OLLAMA_CRITIQUE: "ollama_critique",
        }
        for key, val in expected.items():
            assert key.value == val
        assert not hasattr(PromptKey, "GAP_FILLER_REFINE")

    def test_message_role_values(self) -> None:
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"


class TestChatMessageValueObject:
    """Test suite verifying ChatMessage invariants."""

    def test_valid_chat_message_creation(self) -> None:
        msg = ChatMessage(role=MessageRole.USER, content="Hello model")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello model"

    @pytest.mark.parametrize("empty_content", ["", "   ", "\t\n"])
    def test_empty_content_raises_domain_validation_error(self, empty_content: str) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^ChatMessage content cannot be empty\.$",
        ):
            ChatMessage(role=MessageRole.USER, content=empty_content)

    def test_non_string_content_raises_domain_validation_error(self) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^ChatMessage content cannot be empty\.$",
        ):
            ChatMessage(role=MessageRole.USER, content=123)  # type: ignore[arg-type]

    def test_message_is_immutable(self) -> None:
        msg = ChatMessage(role=MessageRole.ASSISTANT, content="I am here")
        with pytest.raises(AttributeError):
            msg.content = "Changed"  # type: ignore[misc]


class TestChatPromptValueObject:
    """Test suite verifying ChatPrompt invariants and capabilities."""

    def test_single_turn_factory(self) -> None:
        prompt = ChatPrompt.single_turn(
            user_prompt="Summarize this text",
            system_prompt="You are a senior analyst",
        )
        assert prompt.system_prompt == "You are a senior analyst"
        assert len(prompt.messages) == 1
        assert prompt.messages[0].role == MessageRole.USER
        assert prompt.messages[0].content == "Summarize this text"

    def test_multi_turn_with_few_shots(self) -> None:
        prompt = ChatPrompt(
            system_prompt="Strict style guide",
            messages=(
                ChatMessage(role=MessageRole.USER, content="Raw 1"),
                ChatMessage(role=MessageRole.ASSISTANT, content="Clean 1"),
                ChatMessage(role=MessageRole.USER, content="Raw 2"),
            ),
        )
        assert len(prompt.messages) == 3
        assert prompt.messages[-1].content == "Raw 2"

    def test_system_prompt_only_is_valid(self) -> None:
        prompt = ChatPrompt(messages=(), system_prompt="System only instruction")
        assert prompt.system_prompt == "System only instruction"
        assert prompt.messages == ()

    @pytest.mark.parametrize("invalid_sys", [None, "", "   ", "\t"])
    def test_empty_messages_and_empty_system_raises_validation_error(
        self, invalid_sys: str | None
    ) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^ChatPrompt must have at least one message or system_prompt\.$",
        ):
            ChatPrompt(messages=(), system_prompt=invalid_sys)

    def test_to_dict_list_with_system_prompt_and_messages(self) -> None:
        prompt = ChatPrompt(
            system_prompt="Act as editor",
            messages=(
                ChatMessage(role=MessageRole.USER, content="Text to edit"),
                ChatMessage(role=MessageRole.ASSISTANT, content="Edited text"),
            ),
        )
        dict_list = prompt.to_dict_list()
        assert dict_list == [
            {"role": "system", "content": "Act as editor"},
            {"role": "user", "content": "Text to edit"},
            {"role": "assistant", "content": "Edited text"},
        ]

    def test_to_dict_list_without_system_prompt(self) -> None:
        prompt = ChatPrompt(
            messages=(ChatMessage(role=MessageRole.USER, content="Hello"),),
            system_prompt=None,
        )
        dict_list = prompt.to_dict_list()
        assert dict_list == [
            {"role": "user", "content": "Hello"},
        ]
