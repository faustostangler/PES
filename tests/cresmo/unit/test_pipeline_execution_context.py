"""Hermetic Unit Tests for PipelineExecutionContext Value Object.

Conforms to:
    - ADR-031: Pipeline Execution Context and Observability Fabric
    - SPEC-013: Pipeline Execution Context Contract
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from cresmo.application.pipeline.context import PipelineExecutionContext
from cresmo.domain.entities import PipelineSessionId, UserIdentity
from cresmo.domain.value_objects import Channel, ChannelId, ChannelName, Content, ContentId


class TestPipelineExecutionContext:
    """Test suite for PipelineExecutionContext value object validation and immutability."""

    def test_valid_context_instantiation(self) -> None:
        session_id = PipelineSessionId("ch_1:content_1")
        user_identity = UserIdentity.worker()
        channel = Channel(name=ChannelName("TechChannel"), id=ChannelId("UC_12345"))
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        ctx = PipelineExecutionContext(
            session_id=session_id,
            user_identity=user_identity,
            channel=channel,
            content=content,
        )

        assert ctx.session_id == session_id
        assert ctx.user_identity == user_identity
        assert ctx.channel == channel
        assert ctx.content == content

    def test_invalid_session_id_raises_type_error(self) -> None:
        user_identity = UserIdentity.worker()
        channel = Channel(name=ChannelName("TechChannel"))
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        with pytest.raises(TypeError, match="session_id must be PipelineSessionId, got"):
            PipelineExecutionContext(
                session_id="not_a_session_id",  # type: ignore[arg-type]
                user_identity=user_identity,
                channel=channel,
                content=content,
            )

    def test_invalid_user_identity_raises_type_error(self) -> None:
        session_id = PipelineSessionId("ch_1:content_1")
        channel = Channel(name=ChannelName("TechChannel"))
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        with pytest.raises(TypeError, match="user_identity must be UserIdentity, got"):
            PipelineExecutionContext(
                session_id=session_id,
                user_identity="not_a_user_identity",  # type: ignore[arg-type]
                channel=channel,
                content=content,
            )

    def test_invalid_channel_raises_type_error(self) -> None:
        session_id = PipelineSessionId("ch_1:content_1")
        user_identity = UserIdentity.worker()
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        with pytest.raises(TypeError, match="channel must be Channel, got"):
            PipelineExecutionContext(
                session_id=session_id,
                user_identity=user_identity,
                channel="not_a_channel",  # type: ignore[arg-type]
                content=content,
            )

    def test_invalid_content_raises_type_error(self) -> None:
        session_id = PipelineSessionId("ch_1:content_1")
        user_identity = UserIdentity.worker()
        channel = Channel(name=ChannelName("TechChannel"))

        with pytest.raises(TypeError, match="content must be Content, got"):
            PipelineExecutionContext(
                session_id=session_id,
                user_identity=user_identity,
                channel=channel,
                content="not_a_content",  # type: ignore[arg-type]
            )

    def test_context_is_immutable(self) -> None:
        session_id = PipelineSessionId("ch_1:content_1")
        user_identity = UserIdentity.worker()
        channel = Channel(name=ChannelName("TechChannel"))
        content = Content(id=ContentId("c1234567"), title="Episode 1")

        ctx = PipelineExecutionContext(
            session_id=session_id,
            user_identity=user_identity,
            channel=channel,
            content=content,
        )

        with pytest.raises(FrozenInstanceError):
            ctx.session_id = PipelineSessionId("ch_2:content_2")  # type: ignore[misc]
