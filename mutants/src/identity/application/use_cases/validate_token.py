"""Use Case: Validate and decode JWT access token."""

from identity.application.dtos import AuthenticatedUserDTO
from identity.application.ports import TokenServicePort, UserRepositoryPort
from identity.domain.exceptions import InvalidTokenError
from identity.domain.value_objects import UserId


class ValidateTokenUseCase:
    """Validates JWT access token and hydrates AuthenticatedUserDTO."""

    def __init__(self, token_service: TokenServicePort, user_repo: UserRepositoryPort) -> None:
        self._token_service = token_service
        self._user_repo = user_repo

    def execute(self, token: str) -> AuthenticatedUserDTO:
        claims = self._token_service.decode_access_token(token)
        user_id_str = claims.get("sub")

        if not user_id_str:
            raise InvalidTokenError("Access token claims missing subject ('sub').")

        user = self._user_repo.get_by_id(UserId(user_id_str))
        if user is None or not user.is_active:
            raise InvalidTokenError("User account is inactive or not found.")

        return AuthenticatedUserDTO(
            user_id=user.id.value,
            tenant_id=claims.get("tenant_id", "default"),
            email=user.email.value,
            roles=[r.value for r in user.roles],
            scopes=claims.get("scopes", []),
        )
