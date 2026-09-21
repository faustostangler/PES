"""Unit tests for IAM Application Layer Use Cases.

Tests use cases with in-memory double adapters (Hermetic Testing).
Following Doctor Stangler Architecture Method (TDD Red-Green-Refactor).
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from identity.application.dtos import (
    CreatePATRequestDTO,
    LoginRequestDTO,
    RegisterUserRequestDTO,
)
from identity.application.ports import (
    PasswordHasherPort,
    PersonalAccessTokenRepositoryPort,
    TokenServicePort,
    UserRepositoryPort,
)
from identity.application.use_cases.authenticate_user import AuthenticateUserUseCase
from identity.application.use_cases.manage_pat import (
    CreatePersonalAccessTokenUseCase,
    ValidatePersonalAccessTokenUseCase,
)
from identity.application.use_cases.register_user import RegisterUserUseCase
from identity.domain.entities import PersonalAccessToken, User
from identity.domain.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from identity.domain.value_objects import (
    Email,
    HashedPassword,
    Role,
    TokenHash,
    UserId,
)


class InMemoryUserRepository(UserRepositoryPort):
    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def save(self, user: User) -> None:
        if str(user.email) in self._users:
            raise UserAlreadyExistsError(f"User with email '{user.email}' already exists.")
        self._users[str(user.email)] = user

    def get_by_id(self, user_id: UserId) -> User | None:
        for u in self._users.values():
            if u.id == user_id:
                return u
        return None

    def get_by_email(self, email: Email) -> User | None:
        return self._users.get(str(email))

    def update(self, user: User) -> None:
        self._users[str(user.email)] = user


class DummyPasswordHasher(PasswordHasherPort):
    def hash(self, plain_password: str) -> HashedPassword:
        return HashedPassword(f"$dummy${plain_password}")

    def verify(self, plain_password: str, hashed: HashedPassword) -> bool:
        return hashed.value == f"$dummy${plain_password}"


class DummyTokenService(TokenServicePort):
    def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        roles_str = ",".join(r.value for r in user.roles)
        return f"mock_jwt:{user.id.value}:{user.email.value}:{roles_str}"

    def decode_access_token(self, token: str) -> dict[str, Any]:
        if not token.startswith("mock_jwt:"):
            raise InvalidTokenError("Invalid token structure.")
        parts = token.split(":")
        return {
            "sub": parts[1],
            "email": parts[2],
            "roles": parts[3].split(",") if parts[3] else [],
            "exp": (datetime.now(UTC) + timedelta(minutes=15)).timestamp(),
        }


class InMemoryPATRepository(PersonalAccessTokenRepositoryPort):
    def __init__(self) -> None:
        self._pats: dict[str, PersonalAccessToken] = {}

    def save(self, pat: PersonalAccessToken) -> None:
        self._pats[pat.token_hash.value] = pat

    def get_by_hash(self, token_hash: TokenHash) -> PersonalAccessToken | None:
        return self._pats.get(token_hash.value)

    def list_by_user(self, user_id: UserId) -> list[PersonalAccessToken]:
        return [p for p in self._pats.values() if p.user_id == user_id]

    def revoke(self, token_id: str, user_id: UserId) -> bool:
        for p in self._pats.values():
            if p.id == token_id and p.user_id == user_id:
                p.revoke()
                return True
        return False


class TestRegisterUserUseCase:
    def test_register_new_user_success(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        use_case = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)

        dto = RegisterUserRequestDTO(
            email="newuser@example.com",
            password="SecurePassword123!",
            roles=["user"],
        )
        response = use_case.execute(dto)

        assert response.email == "newuser@example.com"
        saved = repo.get_by_email(Email("newuser@example.com"))
        assert saved is not None
        assert saved.has_role(Role.USER) is True

    def test_register_duplicate_email_raises_error(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        use_case = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)

        dto = RegisterUserRequestDTO(
            email="duplicate@example.com",
            password="Password123!",
        )
        use_case.execute(dto)

        with pytest.raises(UserAlreadyExistsError):
            use_case.execute(dto)


class TestAuthenticateUserUseCase:
    def test_authenticate_success(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        token_service = DummyTokenService()

        # Seed user
        user = User(
            id=UserId("usr_1"),
            email=Email("login@example.com"),
            hashed_password=hasher.hash("Secret123"),
            roles=frozenset([Role.USER]),
        )
        repo.save(user)

        use_case = AuthenticateUserUseCase(
            user_repo=repo,
            password_hasher=hasher,
            token_service=token_service,
        )

        response = use_case.execute(
            LoginRequestDTO(email="login@example.com", password="Secret123")
        )
        assert response.token_type == "bearer"
        assert response.access_token.startswith("mock_jwt:usr_1:login@example.com:user")

    def test_authenticate_invalid_password_raises_error(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        token_service = DummyTokenService()

        user = User(
            id=UserId("usr_1"),
            email=Email("login@example.com"),
            hashed_password=hasher.hash("Secret123"),
        )
        repo.save(user)

        use_case = AuthenticateUserUseCase(
            user_repo=repo,
            password_hasher=hasher,
            token_service=token_service,
        )

        with pytest.raises(InvalidCredentialsError):
            use_case.execute(LoginRequestDTO(email="login@example.com", password="WrongPassword"))

    def test_authenticate_inactive_user_raises_error(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        token_service = DummyTokenService()

        user = User(
            id=UserId("usr_1"),
            email=Email("inactive@example.com"),
            hashed_password=hasher.hash("Secret123"),
            is_active=False,
        )
        repo.save(user)

        use_case = AuthenticateUserUseCase(
            user_repo=repo,
            password_hasher=hasher,
            token_service=token_service,
        )

        with pytest.raises(InactiveUserError):
            use_case.execute(LoginRequestDTO(email="inactive@example.com", password="Secret123"))


class TestPersonalAccessTokenUseCases:
    def test_create_and_validate_pat_success(self) -> None:
        pat_repo = InMemoryPATRepository()
        user_repo = InMemoryUserRepository()
        user = User(
            id=UserId("usr_cli"),
            email=Email("cli@example.com"),
            hashed_password=HashedPassword("$dummy$pass"),
            roles=frozenset([Role.USER]),
        )
        user_repo.save(user)

        create_uc = CreatePersonalAccessTokenUseCase(pat_repo=pat_repo)
        validate_uc = ValidatePersonalAccessTokenUseCase(pat_repo=pat_repo, user_repo=user_repo)

        create_dto = CreatePATRequestDTO(
            user_id="usr_cli",
            name="CI Pipeline Runner",
            scopes=["cresmo:read", "cresmo:sync"],
            expires_in_days=30,
        )
        created = create_uc.execute(create_dto)

        assert created.raw_token.startswith("cresmo_pat_")
        assert created.token_prefix.startswith("cresmo_p")

        # Validate raw token
        authenticated = validate_uc.execute(created.raw_token)
        assert authenticated.user_id == "usr_cli"
        assert "cresmo:sync" in authenticated.scopes
        assert Role.USER.value in authenticated.roles

    def test_validate_revoked_pat_raises_error(self) -> None:
        pat_repo = InMemoryPATRepository()
        user_repo = InMemoryUserRepository()
        user = User(
            id=UserId("usr_cli"),
            email=Email("cli@example.com"),
            hashed_password=HashedPassword("$dummy$pass"),
        )
        user_repo.save(user)

        create_uc = CreatePersonalAccessTokenUseCase(pat_repo=pat_repo)
        validate_uc = ValidatePersonalAccessTokenUseCase(pat_repo=pat_repo, user_repo=user_repo)

        created = create_uc.execute(CreatePATRequestDTO(user_id="usr_cli", name="Token to Revoke"))
        pat_repo.revoke(created.id, UserId("usr_cli"))

        with pytest.raises(InvalidTokenError, match="revoked or expired"):
            validate_uc.execute(created.raw_token)
