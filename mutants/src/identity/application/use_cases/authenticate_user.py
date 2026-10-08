"""Use Case: Authenticate user via email and password."""

from identity.application.dtos import LoginRequestDTO, TokenResponseDTO
from identity.application.ports import (
    PasswordHasherPort,
    TokenServicePort,
    UserRepositoryPort,
)
from identity.domain.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
)
from identity.domain.value_objects import Email


class AuthenticateUserUseCase:
    """Authenticates credentials and issues short-lived JWT access token."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, dto: LoginRequestDTO) -> TokenResponseDTO:
        email = Email(dto.email)
        user = self._user_repo.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError("Invalid email or password.")

        if not user.is_active:
            raise InactiveUserError(f"User account '{email.value}' is deactivated.")

        if not self._password_hasher.verify(dto.password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password.")

        access_token = self._token_service.create_access_token(user)

        return TokenResponseDTO(
            access_token=access_token,
            token_type="bearer",
            expires_in=900,
        )
