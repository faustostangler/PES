"""Prompt Value Objects for template identification, multi-turn messages, and few-shot formatting across Cresmo.

Conforms to:
    - ADR-036: Multi-Turn and Few-Shot ChatPrompt Domain Architecture
    - Spec: SOTA-KISS Fail-Fast Immutable Value Objects
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cresmo.domain.exceptions import DomainValidationError


class PromptKey(StrEnum):
    """Canonical enumeration of all prompt template identifiers across Cresmo."""

    FLUID_PROSE = "fluid_prose"
    GAP_FILLER_PASS1 = "gap_filler_pass1"
    GAP_FILLER_PASS_SUBSEQUENT = "gap_filler_pass_subsequent"
    LONG_EXPANDER = "long_expander"
    WIDE_EXPANDER = "wide_expander"
    ATOMIC_INVENTORY = "atomic_inventory"
    JUDGE_ATOMIC_INVENTORY = "judge_atomic_inventory"
    ATOMIC_BATCH = "atomic_batch"
    RECONCILE_MOCS = "reconcile_mocs"
    RAW_INDEX_SUMMARY = "raw_index_summary"
    RAW_INDEX_CONCEPTS = "raw_index_concepts"
    RAW_INDEX_CONCEPTS_REWRITE = "raw_index_concepts_rewrite"
    RAW_INDEX_SYNTHESIS = "raw_index_synthesis"
    JUDGE_RAW_INDEX_SUMMARY = "judge_raw_index_summary"
    JUDGE_RAW_INDEX_CONCEPTS = "judge_raw_index_concepts"
    JUDGE_RAW_INDEX_SYNTHESIS = "judge_raw_index_synthesis"
    LLM_JUDGE = "llm_judge"
    OLLAMA_CRITIQUE = "ollama_critique"


class MessageRole(StrEnum):
    """Semantic role of a message turn in conversation with an LLM."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class ChatMessage:
    """Immutable single message turn with fail-fast domain invariants."""

    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.content, str) or not self.content.strip():
            raise DomainValidationError("ChatMessage content cannot be empty.")


@dataclass(frozen=True)
class ChatPrompt:
    """Canonical multi-turn and few-shot prompt domain value object.

    Shields application and domain layers from vendor-specific message structures,
    unifying persona/system constraints, sequential few-shot examples, and dynamic
    turn interactions across all LLM inference engines.
    """

    messages: tuple[ChatMessage, ...]
    system_instruction: str | None = None

    def __post_init__(self) -> None:
        if not self.messages and (not self.system_instruction or not self.system_instruction.strip()):
            raise DomainValidationError(
                "ChatPrompt must have at least one message or system_instruction."
            )

    @classmethod
    def single_turn(
        cls,
        user_prompt: str,
        system_instruction: str | None = None,
    ) -> ChatPrompt:
        """Convenience factory creating a single-turn user prompt."""
        return cls(
            system_instruction=system_instruction,
            messages=(ChatMessage(role=MessageRole.USER, content=user_prompt),),
        )

    @classmethod
    def from_system_and_user(
        cls,
        user: str,
        system: str | None = None,
    ) -> ChatPrompt:
        """Convenience factory creating a ChatPrompt from user content and optional system instruction."""
        return cls.single_turn(user_prompt=user, system_instruction=system)

    def with_turn(self, role: MessageRole, content: str) -> ChatPrompt:
        """Return a new immutable ChatPrompt with an appended message turn."""
        return ChatPrompt(
            system_instruction=self.system_instruction,
            messages=(*self.messages, ChatMessage(role=role, content=content)),
        )

    def get_last_user_content(self) -> str:
        """Extract content of the last user message, or empty string if absent."""
        for msg in reversed(self.messages):
            if msg.role == MessageRole.USER:
                return msg.content
        return ""

    def to_dict_list(self) -> list[dict[str, str]]:
        """Serialize messages into standardized dictionary representation."""
        result: list[dict[str, str]] = []
        if self.system_instruction:
            result.append({"role": MessageRole.SYSTEM.value, "content": self.system_instruction})
        for msg in self.messages:
            result.append({"role": msg.role.value, "content": msg.content})
        return result

