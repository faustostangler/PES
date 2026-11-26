"""Configuration and Environment Settings for IAM Bounded Context."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

IDENTITY_ENV_PREFIX: Final[str] = "IAM_"
DEFAULT_ENV_FILE: Final[str] = ".env"
DEFAULT_INSECURE_JWT_SECRET: Final[str] = (
    "pes-default-insecure-secret-key-change-in-production-32chars!"
)
MIN_JWT_SECRET_LENGTH: Final[int] = 32
DEFAULT_JWT_ALGORITHM: Final[str] = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 15
DEFAULT_ARGON2_TIME_COST: Final[int] = 3
DEFAULT_ARGON2_MEMORY_COST_KIB: Final[int] = 65536
DEFAULT_ARGON2_PARALLELISM: Final[int] = 4
DEFAULT_IDENTITY_DB_PATH: Final[Path] = Path("data/cresmo_identity.db")


# FUTURE / DEFERRED: Multi-user IAM runtime configuration reserved per ADR-062.
class IdentitySettings(BaseSettings):
    """Configuration settings for IAM Bounded Context."""

    model_config = SettingsConfigDict(
        env_prefix=IDENTITY_ENV_PREFIX,
        env_file=DEFAULT_ENV_FILE,
        extra="ignore",
    )

    jwt_secret_key: SecretStr = Field(
        default=SecretStr(DEFAULT_INSECURE_JWT_SECRET),
        min_length=MIN_JWT_SECRET_LENGTH,
    )
    jwt_algorithm: str = DEFAULT_JWT_ALGORITHM
    access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES

    # Argon2id RFC 9106 recommended parameters
    argon2_time_cost: int = DEFAULT_ARGON2_TIME_COST
    argon2_memory_cost: int = DEFAULT_ARGON2_MEMORY_COST_KIB  # 64 MiB
    argon2_parallelism: int = DEFAULT_ARGON2_PARALLELISM

    # Persistence
    identity_db_path: Path = DEFAULT_IDENTITY_DB_PATH


__all__ = ["IdentitySettings"]
