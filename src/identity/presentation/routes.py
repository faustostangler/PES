"""FastAPI Router exposing authentication, account, and PAT endpoints."""

from typing import Final

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from identity.application.dtos import (
    AuthenticatedUserDTO,
    CreatedPATResponseDTO,
    CreatePATRequestDTO,
    LoginRequestDTO,
    RegisterUserRequestDTO,
    RegisterUserResponseDTO,
    TokenResponseDTO,
)
from identity.domain.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidRoleError,
    UserAlreadyExistsError,
    WeakPasswordError,
)
from identity.domain.value_objects import Role, UserId
from identity.presentation.composition import IdentityContainer, get_identity_container
from identity.presentation.dependencies import (
    AUTH_SCHEME_BEARER_HEADER,
    WWW_AUTHENTICATE_HEADER,
    get_current_user,
)

AUTH_ROUTER_PREFIX: Final[str] = "/auth"
AUTH_ROUTER_TAG: Final[str] = "auth"
ROUTE_TOKENS: Final[str] = "/tokens"

MIN_EMAIL_LENGTH: Final[int] = 3
MAX_EMAIL_LENGTH: Final[int] = 255
MIN_PASSWORD_LENGTH: Final[int] = 8
MIN_PAT_NAME_LENGTH: Final[int] = 1
MAX_PAT_NAME_LENGTH: Final[int] = 100
MIN_PAT_EXPIRATION_DAYS: Final[int] = 1
MAX_PAT_EXPIRATION_DAYS: Final[int] = 365

router = APIRouter(prefix=AUTH_ROUTER_PREFIX, tags=[AUTH_ROUTER_TAG])


# Pydantic Schemas for HTTP Serialization & Validation
class RegisterSchema(BaseModel):
    email: str = Field(min_length=MIN_EMAIL_LENGTH, max_length=MAX_EMAIL_LENGTH)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)


class LoginSchema(BaseModel):
    email: str = Field(min_length=MIN_EMAIL_LENGTH, max_length=MAX_EMAIL_LENGTH)
    password: str


class CreatePATSchema(BaseModel):
    name: str = Field(min_length=MIN_PAT_NAME_LENGTH, max_length=MAX_PAT_NAME_LENGTH)
    scopes: list[str] = Field(default_factory=list)
    expires_in_days: int | None = Field(
        default=None, ge=MIN_PAT_EXPIRATION_DAYS, le=MAX_PAT_EXPIRATION_DAYS
    )


class PATListItemSchema(BaseModel):
    id: str
    name: str
    token_prefix: str
    scopes: list[str]
    created_at: str
    expires_at: str | None
    last_used_at: str | None
    is_active: bool


@router.post(
    "/register",
    response_model=RegisterUserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
)
def register(
    payload: RegisterSchema,
    container: IdentityContainer = Depends(get_identity_container),
) -> RegisterUserResponseDTO:
    dto = RegisterUserRequestDTO(
        email=payload.email,
        password=payload.password,
        roles=[Role.USER.value],
    )
    try:
        return container.register_user_uc.execute(dto)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except (InvalidEmailError, WeakPasswordError, InvalidRoleError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post(
    "/login",
    response_model=TokenResponseDTO,
    summary="Authenticate and receive JWT access token",
)
def login(
    payload: LoginSchema,
    container: IdentityContainer = Depends(get_identity_container),
) -> TokenResponseDTO:
    dto = LoginRequestDTO(email=payload.email, password=payload.password)
    try:
        return container.authenticate_user_uc.execute(dto)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={WWW_AUTHENTICATE_HEADER: AUTH_SCHEME_BEARER_HEADER},
        ) from e
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        ) from e


@router.get(
    "/me",
    response_model=AuthenticatedUserDTO,
    summary="Get current authenticated user profile",
)
def get_me(
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
) -> AuthenticatedUserDTO:
    return current_user


@router.post(
    ROUTE_TOKENS,
    response_model=CreatedPATResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Personal Access Token (revealed once)",
)
def create_personal_access_token(
    payload: CreatePATSchema,
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
    container: IdentityContainer = Depends(get_identity_container),
) -> CreatedPATResponseDTO:
    dto = CreatePATRequestDTO(
        user_id=current_user.user_id,
        name=payload.name,
        scopes=payload.scopes,
        expires_in_days=payload.expires_in_days,
    )
    return container.create_pat_uc.execute(dto)


@router.get(
    ROUTE_TOKENS,
    response_model=list[PATListItemSchema],
    summary="List active Personal Access Tokens for current user",
)
def list_personal_access_tokens(
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
    container: IdentityContainer = Depends(get_identity_container),
) -> list[PATListItemSchema]:
    items = container.list_pats_uc.execute(UserId(current_user.user_id))
    return [
        PATListItemSchema(
            id=t.id,
            name=t.name,
            token_prefix=t.token_prefix,
            scopes=t.scopes,
            created_at=t.created_at,
            expires_at=t.expires_at,
            last_used_at=t.last_used_at,
            is_active=t.is_active,
        )
        for t in items
    ]


@router.delete(
    "/tokens/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke Personal Access Token",
)
def revoke_personal_access_token(
    token_id: str,
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
    container: IdentityContainer = Depends(get_identity_container),
) -> None:
    revoked = container.revoke_pat_uc.execute(token_id, UserId(current_user.user_id))
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal Access Token '{token_id}' not found.",
        )
