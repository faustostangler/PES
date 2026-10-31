"""Unit tests for IAM Application Layer Use Cases.

Tests use cases with in-memory double adapters (Hermetic Testing).
Following Doctor Stangler Architecture Method (TDD Red-Green-Refactor).
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from identity.application.dtos import (
    AuthenticatedUserDTO,
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
from identity.application.use_cases.authenticate_user import (
    DUMMY_ARGON2_HASH,
    AuthenticateUserUseCase,
)
from identity.application.use_cases.manage_pat import (
    CreatePersonalAccessTokenUseCase,
    ListPersonalAccessTokensUseCase,
    RevokePersonalAccessTokenUseCase,
    ValidatePersonalAccessTokenUseCase,
)
from identity.application.use_cases.register_user import RegisterUserUseCase
from identity.application.use_cases.validate_token import ValidateTokenUseCase
from identity.domain.entities import PersonalAccessToken, User
from identity.domain.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRoleError,
    InvalidTokenError,
    UserAlreadyExistsError,
    WeakPasswordError,
)
from identity.domain.value_objects import (
    Email,
    HashedPassword,
    Role,
    Scope,
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
    def __init__(self) -> None:
        self.verified_calls: list[tuple[str, HashedPassword]] = []

    def hash(self, plain_password: str) -> HashedPassword:
        return HashedPassword(f"$dummy${plain_password}")

    def verify(self, plain_password: str, hashed: HashedPassword) -> bool:
        self.verified_calls.append((plain_password, hashed))
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


# Backward-compatible aliases for other test suites
InMemoryPasswordHasher = DummyPasswordHasher
InMemoryTokenService = DummyTokenService


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


class TestAuthenticatedUserDTO:
    def test_default_values(self) -> None:
        user = AuthenticatedUserDTO(user_id="usr_001")
        assert user.user_id == "usr_001"
        assert user.tenant_id == "default"
        assert user.email == ""
        assert user.roles == frozenset()
        assert user.scopes == frozenset()

    def test_explicit_values(self) -> None:
        user = AuthenticatedUserDTO(
            user_id="usr_002",
            tenant_id="tenant_pes",
            email="dev@pes.ai",
            roles=["editor", "user"],
            scopes=["cresmo:read", "cresmo:sync"],
        )
        assert user.user_id == "usr_002"
        assert user.tenant_id == "tenant_pes"
        assert user.email == "dev@pes.ai"
        assert user.roles == frozenset(["editor", "user"])
        assert user.scopes == frozenset(["cresmo:read", "cresmo:sync"])
        assert user.has_role("editor") is True
        assert user.has_role("viewer") is False
        assert user.has_scope("cresmo:sync") is True
        assert user.has_scope("cresmo:delete") is False


class TestRegisterUserUseCase:
    def test_register_new_user_success(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        use_case = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)

        before = datetime.now(UTC)
        dto = RegisterUserRequestDTO(
            email="newuser@example.com",
            password="SecurePassword123!",
            roles=["user"],
        )
        response = use_case.execute(dto)

        assert response.email == "newuser@example.com"
        assert response.roles == ["user"]
        assert response.user_id.startswith("usr_")
        saved = repo.get_by_email(Email("newuser@example.com"))
        assert saved is not None
        assert response.user_id == saved.id.value
        assert response.email == saved.email.value
        assert response.roles == [r.value for r in saved.roles]
        assert saved.has_role(Role.USER) is True
        assert saved.is_active is True
        assert saved.hashed_password.value == "$dummy$SecurePassword123!"
        assert saved.created_at is not None
        assert saved.created_at >= before
        assert saved.updated_at is not None
        assert saved.updated_at >= before

    def test_register_with_minimum_valid_password_length(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        use_case = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)

        dto = RegisterUserRequestDTO(
            email="minpass@example.com",
            password="12345678",  # Exactly 8 characters
            roles=["user"],
        )
        response = use_case.execute(dto)
        assert response.email == "minpass@example.com"

    def test_register_with_short_password_raises_error(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        use_case = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)

        dto = RegisterUserRequestDTO(
            email="shortpass@example.com",
            password="1234567",  # 7 characters (< 8)
            roles=["user"],
        )
        with pytest.raises(WeakPasswordError) as exc_info:
            use_case.execute(dto)
        assert exc_info.value.args[0] == "Password must be at least 8 characters long."

    def test_register_with_empty_roles_defaults_to_user(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        use_case = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)

        dto = RegisterUserRequestDTO(
            email="noroles@example.com",
            password="ValidPassword123!",
            roles=[],
        )
        response = use_case.execute(dto)
        assert response.roles == ["user"]
        saved = repo.get_by_email(Email("noroles@example.com"))
        assert saved is not None
        assert saved.roles == frozenset([Role.USER])

    def test_register_duplicate_email_raises_error(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        use_case = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)

        dto = RegisterUserRequestDTO(
            email="duplicate@example.com",
            password="Password123!",
        )
        use_case.execute(dto)

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            use_case.execute(dto)
        assert exc_info.value.args[0] == "User with email 'duplicate@example.com' is already registered."

    def test_register_with_invalid_role_raises_error(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        use_case = RegisterUserUseCase(user_repo=repo, password_hasher=hasher)

        dto = RegisterUserRequestDTO(
            email="invalidrole@example.com",
            password="Password123!",
            roles=["nonexistent_super_role"],
        )
        with pytest.raises(InvalidRoleError) as exc_info:
            use_case.execute(dto)
        assert exc_info.value.args[0] == "Invalid role: 'nonexistent_super_role'."


class TestAuthenticateUserUseCase:
    def test_authenticate_success(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        token_service = DummyTokenService()

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
        assert response.expires_in == 900
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

        with pytest.raises(InvalidCredentialsError) as exc_info:
            use_case.execute(LoginRequestDTO(email="login@example.com", password="WrongPassword"))
        assert exc_info.value.args[0] == "Invalid email or password."

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

        with pytest.raises(InactiveUserError) as exc_info:
            use_case.execute(LoginRequestDTO(email="inactive@example.com", password="Secret123"))
        assert exc_info.value.args[0] == "User account is deactivated."

    def test_authenticate_nonexistent_user_raises_error_and_verifies_dummy_hash(self) -> None:
        repo = InMemoryUserRepository()
        hasher = DummyPasswordHasher()
        token_service = DummyTokenService()

        use_case = AuthenticateUserUseCase(
            user_repo=repo,
            password_hasher=hasher,
            token_service=token_service,
        )

        with pytest.raises(InvalidCredentialsError) as exc_info:
            use_case.execute(LoginRequestDTO(email="notfound@example.com", password="Password123"))
        assert exc_info.value.args[0] == "Invalid email or password."
        assert len(hasher.verified_calls) == 1
        assert hasher.verified_calls[0] == ("Password123", DUMMY_ARGON2_HASH)


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
        before_create = datetime.now(UTC)
        created = create_uc.execute(create_dto)

        assert created.raw_token.startswith("cresmo_pat_")
        assert created.token_prefix == created.raw_token[:16]
        assert created.expires_at is not None
        assert datetime.fromisoformat(created.expires_at) >= before_create + timedelta(days=29)

        # Validate raw token
        authenticated = validate_uc.execute(created.raw_token)
        assert authenticated.user_id == "usr_cli"
        assert authenticated.tenant_id == "default"
        assert authenticated.email == "cli@example.com"
        assert "cresmo:sync" in authenticated.scopes
        assert Role.USER.value in authenticated.roles

        # Verify created DTO fields
        assert created.name == "CI Pipeline Runner"
        assert set(created.scopes) == {"cresmo:read", "cresmo:sync"}

        # Verify usage timestamp was recorded
        stored_pat = pat_repo.get_by_hash(TokenHash.from_raw_token(created.raw_token))
        assert stored_pat is not None
        assert stored_pat.last_used_at is not None
        assert stored_pat.last_used_at >= before_create

    def test_create_pat_without_expiration(self) -> None:
        pat_repo = InMemoryPATRepository()
        create_uc = CreatePersonalAccessTokenUseCase(pat_repo=pat_repo)
        created = create_uc.execute(CreatePATRequestDTO(user_id="usr_noexp", name="Infinite Token", expires_in_days=None))
        assert created.expires_at is None

    def test_validate_malformed_token_raises_error(self) -> None:
        pat_repo = InMemoryPATRepository()
        user_repo = InMemoryUserRepository()
        validate_uc = ValidatePersonalAccessTokenUseCase(pat_repo=pat_repo, user_repo=user_repo)

        with pytest.raises(InvalidTokenError) as exc_empty:
            validate_uc.execute("")
        assert exc_empty.value.args[0] == "Invalid token format."

        with pytest.raises(InvalidTokenError) as exc_prefix:
            validate_uc.execute("wrong_prefix_12345678901234567890")
        assert exc_prefix.value.args[0] == "Invalid token format."

        with pytest.raises(InvalidTokenError) as exc_notfound:
            validate_uc.execute("cresmo_pat_not_registered_secret_12345")
        assert exc_notfound.value.args[0] == "Personal Access Token is invalid, revoked or expired."

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

        with pytest.raises(InvalidTokenError) as exc_info:
            validate_uc.execute(created.raw_token)
        assert exc_info.value.args[0] == "Personal Access Token is invalid, revoked or expired."

    def test_validate_expired_pat_raises_error(self) -> None:
        pat_repo = InMemoryPATRepository()
        user_repo = InMemoryUserRepository()
        user = User(
            id=UserId("usr_cli"),
            email=Email("cli@example.com"),
            hashed_password=HashedPassword("$dummy$pass"),
        )
        user_repo.save(user)

        raw = "cresmo_pat_expired_token_raw_123456789"
        expired_pat = PersonalAccessToken(
            id="pat_exp",
            user_id=user.id,
            name="Expired",
            token_prefix=raw[:16],
            token_hash=TokenHash.from_raw_token(raw),
            scopes=frozenset([Scope("cresmo:sync")]),
            created_at=datetime.now(UTC) - timedelta(days=2),
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        pat_repo.save(expired_pat)

        validate_uc = ValidatePersonalAccessTokenUseCase(pat_repo=pat_repo, user_repo=user_repo)
        with pytest.raises(InvalidTokenError) as exc_info:
            validate_uc.execute(raw)
        assert exc_info.value.args[0] == "Personal Access Token is invalid, revoked or expired."

    def test_validate_pat_with_inactive_or_missing_user_raises_error(self) -> None:
        pat_repo = InMemoryPATRepository()
        user_repo = InMemoryUserRepository()

        raw = "cresmo_pat_missing_user_raw_1234567890"
        pat = PersonalAccessToken(
            id="pat_missing",
            user_id=UserId("usr_ghost"),
            name="Ghost",
            token_prefix=raw[:16],
            token_hash=TokenHash.from_raw_token(raw),
            scopes=frozenset(),
            created_at=datetime.now(UTC),
        )
        pat_repo.save(pat)

        validate_uc = ValidatePersonalAccessTokenUseCase(pat_repo=pat_repo, user_repo=user_repo)
        with pytest.raises(InvalidTokenError) as exc_missing:
            validate_uc.execute(raw)
        assert exc_missing.value.args[0] == "User account associated with this token is inactive or not found."

        # Inactive user
        inactive_user = User(
            id=UserId("usr_inactive"),
            email=Email("inactive_pat@example.com"),
            hashed_password=HashedPassword("$dummy$pass"),
            is_active=False,
        )
        user_repo.save(inactive_user)
        raw_inactive = "cresmo_pat_inactive_user_raw_12345678"
        pat_inactive = PersonalAccessToken(
            id="pat_inact",
            user_id=inactive_user.id,
            name="Inactive",
            token_prefix=raw_inactive[:16],
            token_hash=TokenHash.from_raw_token(raw_inactive),
            scopes=frozenset(),
            created_at=datetime.now(UTC),
        )
        pat_repo.save(pat_inactive)
        with pytest.raises(InvalidTokenError) as exc_inact:
            validate_uc.execute(raw_inactive)
        assert exc_inact.value.args[0] == "User account associated with this token is inactive or not found."


class TestListPersonalAccessTokensUseCase:
    def test_list_pats_returns_all_user_tokens(self) -> None:
        pat_repo = InMemoryPATRepository()
        create_uc = CreatePersonalAccessTokenUseCase(pat_repo=pat_repo)
        list_uc = ListPersonalAccessTokensUseCase(pat_repo=pat_repo)

        t1 = create_uc.execute(CreatePATRequestDTO(user_id="usr_1", name="Token 1", scopes=["cresmo:sync"], expires_in_days=10))
        t2 = create_uc.execute(CreatePATRequestDTO(user_id="usr_1", name="Token 2", scopes=["cresmo:admin"], expires_in_days=None))
        create_uc.execute(CreatePATRequestDTO(user_id="usr_2", name="Token Other", scopes=[]))

        # Simulate usage on t1
        stored_t1 = pat_repo.get_by_hash(TokenHash.from_raw_token(t1.raw_token))
        assert stored_t1 is not None
        stored_t1.record_usage()
        pat_repo.save(stored_t1)

        items = list_uc.execute(UserId("usr_1"))
        assert len(items) == 2

        item_map = {item.id: item for item in items}
        assert t1.id in item_map
        assert t2.id in item_map

        i1 = item_map[t1.id]
        assert i1.name == "Token 1"
        assert i1.token_prefix == t1.token_prefix
        assert i1.scopes == ["cresmo:sync"]
        assert i1.created_at is not None
        assert i1.expires_at is not None
        assert i1.last_used_at is not None
        assert i1.is_active is True

        i2 = item_map[t2.id]
        assert i2.name == "Token 2"
        assert i2.token_prefix == t2.token_prefix
        assert i2.scopes == ["cresmo:admin"]
        assert i2.created_at is not None
        assert i2.expires_at is None
        assert i2.last_used_at is None
        assert i2.is_active is True


class TestRevokePersonalAccessTokenUseCase:
    def test_revoke_existing_pat_returns_true(self) -> None:
        pat_repo = InMemoryPATRepository()
        create_uc = CreatePersonalAccessTokenUseCase(pat_repo=pat_repo)
        revoke_uc = RevokePersonalAccessTokenUseCase(pat_repo=pat_repo)

        t1 = create_uc.execute(CreatePATRequestDTO(user_id="usr_1", name="Token 1"))
        assert revoke_uc.execute(t1.id, UserId("usr_1")) is True

        tokens = pat_repo.list_by_user(UserId("usr_1"))
        assert len(tokens) == 1
        assert tokens[0].is_active is False

    def test_revoke_nonexistent_or_other_user_pat_returns_false(self) -> None:
        pat_repo = InMemoryPATRepository()
        create_uc = CreatePersonalAccessTokenUseCase(pat_repo=pat_repo)
        revoke_uc = RevokePersonalAccessTokenUseCase(pat_repo=pat_repo)

        t1 = create_uc.execute(CreatePATRequestDTO(user_id="usr_1", name="Token 1"))
        assert revoke_uc.execute(t1.id, UserId("usr_2")) is False
        assert revoke_uc.execute("nonexistent", UserId("usr_1")) is False


class TestValidateTokenUseCase:
    def test_validate_valid_token_success(self) -> None:
        user_repo = InMemoryUserRepository()
        token_service = DummyTokenService()
        user = User(
            id=UserId("usr_jwt_valid"),
            email=Email("jwt@example.com"),
            hashed_password=HashedPassword("$dummy$pass"),
            roles=frozenset([Role.USER]),
        )
        user_repo.save(user)
        token = token_service.create_access_token(user)

        use_case = ValidateTokenUseCase(token_service=token_service, user_repo=user_repo)
        auth_user = use_case.execute(token)

        assert auth_user.user_id == "usr_jwt_valid"
        assert auth_user.email == "jwt@example.com"
        assert auth_user.has_role(Role.USER.value) is True
        assert auth_user.tenant_id == "default"

    def test_validate_token_with_custom_tenant_and_scopes(self) -> None:
        user_repo = InMemoryUserRepository()
        user = User(
            id=UserId("usr_custom_claims"),
            email=Email("custom@example.com"),
            hashed_password=HashedPassword("$dummy$pass"),
            roles=frozenset([Role.ADMIN]),
        )
        user_repo.save(user)

        class CustomClaimsTokenService(TokenServicePort):
            def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str:
                return "custom_token"

            def decode_access_token(self, token: str) -> dict[str, Any]:
                return {
                    "sub": "usr_custom_claims",
                    "tenant_id": "tenant_custom_123",
                    "scopes": ["cresmo:read", "cresmo:sync"],
                }

        use_case = ValidateTokenUseCase(token_service=CustomClaimsTokenService(), user_repo=user_repo)
        auth_user = use_case.execute("custom_token")

        assert auth_user.user_id == "usr_custom_claims"
        assert auth_user.tenant_id == "tenant_custom_123"
        assert auth_user.scopes == frozenset(["cresmo:read", "cresmo:sync"])

    def test_validate_token_missing_subject_raises_error(self) -> None:
        user_repo = InMemoryUserRepository()

        class MissingSubTokenService(TokenServicePort):
            def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str:
                return "token"

            def decode_access_token(self, token: str) -> dict[str, Any]:
                return {"roles": ["user"]}

        use_case = ValidateTokenUseCase(token_service=MissingSubTokenService(), user_repo=user_repo)
        with pytest.raises(InvalidTokenError, match="missing subject") as exc_info:
            use_case.execute("token")
        assert exc_info.value.args[0] == "Access token claims missing subject ('sub')."

    def test_validate_token_user_not_found_raises_error(self) -> None:
        user_repo = InMemoryUserRepository()
        token_service = DummyTokenService()
        dummy_user = User(
            id=UserId("usr_nonexistent"),
            email=Email("nonexistent@example.com"),
            hashed_password=HashedPassword("$dummy$pass"),
        )
        token = token_service.create_access_token(dummy_user)

        use_case = ValidateTokenUseCase(token_service=token_service, user_repo=user_repo)
        with pytest.raises(InvalidTokenError, match="inactive or not found") as exc_info:
            use_case.execute(token)
        assert exc_info.value.args[0] == "User account is inactive or not found."

    def test_validate_token_inactive_user_raises_error(self) -> None:
        user_repo = InMemoryUserRepository()
        token_service = DummyTokenService()
        user = User(
            id=UserId("usr_inactive"),
            email=Email("inactive@example.com"),
            hashed_password=HashedPassword("$dummy$pass"),
            is_active=False,
        )
        user_repo.save(user)
        token = token_service.create_access_token(user)

        use_case = ValidateTokenUseCase(token_service=token_service, user_repo=user_repo)
        with pytest.raises(InvalidTokenError, match="inactive or not found") as exc_info:
            use_case.execute(token)
        assert exc_info.value.args[0] == "User account is inactive or not found."


