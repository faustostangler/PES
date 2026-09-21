"""Configuration and Environment Settings for IAM Bounded Context."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class IdentitySettings(BaseSettings):
    """Configuration settings for IAM, with fail-fast validation via pydantic-settings."""

    model_config = SettingsConfigDict(
        env_prefix="IAM_",
        env_file=".env",
        extra="ignore",
    )

    jwt_secret_key: SecretStr = SecretStr(
        "pes-default-insecure-secret-key-change-in-production-32chars!"
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    # Argon2id RFC 9106 recommended parameters
    argon2_time_cost: int = 3
    argon2_memory_cost: int = 65536  # 64 MiB
    argon2_parallelism: int = 4

    # Persistence
    identity_db_path: Path = Path("data/cresmo_identity.db")
