"""Hermetic Unit Tests for PipelineExecutionContext Value Object.

Conforms to:
    - ADR-031: Pipeline Execution Context and Observability Fabric
    - SPEC-013: Pipeline Execution Context Contract
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.domain.entities import UserIdentity
from cresmo.domain.value_objects import Channel, ChannelId, ChannelName, Content, ContentId


class TestPipelineExecutionContext:
    """Test suite for PipelineExecutionContext value object validation and immutability."""

    def test_valid_context_instantiation(self) -> None:
        user_identity = UserIdentity.worker()
        channel = Channel(name=ChannelName("TechChannel"), id=ChannelId("UC_12345"))
        content = Content(id=ContentId("c1234567"), title="Episode 1", session_id="ch_1:content_1")

        ctx = PipelineExecutionContext(
            user_identity=user_identity,
            channel=channel,
            content=content,
        )

        assert not hasattr(ctx, "session_id")
        assert ctx.content.session_id == "ch_1:content_1"
        assert ctx.user_identity == user_identity
        assert ctx.channel == channel
        assert ctx.content == content

    def test_auto_populates_content_session_id_when_empty(self) -> None:
        user_identity = UserIdentity.worker()
        channel = Channel(name=ChannelName("TechChannel"), id=ChannelId("UC_12345"))
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        ctx = PipelineExecutionContext(
            user_identity=user_identity,
            channel=channel,
            content=content,
        )

        assert ctx.content.session_id == "UC_12345:c1234567"

    def test_invalid_user_identity_raises_type_error(self) -> None:
        channel = Channel(name=ChannelName("TechChannel"))
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        with pytest.raises(
            TypeError, match=r"^user_identity must be UserIdentity, got <class 'str'>$"
        ):
            PipelineExecutionContext(
                user_identity="not_a_user_identity",  # type: ignore[arg-type]
                channel=channel,
                content=content,
            )

    def test_invalid_channel_raises_type_error(self) -> None:
        user_identity = UserIdentity.worker()
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        with pytest.raises(TypeError, match=r"^channel must be Channel, got <class 'str'>$"):
            PipelineExecutionContext(
                user_identity=user_identity,
                channel="not_a_channel",  # type: ignore[arg-type]
                content=content,
            )

    def test_invalid_content_raises_type_error(self) -> None:
        user_identity = UserIdentity.worker()
        channel = Channel(name=ChannelName("TechChannel"))

        with pytest.raises(TypeError, match=r"^content must be Content, got <class 'str'>$"):
            PipelineExecutionContext(
                user_identity=user_identity,
                channel=channel,
                content="not_a_content",  # type: ignore[arg-type]
            )

    def test_context_is_immutable(self) -> None:
        user_identity = UserIdentity.worker()
        channel = Channel(name=ChannelName("TechChannel"))
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        ctx = PipelineExecutionContext(
            user_identity=user_identity,
            channel=channel,
            content=content,
        )

        with pytest.raises(FrozenInstanceError):
            ctx.user_identity = UserIdentity.anonymous()  # type: ignore[misc]
