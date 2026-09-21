"""Use Case: Register new User account."""

import uuid
from datetime import UTC, datetime

from identity.application.dtos import RegisterUserRequestDTO, RegisterUserResponseDTO
from identity.application.ports import PasswordHasherPort, UserRepositoryPort
from identity.domain.entities import User
from identity.domain.exceptions import UserAlreadyExistsError, WeakPasswordError
from identity.domain.value_objects import Email, Role, UserId


class RegisterUserUseCase:
    """Orchestrates registration of a new user with secure password hashing."""

    def __init__(self, user_repo: UserRepositoryPort, password_hasher: PasswordHasherPort) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, dto: RegisterUserRequestDTO) -> RegisterUserResponseDTO:
        email = Email(dto.email)

        # Enforce uniqueness
        existing = self._user_repo.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError(f"User with email '{email.value}' is already registered.")

        # Minimum password strength invariant
        if len(dto.password) < 8:
            raise WeakPasswordError("Password must be at least 8 characters long.")

        hashed_password = self._password_hasher.hash(dto.password)

        parsed_roles = []
        for r in dto.roles:
            try:
                parsed_roles.append(Role(r.lower()))
            except ValueError:
                parsed_roles.append(Role.USER)

        user_id = UserId(f"usr_{uuid.uuid4().hex}")
        user = User(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
            roles=frozenset(parsed_roles if parsed_roles else [Role.USER]),
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self._user_repo.save(user)

        return RegisterUserResponseDTO(
            user_id=user.id.value,
            email=user.email.value,
            roles=[r.value for r in user.roles],
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )
