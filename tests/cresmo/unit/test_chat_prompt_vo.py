"""Unit tests for ChatMessage, MessageRole, and ChatPrompt value objects.

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
)


class TestChatMessageValueObject:
    """Test suite verifying ChatMessage invariants."""

    def test_valid_chat_message_creation(self) -> None:
        msg = ChatMessage(role=MessageRole.USER, content="Hello model")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello model"

    def test_empty_content_raises_domain_validation_error(self) -> None:
        with pytest.raises(DomainValidationError, match="content cannot be empty"):
            ChatMessage(role=MessageRole.USER, content="   ")

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

    def test_with_turn_returns_new_immutable_instance(self) -> None:
        base = ChatPrompt.single_turn("Initial prompt")
        turn2 = base.with_turn(MessageRole.ASSISTANT, "Generated text")
        turn3 = turn2.with_turn(MessageRole.USER, "Critique: fix parataxis")

        assert len(base.messages) == 1
        assert len(turn2.messages) == 2
        assert len(turn3.messages) == 3
        assert turn3.get_last_user_content() == "Critique: fix parataxis"

    def test_empty_prompt_raises_validation_error(self) -> None:
        with pytest.raises(
            DomainValidationError,
            match="ChatPrompt must have at least one message or system_instruction",
        ):
            ChatPrompt(messages=(), system_instruction=None)
