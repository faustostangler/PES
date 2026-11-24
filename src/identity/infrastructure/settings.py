"""Configuration and Environment Settings for IAM Bounded Context."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# FUTURE / DEFERRED: Multi-user IAM runtime configuration reserved per ADR-062.
class IdentitySettings(BaseSettings):
    """Configuration settings for IAM Bounded Context."""

    model_config = SettingsConfigDict(
        env_prefix="IAM_",
        env_file=".env",
        extra="ignore",
    )

    jwt_secret_key: SecretStr = Field(
        default=SecretStr("pes-default-insecure-secret-key-change-in-production-32chars!"),
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    # Argon2id RFC 9106 recommended parameters
    argon2_time_cost: int = 3
    argon2_memory_cost: int = 65536  # 64 MiB
    argon2_parallelism: int = 4

    # Persistence
    identity_db_path: Path = Path("data/cresmo_identity.db")


__all__ = ["IdentitySettings"]
