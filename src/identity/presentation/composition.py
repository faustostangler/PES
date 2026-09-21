"""Composition Root for IAM Bounded Context.

Wires together infrastructure adapters and application use cases.
"""

from identity.application.use_cases.authenticate_user import AuthenticateUserUseCase
from identity.application.use_cases.manage_pat import (
    CreatePersonalAccessTokenUseCase,
    ValidatePersonalAccessTokenUseCase,
)
from identity.application.use_cases.register_user import RegisterUserUseCase
from identity.application.use_cases.validate_token import ValidateTokenUseCase
from identity.infrastructure.adapters.argon2_hasher_adapter import Argon2PasswordHasherAdapter
from identity.infrastructure.adapters.jwt_token_adapter import JwtTokenServiceAdapter
from identity.infrastructure.adapters.sqlite_user_repository import (
    SqlitePersonalAccessTokenRepositoryAdapter,
    SqliteUserRepositoryAdapter,
)
from identity.infrastructure.settings import IdentitySettings


class IdentityContainer:
    """Dependency injection container for IAM Bounded Context."""

    def __init__(self, settings: IdentitySettings | None = None) -> None:
        self.settings = settings or IdentitySettings()

        # Infrastructure Adapters
        self.password_hasher = Argon2PasswordHasherAdapter(self.settings)
        self.token_service = JwtTokenServiceAdapter(self.settings)
        self.user_repo = SqliteUserRepositoryAdapter(self.settings.identity_db_path)
        self.pat_repo = SqlitePersonalAccessTokenRepositoryAdapter(self.settings.identity_db_path)

        # Application Use Cases
        self.register_user_uc = RegisterUserUseCase(self.user_repo, self.password_hasher)
        self.authenticate_user_uc = AuthenticateUserUseCase(
            self.user_repo,
            self.password_hasher,
            self.token_service,
        )
        self.create_pat_uc = CreatePersonalAccessTokenUseCase(self.pat_repo)
        self.validate_pat_uc = ValidatePersonalAccessTokenUseCase(self.pat_repo, self.user_repo)
        self.validate_token_uc = ValidateTokenUseCase(self.token_service, self.user_repo)


# Global singleton instance for presentation layer injection
_default_container: IdentityContainer | None = None


def get_identity_container() -> IdentityContainer:
    global _default_container
    if _default_container is None:
        _default_container = IdentityContainer()
    return _default_container


def set_identity_container(container: IdentityContainer | None) -> None:
    global _default_container
    _default_container = container
