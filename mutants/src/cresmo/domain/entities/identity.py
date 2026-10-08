"""Identity, Session, Tenant, and Telemetry Value Objects and Entities.

Conforms to:
- ADR-016: Cost-Center Observability and Channel Multi-Tenancy
- ADR-027: User & Worker Unified Identity Modalities
- ADR-013: LLM Judge Friction Metrics
"""

from __future__ import annotations

from dataclasses import dataclass

from cresmo.domain.value_objects import (
    Channel,
    ChannelId,
    ChannelName,
    Content,
    ContentId,
)

CANONICAL_SESSION_ID_PARTS: int = 2
LEGACY_SESSION_ID_PARTS: int = 3
PIPELINE_SESSION_ID_PART_COUNT: int = LEGACY_SESSION_ID_PARTS


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁPipelineSessionIdǁ__post_init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁPipelineSessionIdǁcreate__mutmut: MutantDict = {}  # type: ignore


@dataclass(frozen=True)
class PipelineSessionId:
    """Value Object representing the holistic multi-stage content lifecycle session.

    Conforms to ADR-016, ADR-027, and ADR-033.
    Ensures end-to-end Session Replay in Langfuse for exactly one content item.
    Canonical format: {channel_id}:{content_id}
    """

    value: str

    @_mutmut_mutated(mutants_xǁPipelineSessionIdǁ__post_init____mutmut)
    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_orig(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_1(self) -> None:
        if not self.value and not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_2(self) -> None:
        if self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_3(self) -> None:
        if not self.value or self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_4(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError(None)
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_5(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("XXPipelineSessionId cannot be empty.XX")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_6(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("pipelinesessionid cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_7(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PIPELINESESSIONID CANNOT BE EMPTY.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_8(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = None
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_9(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(None)
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_10(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split("XX:XX")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_11(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) != CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_12(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() and not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_13(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_14(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[1].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_15(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_16(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_17(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    None
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_18(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "XXExpected '{channel_id}:{content_id}'.XX"
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_19(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_20(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "EXPECTED '{CHANNEL_ID}:{CONTENT_ID}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_21(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS or parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_22(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) != LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_23(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[1] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_24(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] != "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_25(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "XXcontentXX":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_26(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "CONTENT":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_27(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() and not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_28(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_29(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[2].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_30(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_31(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[3].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_32(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    None
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_33(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "XXExpected 'content:{channel}:{content_id}'.XX"
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_34(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_35(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "EXPECTED 'CONTENT:{CHANNEL}:{CONTENT_ID}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "Expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_36(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                None
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_37(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "XXExpected '{channel_id}:{content_id}'.XX"
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_38(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "expected '{channel_id}:{content_id}'."
            )

    def xǁPipelineSessionIdǁ__post_init____mutmut_39(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PipelineSessionId cannot be empty.")
        parts = self.value.split(":")
        if len(parts) == CANONICAL_SESSION_ID_PARTS:
            if not parts[0].strip() or not parts[1].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected '{channel_id}:{content_id}'."
                )
        elif len(parts) == LEGACY_SESSION_ID_PARTS and parts[0] == "content":
            if not parts[1].strip() or not parts[2].strip():
                raise ValueError(
                    f"Invalid PipelineSessionId format: '{self.value}'. "
                    "Expected 'content:{channel}:{content_id}'."
                )
        else:
            raise ValueError(
                f"Invalid PipelineSessionId format: '{self.value}'. "
                "EXPECTED '{CHANNEL_ID}:{CONTENT_ID}'."
            )

    @classmethod
    @_mutmut_mutated(mutants_xǁPipelineSessionIdǁcreate__mutmut, is_classmethod = True)
    def create(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @classmethod
    def xǁPipelineSessionIdǁcreate__mutmut_orig(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @classmethod
    def xǁPipelineSessionIdǁcreate__mutmut_1(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = None
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @classmethod
    def xǁPipelineSessionIdǁcreate__mutmut_2(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id and channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @classmethod
    def xǁPipelineSessionIdǁcreate__mutmut_3(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = None
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @classmethod
    def xǁPipelineSessionIdǁcreate__mutmut_4(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = None

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @classmethod
    def xǁPipelineSessionIdǁcreate__mutmut_5(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = None
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @classmethod
    def xǁPipelineSessionIdǁcreate__mutmut_6(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = None

        return cls(value=f"{channel_identifier}:{content_identifier}")

    @classmethod
    def xǁPipelineSessionIdǁcreate__mutmut_7(
        cls,
        channel: Channel | ChannelName | str,
        content_id: Content | ContentId | str,
        channel_id: ChannelId | None = None,
    ) -> PipelineSessionId:
        """Construct canonical session key preferring stable ChannelId over mutable Channel.name.

        Args:
            channel: Composite Channel VO, human-readable ChannelName, or str.
            content_id: Composite Content VO, ContentId, or str.
            channel_id: Optional stable platform ID (preferred for algorithmic keys).
        """
        # Algorithmic key: prefer stable ID over mutable name
        if isinstance(channel, Channel):
            resolved_channel_id = channel.id or channel_id
            channel_identifier = resolved_channel_id.value if resolved_channel_id else channel.name
        else:
            channel_identifier = (
                channel_id.value
                if channel_id
                else (channel.value if isinstance(channel, ChannelName) else channel.strip())
            )

        if isinstance(content_id, Content):
            content_identifier = content_id.id.value
        else:
            content_identifier = (
                content_id.value if isinstance(content_id, ContentId) else content_id.strip()
            )

        return cls(value=None)

    @property
    def channel_id(self) -> str:
        """Algorithmic channel identifier token stored in the session key (ID or name)."""
        parts = self.value.split(":")
        return (
            parts[1]
            if parts[0] == "content" and len(parts) == LEGACY_SESSION_ID_PARTS
            else parts[0]
        )

    @property
    def content_id(self) -> str:
        """Content identifier stored in the session key."""
        parts = self.value.split(":")
        return (
            parts[2]
            if parts[0] == "content" and len(parts) == LEGACY_SESSION_ID_PARTS
            else parts[1]
        )

mutants_xǁPipelineSessionIdǁ__post_init____mutmut['_mutmut_orig'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_1'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_2'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_3'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_4'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_5'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_6'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_7'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_8'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_9'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_10'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_11'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_12'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_13'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_14'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_15'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_16'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_17'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_18'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_18 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_19'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_19 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_20'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_20 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_21'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_21 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_22'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_22 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_23'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_23 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_24'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_24 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_25'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_25 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_26'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_26 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_27'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_27 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_28'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_28 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_29'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_29 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_30'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_30 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_31'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_31 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_32'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_32 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_33'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_33 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_34'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_34 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_35'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_35 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_36'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_36 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_37'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_37 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_38'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_38 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁ__post_init____mutmut['xǁPipelineSessionIdǁ__post_init____mutmut_39'] = PipelineSessionId.xǁPipelineSessionIdǁ__post_init____mutmut_39 # type: ignore # mutmut generated

mutants_xǁPipelineSessionIdǁcreate__mutmut['_mutmut_orig'] = PipelineSessionId.xǁPipelineSessionIdǁcreate__mutmut_orig # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁcreate__mutmut['xǁPipelineSessionIdǁcreate__mutmut_1'] = PipelineSessionId.xǁPipelineSessionIdǁcreate__mutmut_1 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁcreate__mutmut['xǁPipelineSessionIdǁcreate__mutmut_2'] = PipelineSessionId.xǁPipelineSessionIdǁcreate__mutmut_2 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁcreate__mutmut['xǁPipelineSessionIdǁcreate__mutmut_3'] = PipelineSessionId.xǁPipelineSessionIdǁcreate__mutmut_3 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁcreate__mutmut['xǁPipelineSessionIdǁcreate__mutmut_4'] = PipelineSessionId.xǁPipelineSessionIdǁcreate__mutmut_4 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁcreate__mutmut['xǁPipelineSessionIdǁcreate__mutmut_5'] = PipelineSessionId.xǁPipelineSessionIdǁcreate__mutmut_5 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁcreate__mutmut['xǁPipelineSessionIdǁcreate__mutmut_6'] = PipelineSessionId.xǁPipelineSessionIdǁcreate__mutmut_6 # type: ignore # mutmut generated
mutants_xǁPipelineSessionIdǁcreate__mutmut['xǁPipelineSessionIdǁcreate__mutmut_7'] = PipelineSessionId.xǁPipelineSessionIdǁcreate__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁ__post_init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁUserIdentityǁanonymous__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUserIdentityǁidentified__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUserIdentityǁworker__mutmut: MutantDict = {}  # type: ignore
mutants_xǁUserIdentityǁfrom_channel__mutmut: MutantDict = {}  # type: ignore


@dataclass(frozen=True)
class UserIdentity:
    """Value Object representing the user/operator executing the synthesis pipeline.

    Supports forward-compatible identity modalities per ADR-027:
    - Anonymous (unauthenticated, guest, CLI): 'anonymous'
    - Identified (authenticated via IAM / OAuth): 'user:iam:alice' or 'user:oauth:subject'
    - Scheduled workers (daemons, batch sync): 'system:worker'
    - Channel fallback (legacy background worker pipelines): 'channel:...'
    """

    value: str
    is_anonymous: bool = True
    provider: str = "anonymous"
    subject: str = ""

    @_mutmut_mutated(mutants_xǁUserIdentityǁ__post_init____mutmut)
    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("UserIdentity cannot be empty.")

    def xǁUserIdentityǁ__post_init____mutmut_orig(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("UserIdentity cannot be empty.")

    def xǁUserIdentityǁ__post_init____mutmut_1(self) -> None:
        if not self.value and not self.value.strip():
            raise ValueError("UserIdentity cannot be empty.")

    def xǁUserIdentityǁ__post_init____mutmut_2(self) -> None:
        if self.value or not self.value.strip():
            raise ValueError("UserIdentity cannot be empty.")

    def xǁUserIdentityǁ__post_init____mutmut_3(self) -> None:
        if not self.value or self.value.strip():
            raise ValueError("UserIdentity cannot be empty.")

    def xǁUserIdentityǁ__post_init____mutmut_4(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError(None)

    def xǁUserIdentityǁ__post_init____mutmut_5(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("XXUserIdentity cannot be empty.XX")

    def xǁUserIdentityǁ__post_init____mutmut_6(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("useridentity cannot be empty.")

    def xǁUserIdentityǁ__post_init____mutmut_7(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("USERIDENTITY CANNOT BE EMPTY.")

    @classmethod
    @_mutmut_mutated(mutants_xǁUserIdentityǁanonymous__mutmut, is_classmethod = True)
    def anonymous(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_orig(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_1(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = None
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_2(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "XXanonymousXX"
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_3(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "ANONYMOUS"
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_4(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=None, is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_5(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=None, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_6(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider=None, subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_7(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", subject=None)

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_8(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(is_anonymous=True, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_9(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_10(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_11(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", )

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_12(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=False, provider="anonymous", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_13(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider="XXanonymousXX", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_14(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider="ANONYMOUS", subject="")

    @classmethod
    def xǁUserIdentityǁanonymous__mutmut_15(cls, token: str | None = None) -> UserIdentity:
        """Create an anonymous user identity."""
        identity_value = f"anon:{token}" if token else "anonymous"
        return cls(value=identity_value, is_anonymous=True, provider="anonymous", subject="XXXX")

    @classmethod
    @_mutmut_mutated(mutants_xǁUserIdentityǁidentified__mutmut, is_classmethod = True)
    def identified(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_orig(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_1(cls, subject: str, provider: str = "XXoauthXX") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_2(cls, subject: str, provider: str = "OAUTH") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_3(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject and not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_4(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_5(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_6(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError(None)
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_7(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("XXIdentified UserIdentity requires a non-empty subject.XX")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_8(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("identified useridentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_9(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("IDENTIFIED USERIDENTITY REQUIRES A NON-EMPTY SUBJECT.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_10(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = None
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_11(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() and "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_12(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().upper() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_13(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "XXoauthXX"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_14(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "OAUTH"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_15(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = None
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_16(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=None,
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_17(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=None,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_18(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=None,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_19(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            subject=None,
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_20(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            is_anonymous=False,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_21(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_22(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            subject=subject.strip(),
        )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_23(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=False,
            provider=resolved_provider,
            )

    @classmethod
    def xǁUserIdentityǁidentified__mutmut_24(cls, subject: str, provider: str = "oauth") -> UserIdentity:
        """Create an identified user identity from OAuth subject, IAM username, or email."""
        if not subject or not subject.strip():
            raise ValueError("Identified UserIdentity requires a non-empty subject.")
        resolved_provider = provider.strip().lower() or "oauth"
        identity_value = f"user:{resolved_provider}:{subject.strip()}"
        return cls(
            value=identity_value,
            is_anonymous=True,
            provider=resolved_provider,
            subject=subject.strip(),
        )

    @classmethod
    @_mutmut_mutated(mutants_xǁUserIdentityǁworker__mutmut, is_classmethod = True)
    def worker(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_orig(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_1(cls, name: str = "XXworkerXX") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_2(cls, name: str = "WORKER") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_3(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = None
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_4(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() and "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_5(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "XXworkerXX"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_6(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "WORKER"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_7(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=None,
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_8(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=None,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_9(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider=None,
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_10(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            subject=None,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_11(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            is_anonymous=False,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_12(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_13(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_14(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="system",
            )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_15(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=True,
            provider="system",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_16(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="XXsystemXX",
            subject=clean_name,
        )

    @classmethod
    def xǁUserIdentityǁworker__mutmut_17(cls, name: str = "worker") -> UserIdentity:
        """Create a scheduled or background worker user identity per ADR-027."""
        clean_name = name.strip() or "worker"
        return cls(
            value=f"system:{clean_name}",
            is_anonymous=False,
            provider="SYSTEM",
            subject=clean_name,
        )

    @classmethod
    @_mutmut_mutated(mutants_xǁUserIdentityǁfrom_channel__mutmut, is_classmethod = True)
    def from_channel(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_orig(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_1(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel and not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_2(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_3(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_4(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError(None)
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_5(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("XXChannel name cannot be empty.XX")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_6(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_7(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("CHANNEL NAME CANNOT BE EMPTY.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_8(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = None
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_9(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=None,
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_10(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=None,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_11(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider=None,
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_12(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            subject=None,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_13(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            is_anonymous=True,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_14(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_15(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_16(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="channel",
            )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_17(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=False,
            provider="channel",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_18(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="XXchannelXX",
            subject=clean_channel,
        )

    @classmethod
    def xǁUserIdentityǁfrom_channel__mutmut_19(cls, channel: str) -> UserIdentity:
        """Create a channel-bound fallback user identity for backward compatibility."""
        if not channel or not channel.strip():
            raise ValueError("Channel name cannot be empty.")
        clean_channel = channel.strip()
        return cls(
            value=f"channel:{clean_channel}",
            is_anonymous=True,
            provider="CHANNEL",
            subject=clean_channel,
        )

mutants_xǁUserIdentityǁ__post_init____mutmut['_mutmut_orig'] = UserIdentity.xǁUserIdentityǁ__post_init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁUserIdentityǁ__post_init____mutmut['xǁUserIdentityǁ__post_init____mutmut_1'] = UserIdentity.xǁUserIdentityǁ__post_init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁ__post_init____mutmut['xǁUserIdentityǁ__post_init____mutmut_2'] = UserIdentity.xǁUserIdentityǁ__post_init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁ__post_init____mutmut['xǁUserIdentityǁ__post_init____mutmut_3'] = UserIdentity.xǁUserIdentityǁ__post_init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁ__post_init____mutmut['xǁUserIdentityǁ__post_init____mutmut_4'] = UserIdentity.xǁUserIdentityǁ__post_init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁ__post_init____mutmut['xǁUserIdentityǁ__post_init____mutmut_5'] = UserIdentity.xǁUserIdentityǁ__post_init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁ__post_init____mutmut['xǁUserIdentityǁ__post_init____mutmut_6'] = UserIdentity.xǁUserIdentityǁ__post_init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁ__post_init____mutmut['xǁUserIdentityǁ__post_init____mutmut_7'] = UserIdentity.xǁUserIdentityǁ__post_init____mutmut_7 # type: ignore # mutmut generated

mutants_xǁUserIdentityǁanonymous__mutmut['_mutmut_orig'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_1'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_2'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_3'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_4'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_5'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_6'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_7'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_8'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_9'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_10'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_11'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_12'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_13'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_14'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁanonymous__mutmut['xǁUserIdentityǁanonymous__mutmut_15'] = UserIdentity.xǁUserIdentityǁanonymous__mutmut_15 # type: ignore # mutmut generated

mutants_xǁUserIdentityǁidentified__mutmut['_mutmut_orig'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_1'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_2'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_3'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_4'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_5'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_6'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_7'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_8'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_9'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_10'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_11'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_12'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_13'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_14'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_15'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_16'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_17'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_18'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_19'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_19 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_20'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_20 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_21'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_21 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_22'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_22 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_23'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_23 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁidentified__mutmut['xǁUserIdentityǁidentified__mutmut_24'] = UserIdentity.xǁUserIdentityǁidentified__mutmut_24 # type: ignore # mutmut generated

mutants_xǁUserIdentityǁworker__mutmut['_mutmut_orig'] = UserIdentity.xǁUserIdentityǁworker__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_1'] = UserIdentity.xǁUserIdentityǁworker__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_2'] = UserIdentity.xǁUserIdentityǁworker__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_3'] = UserIdentity.xǁUserIdentityǁworker__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_4'] = UserIdentity.xǁUserIdentityǁworker__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_5'] = UserIdentity.xǁUserIdentityǁworker__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_6'] = UserIdentity.xǁUserIdentityǁworker__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_7'] = UserIdentity.xǁUserIdentityǁworker__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_8'] = UserIdentity.xǁUserIdentityǁworker__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_9'] = UserIdentity.xǁUserIdentityǁworker__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_10'] = UserIdentity.xǁUserIdentityǁworker__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_11'] = UserIdentity.xǁUserIdentityǁworker__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_12'] = UserIdentity.xǁUserIdentityǁworker__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_13'] = UserIdentity.xǁUserIdentityǁworker__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_14'] = UserIdentity.xǁUserIdentityǁworker__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_15'] = UserIdentity.xǁUserIdentityǁworker__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_16'] = UserIdentity.xǁUserIdentityǁworker__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁworker__mutmut['xǁUserIdentityǁworker__mutmut_17'] = UserIdentity.xǁUserIdentityǁworker__mutmut_17 # type: ignore # mutmut generated

mutants_xǁUserIdentityǁfrom_channel__mutmut['_mutmut_orig'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_orig # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_1'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_1 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_2'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_2 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_3'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_3 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_4'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_4 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_5'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_5 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_6'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_6 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_7'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_7 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_8'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_8 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_9'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_9 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_10'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_10 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_11'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_11 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_12'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_12 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_13'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_13 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_14'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_14 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_15'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_15 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_16'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_16 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_17'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_17 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_18'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_18 # type: ignore # mutmut generated
mutants_xǁUserIdentityǁfrom_channel__mutmut['xǁUserIdentityǁfrom_channel__mutmut_19'] = UserIdentity.xǁUserIdentityǁfrom_channel__mutmut_19 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut: MutantDict = {}  # type: ignore


@dataclass(frozen=True)
class JudgeFrictionMetric:
    """Value Object calculating LLM-as-a-judge retry friction per ADR-013 & ADR-016.

    Friction ratio = (iterations - 1) / (max_iterations - 1).
    0.0 = perfect first pass; 1.0 = all retries exhausted.
    """

    iterations: int
    max_iterations: int
    verdict: str

    @_mutmut_mutated(mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut)
    def __post_init__(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_orig(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_1(self) -> None:
        if self.iterations <= 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_2(self) -> None:
        if self.iterations < 2:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_3(self) -> None:
        if self.iterations < 1:
            raise ValueError(None)
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_4(self) -> None:
        if self.iterations < 1:
            raise ValueError("XXiterations must be >= 1XX")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_5(self) -> None:
        if self.iterations < 1:
            raise ValueError("ITERATIONS MUST BE >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_6(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations <= 1:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_7(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 2:
            raise ValueError("max_iterations must be >= 1")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_8(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError(None)

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_9(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("XXmax_iterations must be >= 1XX")

    def xǁJudgeFrictionMetricǁ__post_init____mutmut_10(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be >= 1")
        if self.max_iterations < 1:
            raise ValueError("MAX_ITERATIONS MUST BE >= 1")

    @property
    def friction_ratio(self) -> float:
        if self.iterations <= 1 or self.max_iterations <= 1:
            return 0.0
        return min(1.0, (self.iterations - 1) / (self.max_iterations - 1))

mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['_mutmut_orig'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_1'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_2'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_3'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_4'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_5'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_6'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_7'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_8'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_9'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁJudgeFrictionMetricǁ__post_init____mutmut['xǁJudgeFrictionMetricǁ__post_init____mutmut_10'] = JudgeFrictionMetric.xǁJudgeFrictionMetricǁ__post_init____mutmut_10 # type: ignore # mutmut generated
