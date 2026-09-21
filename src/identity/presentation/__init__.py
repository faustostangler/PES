"""Presentation layer for Identity & Access Management (IAM)."""

from identity.presentation.composition import (
    IdentityContainer,
    get_identity_container,
    set_identity_container,
)
from identity.presentation.dependencies import (
    get_current_user,
    require_role,
    require_scope,
)
from identity.presentation.routes import router as auth_router

__all__ = [
    "IdentityContainer",
    "auth_router",
    "get_current_user",
    "get_identity_container",
    "require_role",
    "require_scope",
    "set_identity_container",
]
