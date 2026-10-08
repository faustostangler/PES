"""FastAPI Router exposing authentication, account, and PAT endpoints."""

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
    UserAlreadyExistsError,
    WeakPasswordError,
)
from identity.domain.value_objects import UserId
from identity.presentation.composition import IdentityContainer, get_identity_container
from identity.presentation.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# Pydantic Schemas for HTTP Serialization & Validation
class RegisterSchema(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8)
    roles: list[str] = Field(default_factory=lambda: ["user"])


class LoginSchema(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str


class CreatePATSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scopes: list[str] = Field(default_factory=list)
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


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
async def register(
    payload: RegisterSchema,
    container: IdentityContainer = Depends(get_identity_container),
) -> RegisterUserResponseDTO:
    dto = RegisterUserRequestDTO(
        email=payload.email,
        password=payload.password,
        roles=payload.roles,
    )
    try:
        return container.register_user_uc.execute(dto)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except (InvalidEmailError, WeakPasswordError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post(
    "/login",
    response_model=TokenResponseDTO,
    summary="Authenticate and receive JWT access token",
)
async def login(
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
            headers={"WWW-Authenticate": "Bearer"},
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
async def get_me(
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
) -> AuthenticatedUserDTO:
    return current_user


@router.post(
    "/tokens",
    response_model=CreatedPATResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Personal Access Token (revealed once)",
)
async def create_personal_access_token(
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
    "/tokens",
    response_model=list[PATListItemSchema],
    summary="List active Personal Access Tokens for current user",
)
async def list_personal_access_tokens(
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
    container: IdentityContainer = Depends(get_identity_container),
) -> list[PATListItemSchema]:
    tokens = container.pat_repo.list_by_user(UserId(current_user.user_id))
    return [
        PATListItemSchema(
            id=t.id,
            name=t.name,
            token_prefix=t.token_prefix,
            scopes=[s.value for s in t.scopes],
            created_at=t.created_at.isoformat(),
            expires_at=t.expires_at.isoformat() if t.expires_at else None,
            last_used_at=t.last_used_at.isoformat() if t.last_used_at else None,
            is_active=t.is_active,
        )
        for t in tokens
    ]


@router.delete(
    "/tokens/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke Personal Access Token",
)
async def revoke_personal_access_token(
    token_id: str,
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
    container: IdentityContainer = Depends(get_identity_container),
) -> None:
    revoked = container.pat_repo.revoke(token_id, UserId(current_user.user_id))
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal Access Token '{token_id}' not found.",
        )
