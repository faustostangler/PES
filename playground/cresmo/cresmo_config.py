"""Centralized Configuration System for the Cresmo Knowledge Ingestion & Synthesis Pipeline.

Implements the SOTA KISS single source of truth (SSOT) configuration architecture
following the Doctor Stangler Architecture Method (Clean / Hexagonal DDD).

Enforces the 4-Category Configuration Taxonomy:
  🔴 Category 1: Secrets & Credentials (Strictly .env or OS environment, fail-fast validated)
  🟡 Category 2: Infra & Topology (Filesystem paths, RPC addresses, binary targets)
  🟢 Category 3: Operational Tunables (LLM hyperparameters, retry policies, polling loops, concurrency)
  🔵 Category 4: Domain Invariants (Preserved in domain modules — not configurations)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import tomllib
from typing import Any, Literal
import yaml

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    SecretStr,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)

_CURRENT_DIR = Path(__file__).parent.resolve()
_WORKSPACE_DIR = _CURRENT_DIR.parent.parent


# ==============================================================================
# 🟡 Category 2: Infra & Topology Sub-models
# ==============================================================================


class StorageSettings(BaseModel):
    """Filesystem infrastructure layout and artifact storage topology.

    Paths default relative to root_dir, dynamically updating if root_dir is customized.
    """

    root_dir: Path = Field(
        default=_CURRENT_DIR,
        validation_alias=AliasChoices("root_dir", "CRESMO_ROOT", "STORAGE_ROOT_DIR"),
        description="Root directory for Cresmo pipeline artifacts and working storage.",
    )
    raw_dir: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("raw_dir", "DEFAULT_RAW_DIR", "CRESMO_RAW_DIR"),
        description="Directory for raw audio, video metadata, and initial transcripts.",
    )
    enriched_dir: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("enriched_dir", "DEFAULT_ENRICHED_DIR", "CRESMO_ENRICHED_DIR"),
        description="Directory containing enriched multi-pass markdown transcripts.",
    )
    wiki_dir: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("wiki_dir", "DEFAULT_CRESMO_WIKI_DIR", "CRESMO_WIKI_DIR"),
        description="Second-brain Obsidian vault directory for atomic notes and MOCs.",
    )
    processed_log: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("processed_log", "PROCESSED_CRESMO_LOG", "CRESMO_PROCESSED_LOG"),
        description="JSON ledger of successfully processed content IDs.",
    )
    playlist_file: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("playlist_file", "DEFAULT_PLAYLIST_FILE", "CRESMO_PLAYLIST_FILE"),
        description="Text manifest of YouTube channels and playlists for regular ingestion.",
    )
    priority_playlist: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("priority_playlist", "DEFAULT_PLAYLIST_PRIORITY_FILE", "CRESMO_PRIORITY_PLAYLIST_FILE"),
        description="Text manifest of expedited high-priority video URLs.",
    )
    priority_folder: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("priority_folder", "DEFAULT_PRIORITY_FOLDER", "CRESMO_PRIORITY_FOLDER"),
        description="Directory holding local raw markdown/text files for fast-track ingestion.",
    )
    brain_csv: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("brain_csv", "DEFAULT_BRAIN_CSV", "CRESMO_BRAIN_CSV"),
        description="Master index CSV linking content UUIDs, titles, URLs, and status.",
    )
    cookies_file: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("cookies_file", "DEFAULT_COOKIES_FILE", "CRESMO_COOKIES_FILE"),
        description="Netscape cookies file for yt-dlp authentication and rate-limit mitigation.",
    )
    rate_limit_log: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("rate_limit_log", "DEFAULT_RATE_LIMIT_LOG_FILE", "CRESMO_RATE_LIMIT_LOG"),
        description="Telemetry log file recording HTTP 429 and rate-limiting occurrences.",
    )

    @model_validator(mode="after")
    def _anchor_relative_paths(self) -> StorageSettings:
        """Anchor uninitialized subdirectories to root_dir."""
        root = self.root_dir
        if self.raw_dir is None:
            self.raw_dir = root / "raw"
        if self.enriched_dir is None:
            self.enriched_dir = root / "enriched"
        if self.wiki_dir is None:
            self.wiki_dir = root / "wiki"
        if self.processed_log is None:
            self.processed_log = root / "processed_cresmo.json"
        if self.playlist_file is None:
            self.playlist_file = root / "playlist.txt"
        if self.priority_playlist is None:
            self.priority_playlist = root / "playlist-priority.txt"
        if self.priority_folder is None:
            self.priority_folder = root / "priority_content"
        if self.brain_csv is None:
            self.brain_csv = root / "brain.csv"
        if self.cookies_file is None:
            self.cookies_file = root / ".yt_dlp_cookies.txt"
        if self.rate_limit_log is None:
            self.rate_limit_log = root / "rate_limit_log.json"
        return self


class AgentRPCSettings(BaseModel):
    """IDE Subagent RPC and gRPC IPC connection parameters."""

    brain_dir: Path = Field(
        default_factory=lambda: Path(
            os.environ.get(
                "ANTIGRAVITY_BRAIN_DIR",
                Path.home() / ".gemini" / "antigravity-ide" / "brain",
            )
        ),
        validation_alias=AliasChoices("brain_dir", "ANTIGRAVITY_BRAIN_DIR"),
        description="Directory where IDE agent session context and scratchpads reside.",
    )
    agentapi_binary: Path = Field(
        default_factory=lambda: Path(
            os.environ.get(
                "ANTIGRAVITY_AGENTAPI_BINARY",
                Path.home() / ".gemini" / "antigravity-ide" / "bin" / "agentapi",
            )
        ),
        validation_alias=AliasChoices("agentapi_binary", "ANTIGRAVITY_AGENTAPI_BINARY"),
        description="Path to the Antigravity agentapi CLI executable.",
    )
    ls_address: str = Field(
        default="127.0.0.1:41667",
        validation_alias=AliasChoices("ls_address", "ANTIGRAVITY_LS_ADDRESS", "DEFAULT_LS_ADDRESS"),
        description="Localhost gRPC address of the language server agent runner.",
    )
    csrf_token: str = Field(
        default="ff53390d-3617-40f6-836e-6c5375ff5817",
        validation_alias=AliasChoices("csrf_token", "ANTIGRAVITY_CSRF_TOKEN", "DEFAULT_CSRF_TOKEN"),
        description="Shared CSRF authentication token for IDE gRPC endpoints.",
    )
    grpc_test_timeout: float = Field(
        default=1.5,
        gt=0.0,
        validation_alias=AliasChoices("grpc_test_timeout", "GRPC_TEST_TIMEOUT_SECONDS"),
        description="Timeout in seconds for gRPC connectivity healthchecks.",
    )
    fallback_test_conversation_id: str = Field(
        default="0e69775c-ba22-4a48-ad18-ba6a318c9a04",
        validation_alias=AliasChoices(
            "fallback_test_conversation_id",
            "ANTIGRAVITY_FALLBACK_CONVERSATION_ID",
            "CRESMO_FALLBACK_TEST_CONVERSATION_ID",
        ),
        description="Fallback conversation UUID used to verify gRPC RPC alive status.",
    )


# ==============================================================================
# 🟢 Category 3: Operational Tunables Sub-models
# ==============================================================================


class RetrySettings(BaseModel):
    """Defensive retry engineering parameters for network and LLM API calls."""

    max_attempts: int = Field(
        default=7,
        ge=1,
        validation_alias=AliasChoices("max_attempts", "RETRY_MAX_ATTEMPTS", "CRESMO_RETRY_MAX_ATTEMPTS"),
        description="Maximum retry attempts on transient network or API rate-limit errors.",
    )
    multiplier: float = Field(
        default=2.0,
        ge=1.0,
        validation_alias=AliasChoices("multiplier", "RETRY_MULTIPLIER", "CRESMO_RETRY_MULTIPLIER"),
        description="Multiplier for exponential backoff sleep calculation.",
    )
    min_seconds: float = Field(
        default=2.0,
        ge=0.0,
        validation_alias=AliasChoices("min_seconds", "RETRY_MIN_SECONDS", "CRESMO_RETRY_MIN_SECONDS"),
        description="Minimum sleep duration in seconds between retry attempts.",
    )
    max_seconds: float = Field(
        default=60.0,
        ge=0.0,
        validation_alias=AliasChoices("max_seconds", "RETRY_MAX_SECONDS", "CRESMO_RETRY_MAX_SECONDS"),
        description="Maximum sleep duration cap in seconds between retry attempts.",
    )


class GeminiProviderSettings(BaseModel):
    """Operational tunables for the Google Gemini API adapter."""

    model_name: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices("model_name", "GEMINI_MODEL", "gemini_model", "CRESMO_GEMINI_MODEL"),
        description="Target Gemini model identifier (e.g. gemini-2.5-flash, gemini-3.8-flash).",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        validation_alias=AliasChoices("temperature", "GEMINI_TEMPERATURE", "CRESMO_GEMINI_TEMPERATURE"),
        description="Sampling temperature; lower values produce more deterministic output.",
    )
    max_output_tokens: int = Field(
        default=65536,
        ge=1,
        validation_alias=AliasChoices("max_output_tokens", "GEMINI_MAX_OUTPUT_TOKENS", "CRESMO_GEMINI_MAX_OUTPUT_TOKENS"),
        description="Maximum tokens allowed in generation response.",
    )
    request_timeout_seconds: float = Field(
        default=180.0,
        gt=0.0,
        validation_alias=AliasChoices("request_timeout_seconds", "GEMINI_REQUEST_TIMEOUT", "CRESMO_GEMINI_REQUEST_TIMEOUT"),
        description="Client HTTP/gRPC request timeout in seconds.",
    )
    enable_streaming: bool = Field(
        default=True,
        validation_alias=AliasChoices("enable_streaming", "GEMINI_ENABLE_STREAMING", "CRESMO_GEMINI_ENABLE_STREAMING"),
        description="Enable live token streaming for debug visibility into generation progress.",
    )
    retry: RetrySettings = Field(
        default_factory=RetrySettings,
        description="Defensive backoff retry configuration for Gemini API calls.",
    )


class OllamaProviderSettings(BaseModel):
    """Operational tunables for local Ollama LLM provider."""

    base_url: str = Field(
        default="http://localhost:11434",
        validation_alias=AliasChoices("base_url", "OLLAMA_URL", "DEFAULT_OLLAMA_URL"),
        description="Base URL for local Ollama HTTP inference endpoint.",
    )
    model_name: str = Field(
        default="phi3:mini",
        validation_alias=AliasChoices("model_name", "OLLAMA_MODEL", "DEFAULT_OLLAMA_MODEL"),
        description="Model identifier served by local Ollama daemon.",
    )
    request_timeout_seconds: float = Field(
        default=120.0,
        gt=0.0,
        validation_alias=AliasChoices("request_timeout_seconds", "OLLAMA_REQUEST_TIMEOUT"),
        description="Timeout in seconds for Ollama inference requests.",
    )
    max_transcript_chars: int = Field(
        default=2500,
        ge=100,
        validation_alias=AliasChoices("max_transcript_chars", "MAX_TRANSCRIPT_CHARS"),
        description="Maximum characters from raw transcript to send for indexing heuristics.",
    )


class LLMConfig(BaseModel):
    """Provider-segregated LLM settings adhering to Hexagonal Ports & Adapters."""

    active_provider: Literal["gemini", "ollama", "mock"] = Field(
        default="gemini",
        validation_alias=AliasChoices("active_provider", "LLM_PROVIDER", "CRESMO_LLM_PROVIDER"),
        description="Active LLM provider used by the transformation adapter.",
    )
    gemini: GeminiProviderSettings = Field(
        default_factory=GeminiProviderSettings,
        description="Configuration for Google Gemini provider.",
    )
    ollama: OllamaProviderSettings = Field(
        default_factory=OllamaProviderSettings,
        description="Configuration for local Ollama provider.",
    )


class PipelineSettings(BaseModel):
    """Operational tunables governing pipeline stage execution, timeouts, and thresholds."""

    trajectory_timeout_seconds: int = Field(
        default=15,
        ge=1,
        validation_alias=AliasChoices("trajectory_timeout_seconds", "DEFAULT_TRAJECTORY_TIMEOUT_SECONDS"),
        description="Timeout in seconds for reading trajectory logs during IDE agent execution.",
    )
    poll_max_attempts: int = Field(
        default=300,
        ge=1,
        validation_alias=AliasChoices("poll_max_attempts", "POLL_MAX_ATTEMPTS"),
        description="Maximum polling cycles before timing out an async IDE agent task.",
    )
    poll_sleep_seconds: float = Field(
        default=1.0,
        gt=0.0,
        validation_alias=AliasChoices("poll_sleep_seconds", "POLL_SLEEP_SECONDS"),
        description="Interval in seconds between async polling attempts.",
    )
    poll_dispatch_time_buffer: float = Field(
        default=1.0,
        ge=0.0,
        validation_alias=AliasChoices("poll_dispatch_time_buffer", "POLL_DISPATCH_TIME_BUFFER"),
        description="Safety buffer in seconds added before polling started timestamp.",
    )
    poll_fallback_interval: int = Field(
        default=30,
        ge=1,
        validation_alias=AliasChoices("poll_fallback_interval", "POLL_FALLBACK_INTERVAL"),
        description="Interval of polling attempts between checking fallback trajectory logs.",
    )
    stage2_passes: int = Field(
        default=3,
        ge=1,
        validation_alias=AliasChoices("stage2_passes", "DEFAULT_STAGE2_PASSES"),
        description="Number of iterative expansion passes executed in Stage 2 (cresmo-expander).",
    )
    min_enriched_existing_bytes: int = Field(
        default=500,
        ge=1,
        validation_alias=AliasChoices("min_enriched_existing_bytes", "MIN_ENRICHED_EXISTING_BYTES"),
        description="Minimum file size in bytes for an existing enriched note to be considered valid.",
    )
    min_valid_output_bytes: int = Field(
        default=300,
        ge=1,
        validation_alias=AliasChoices("min_valid_output_bytes", "MIN_VALID_OUTPUT_BYTES"),
        description="Minimum response payload size in bytes for Stage 2 markdown output.",
    )
    min_reconciliation_log_bytes: int = Field(
        default=200,
        ge=1,
        validation_alias=AliasChoices("min_reconciliation_log_bytes", "MIN_RECONCILIATION_LOG_BYTES"),
        description="Minimum response payload size in bytes for Stage 6 reconciliation log.",
    )
    max_candidate_parse_limit: int = Field(
        default=1000,
        ge=10,
        validation_alias=AliasChoices("max_candidate_parse_limit", "MAX_CANDIDATE_PARSE_LIMIT"),
        description="Maximum characters scanned when attempting to parse candidate JSON arrays.",
    )
    prompt_max_bytes_inline: int = Field(
        default=120_000,
        ge=1000,
        validation_alias=AliasChoices("prompt_max_bytes_inline", "PROMPT_MAX_BYTES_INLINE"),
        description="Safe byte limit for inlining content directly into CLI arguments vs disk references.",
    )


class IngestionSettings(BaseModel):
    """Operational tunables for media downloading and transcription ingestion."""

    days_lookback: int = Field(
        default=365 * 2,
        ge=1,
        validation_alias=AliasChoices("days_lookback", "DEFAULT_DAYS", "CRESMO_DAYS_LOOKBACK"),
        description="Temporal lookback window in days when filtering channel uploads.",
    )
    whisper_model: str = Field(
        default="base",
        validation_alias=AliasChoices("whisper_model", "DEFAULT_WHISPER_MODEL", "CRESMO_WHISPER_MODEL"),
        description="Whisper model footprint for audio transcription (tiny, base, small, medium, large).",
    )
    max_workers: int | None = Field(
        default=None,
        validation_alias=AliasChoices("max_workers", "DEFAULT_MAX_WORKERS", "CRESMO_MAX_WORKERS"),
        description="Worker concurrency limit. If None, dynamically resolved: 1 in debug, os.cpu_count() in prod.",
    )
    keep_audio: bool = Field(
        default=False,
        validation_alias=AliasChoices("keep_audio", "DEFAULT_KEEP_AUDIO", "CRESMO_KEEP_AUDIO"),
        description="Flag indicating whether to retain downloaded audio files post-transcription.",
    )

    def resolve_max_workers(self, debug: bool = False) -> int:
        """Resolve worker count dynamically following Doctor Stangler operational guidelines.

        In debug mode, worker count is clamped to 1 to guarantee deterministic tracing.
        In production mode, concurrency utilizes maximum available processor cores.
        Explicit non-zero configuration always takes precedence.

        Args:
            debug: True if running in debug mode; False for production runtime.

        Returns:
            Resolved integer concurrency limit.
        """
        if self.max_workers is not None and self.max_workers > 0:
            return self.max_workers
        if debug:
            return 1
        cpu_count = os.cpu_count() or 1
        return max(1, cpu_count)


class RuntimeSettings(BaseModel):
    """Operational tunables for CLI orchestrator execution mode and behavior."""

    default_command: str = Field(
        default="sync",
        validation_alias=AliasChoices("default_command", "DEFAULT_COMMAND"),
        description="Default CLI action when cresmo_main.py is invoked without subcommands.",
    )
    isolate_context: bool = Field(
        default=True,
        validation_alias=AliasChoices("isolate_context", "DEFAULT_ISOLATE_CONTEXT"),
        description="Whether to clear session conversation history between distinct pipeline stages.",
    )
    restart_server: bool = Field(
        default=False,
        validation_alias=AliasChoices("restart_server", "DEFAULT_RESTART_SERVER"),
        description="Whether to forcefully restart language server before executing stages.",
    )
    default_categories: tuple[str, ...] = Field(
        default=("politics_br",),
        validation_alias=AliasChoices("default_categories", "DEFAULT_CATEGORIES"),
        description="Default category taxonomy filters applied when no category is specified.",
    )
    auto_sync: bool = Field(
        default=True,
        validation_alias=AliasChoices("auto_sync", "CRESMO_AUTO_SYNC"),
        description="Automatically pull remote updates or playlists before starting pipeline run.",
    )


# ==============================================================================
# 🔴 SSOT Configuration Root: CresmoConfig
# ==============================================================================


class CresmoConfig(BaseSettings):
    """System-wide Single Source of Truth (SSOT) configuration root.

    Provides fail-fast Pydantic validation across all categories, supporting:
      1. Default safe operational values
      2. .env files (current directory and workspace root)
      3. Environment variable overrides (e.g. GEMINI_API_KEY, CRESMO_STORAGE__ROOT_DIR)
      4. External configuration files (YAML, TOML, JSON) via from_file() or CRESMO_CONFIG_FILE.
    """

    # 🔴 Category 1: Secret Credentials (Strictly required in prod / fail-fast)
    gemini_api_key: SecretStr = Field(
        ...,
        validation_alias=AliasChoices("gemini_api_key", "GEMINI_API_KEY", "CRESMO_GEMINI_API_KEY"),
        description="Google AI Studio Gemini API Key secret.",
    )

    # 🟡 Category 2: Infra & Topology
    storage: StorageSettings = Field(
        default_factory=StorageSettings,
        description="Storage directory paths and artifact files.",
    )
    agent_rpc: AgentRPCSettings = Field(
        default_factory=AgentRPCSettings,
        description="Agent RPC and gRPC connection settings.",
    )

    # 🟢 Category 3: Operational Tunables
    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM provider configurations segregated by provider.",
    )
    pipeline: PipelineSettings = Field(
        default_factory=PipelineSettings,
        description="Pipeline polling, threshold, and execution settings.",
    )
    ingestion: IngestionSettings = Field(
        default_factory=IngestionSettings,
        description="Audio downloading and transcription ingestion settings.",
    )
    runtime: RuntimeSettings = Field(
        default_factory=RuntimeSettings,
        description="CLI runtime behavior settings.",
    )

    model_config = SettingsConfigDict(
        env_file=(
            str(_CURRENT_DIR / ".env"),
            str(_WORKSPACE_DIR / ".env"),
        ),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        populate_by_name=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise configuration sources to optionally load from external config file."""
        sources: list[PydanticBaseSettingsSource] = [init_settings, env_settings, dotenv_settings]

        config_file_env = os.environ.get("CRESMO_CONFIG_FILE")
        if config_file_env:
            config_path = Path(config_file_env).resolve()
            if config_path.exists():
                suffix = config_path.suffix.lower()
                if suffix in (".yaml", ".yml"):
                    sources.append(YamlConfigSettingsSource(settings_cls, yaml_file=config_path))
                elif suffix == ".toml":
                    sources.append(TomlConfigSettingsSource(settings_cls, toml_file=config_path))
                elif suffix == ".json":
                    sources.append(JsonConfigSettingsSource(settings_cls, json_file=config_path))

        sources.append(file_secret_settings)
        return tuple(sources)

    @classmethod
    def from_file(cls, file_path: Path | str, **overrides: Any) -> CresmoConfig:
        """Instantiate CresmoConfig by parsing an external YAML, TOML, or JSON file.

        Args:
            file_path: Absolute or relative path to the configuration file.
            **overrides: Runtime overrides that take precedence over file values.

        Returns:
            Validated CresmoConfig instance.

        Raises:
            FileNotFoundError: If the specified config file does not exist.
            ValueError: If the file extension is unsupported.
        """
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        suffix = path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            raw_data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        elif suffix == ".toml":
            raw_data = tomllib.loads(path.read_text(encoding="utf-8"))
        elif suffix == ".json":
            raw_data = json.loads(path.read_text(encoding="utf-8"))
        else:
            raise ValueError(f"Unsupported configuration file format '{suffix}'. Supported: .yaml, .yml, .toml, .json")

        merged = {**raw_data, **overrides}
        return cls(**merged)


# ==============================================================================
# SSOT Singleton Accessor
# ==============================================================================

_CONFIG_CACHE: CresmoConfig | None = None


def get_config(
    reload: bool = False,
    config_file: Path | str | None = None,
    **overrides: Any,
) -> CresmoConfig:
    """Retrieve the cached system configuration singleton or construct a new one.

    Args:
        reload: Force reconstruction of the singleton even if cached.
        config_file: Optional external file (.yaml, .toml, .json) to load from.
        **overrides: Optional explicit parameter overrides.

    Returns:
        The validated CresmoConfig singleton.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None or reload:
        if config_file is not None:
            _CONFIG_CACHE = CresmoConfig.from_file(config_file, **overrides)
        else:
            _CONFIG_CACHE = CresmoConfig(**overrides)
    return _CONFIG_CACHE


def reset_config() -> None:
    """Clear cached configuration singleton, ensuring test isolation."""
    global _CONFIG_CACHE
    _CONFIG_CACHE = None
