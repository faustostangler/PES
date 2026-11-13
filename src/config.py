"""Single Source of Truth Centralized Configuration for PES Modular Monolith.

Sources settings strictly from .env and environment variables.
Conforms to:
- SOTA-KISS Core Engineering Directives: fail-fast validation with pydantic-settings
  centralized in single config.py sourced from .env. Zero scattered env vars.
- ADR-005: Multi-Role 12-Factor Container & Settings
- ADR-048: Architectural Remediation and Comprehensive Mutation Blindage
"""

from __future__ import annotations

import functools
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from cresmo.infrastructure.config import CresmoSettings


# FUTURE / DEFERRED: Multi-user IAM runtime configuration reserved per ADR-062.
class IamSettings(BaseSettings):
    """Configuration settings for IAM Bounded Context."""

    model_config = SettingsConfigDict(
        env_prefix="IAM_",
        env_file=".env",
        extra="ignore",
    )

    jwt_secret_key: SecretStr = Field(
        default=SecretStr("pes-default-insecure-secret-key-change-in-production-32chars!"),
        min_length=32,
        validation_alias=AliasChoices("jwt_secret_key", "IAM_JWT_SECRET_KEY", "jwt_secret"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    # Argon2id RFC 9106 recommended parameters
    argon2_time_cost: int = 3
    argon2_memory_cost: int = 65536  # 64 MiB
    argon2_parallelism: int = 4

    # Persistence
    identity_db_path: Path = Path("data/cresmo_identity.db")


# Backward-compatible alias
IdentitySettings = IamSettings


class AppConfig(BaseSettings):
    """Single Source of Truth Root Application Settings combining Bounded Contexts."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    iam: IamSettings = Field(default_factory=IamSettings)
    cresmo: CresmoSettings = Field(default_factory=CresmoSettings)


@functools.lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Cached global singleton for AppConfig."""
    return AppConfig()


__all__ = [
    "AppConfig",
    "CresmoSettings",
    "IamSettings",
    "IdentitySettings",
    "get_config",
]
