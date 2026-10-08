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
            PromptKey.GAP_FILLER_PASS1: "gap_filler_pass1",
            PromptKey.GAP_FILLER_PASS_SUBSEQUENT: "gap_filler_pass_subsequent",
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
            PromptKey.LLM_JUDGE: "llm_judge",
            PromptKey.OLLAMA_CRITIQUE: "ollama_critique",
        }
        for key, val in expected.items():
            assert key.value == val

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
            system_instruction="You are a senior analyst",
        )
        assert prompt.system_instruction == "You are a senior analyst"
        assert len(prompt.messages) == 1
        assert prompt.messages[0].role == MessageRole.USER
        assert prompt.messages[0].content == "Summarize this text"
        assert prompt.get_last_user_content() == "Summarize this text"

    def test_from_system_and_user_factory(self) -> None:
        prompt = ChatPrompt.from_system_and_user(
            user="Analyze this data",
            system="System persona",
        )
        assert prompt.system_instruction == "System persona"
        assert len(prompt.messages) == 1
        assert prompt.messages[0].role == MessageRole.USER
        assert prompt.messages[0].content == "Analyze this data"
        assert prompt.get_last_user_content() == "Analyze this data"

    def test_multi_turn_with_few_shots(self) -> None:
        prompt = ChatPrompt(
            system_instruction="Strict style guide",
            messages=(
                ChatMessage(role=MessageRole.USER, content="Raw 1"),
                ChatMessage(role=MessageRole.ASSISTANT, content="Clean 1"),
                ChatMessage(role=MessageRole.USER, content="Raw 2"),
            ),
        )
        assert len(prompt.messages) == 3
        assert prompt.get_last_user_content() == "Raw 2"

    def test_with_turn_returns_new_immutable_instance_and_preserves_system_instruction(self) -> None:
        base = ChatPrompt.single_turn(
            user_prompt="Initial prompt",
            system_instruction="System context instructions",
        )
        turn2 = base.with_turn(MessageRole.ASSISTANT, "Generated text")
        turn3 = turn2.with_turn(MessageRole.USER, "Critique: fix parataxis")

        assert len(base.messages) == 1
        assert base.system_instruction == "System context instructions"

        assert len(turn2.messages) == 2
        assert turn2.system_instruction == "System context instructions"
        assert turn2.messages[1].role == MessageRole.ASSISTANT
        assert turn2.messages[1].content == "Generated text"

        assert len(turn3.messages) == 3
        assert turn3.system_instruction == "System context instructions"
        assert turn3.get_last_user_content() == "Critique: fix parataxis"

    def test_get_last_user_content_when_no_user_message(self) -> None:
        prompt = ChatPrompt(
            system_instruction="System prompt",
            messages=(ChatMessage(role=MessageRole.ASSISTANT, content="Hi"),),
        )
        assert prompt.get_last_user_content() == ""

    def test_system_instruction_only_is_valid(self) -> None:
        prompt = ChatPrompt(messages=(), system_instruction="System only instruction")
        assert prompt.system_instruction == "System only instruction"
        assert prompt.messages == ()
        assert prompt.get_last_user_content() == ""

    @pytest.mark.parametrize("invalid_sys", [None, "", "   ", "\t"])
    def test_empty_messages_and_empty_system_raises_validation_error(self, invalid_sys: str | None) -> None:
        with pytest.raises(
            DomainValidationError,
            match=r"^ChatPrompt must have at least one message or system_instruction\.$",
        ):
            ChatPrompt(messages=(), system_instruction=invalid_sys)

    def test_to_dict_list_with_system_instruction_and_messages(self) -> None:
        prompt = ChatPrompt(
            system_instruction="Act as editor",
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

    def test_to_dict_list_without_system_instruction(self) -> None:
        prompt = ChatPrompt(
            messages=(
                ChatMessage(role=MessageRole.USER, content="Hello"),
            ),
            system_instruction=None,
        )
        dict_list = prompt.to_dict_list()
        assert dict_list == [
            {"role": "user", "content": "Hello"},
        ]
