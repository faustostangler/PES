"""FastAPI Authentication and Authorization Dependencies for Dual-Gate Security."""

from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, status

from identity.application.dtos import AuthenticatedUserDTO
from identity.domain.exceptions import InactiveUserError, InvalidTokenError
from identity.presentation.composition import IdentityContainer, get_identity_container


async def get_current_user(
    authorization: str | None = Header(default=None),
    x_cresmo_pat: str | None = Header(default=None, alias="X-Cresmo-PAT"),
    container: IdentityContainer = Depends(get_identity_container),
) -> AuthenticatedUserDTO:
    """Extracts and validates security principal from either Bearer JWT or X-Cresmo-PAT header.

    Supports:
    1. Authorization: Bearer <jwt_access_token> (For SvelteKit BFF and Web Clients)
    2. X-Cresmo-PAT: cresmo_pat_<token> (For Terminal CLI and Daemon Workers)
    """
    # 1. Check Personal Access Token (CLI / Worker)
    if x_cresmo_pat:
        try:
            return container.validate_pat_uc.execute(x_cresmo_pat)
        except (InvalidTokenError, InactiveUserError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Personal Access Token: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    # 2. Check Bearer JWT (Web / BFF)
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            try:
                return container.validate_token_uc.execute(token)
            except (InvalidTokenError, InactiveUserError) as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid access token: {e}",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from e

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication credentials. Provide 'Authorization: Bearer <token>' or 'X-Cresmo-PAT: <token>'.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(required_role: str) -> Callable[[AuthenticatedUserDTO], AuthenticatedUserDTO]:
    """Dependency factory enforcing specific Role access."""

    def role_checker(
        current_user: AuthenticatedUserDTO = Depends(get_current_user),
    ) -> AuthenticatedUserDTO:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires role '{required_role}'.",
            )
        return current_user

    return role_checker


def require_scope(required_scope: str) -> Callable[[AuthenticatedUserDTO], AuthenticatedUserDTO]:
    """Dependency factory enforcing specific permission Scope."""

    def scope_checker(
        current_user: AuthenticatedUserDTO = Depends(get_current_user),
    ) -> AuthenticatedUserDTO:
        if not current_user.has_scope(required_scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires scope '{required_scope}'.",
            )
        return current_user

    return scope_checker
