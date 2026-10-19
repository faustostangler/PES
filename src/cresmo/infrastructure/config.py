"""Centralized Configuration for Cresmo Hexagonal Modular Monolith.

Enforces the 4-Category Configuration Taxonomy using Pydantic Settings V2:
- Category 1: Secrets & Credentials (Strictly from .env or environment)
- Category 2: Infra & Storage Paths (Obsidian vault, raw, enriched, master, index)
- Category 3: Operational Tunables (Model names, temperatures, batch sizes, worker counts)
- Category 4: Domain Invariants (Defined in domain entities and value objects)

Conforms to:
    - ADR-005: Multi-Role 12-Factor Container & Settings
    - ADR-006: Resilient Workspace Root Discovery
    - SPEC-005: Operational Staging Validation
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Self

from pydantic import AliasChoices, Field, SecretStr, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from cresmo.application.ports.settings import DEFAULT_LANGUAGE
from cresmo.infrastructure.paths import find_workspace_root

_WORKSPACE_DIR = find_workspace_root()

DEFAULT_LANGFUSE_PROMPT_LABEL: str = "production"
DEFAULT_JUDGE_PASS_THRESHOLD: float = 0.9
DEFAULT_JUDGE_GEMINI_MODEL: str = "gemini-3.5-flash-lite"
DEFAULT_JUDGE_TEMPERATURE: float = 0.0


class CresmoSettings(BaseSettings):
    """Single Source of Truth (SSOT) configuration for the Cresmo engine.

    Aggregates runtime options, credential secrets, infrastructure filesystem paths,
    and operational tunables. Validates configurations at application startup to enforce
    the 12-Factor App methodology and fail-fast principles.

    Attributes:
        DEFAULT_LANGUAGE: Class-level canonical default language fallback.
        DEFAULT_LANGFUSE_PROMPT_LABEL: Class-level canonical prompt label fallback.
        gemini_api_keys: List of secret keys for Google GenAI quota-aware failover.
        gemini_api_key: Primary secret key for backward compatibility.
        langfuse_secret_key: Secret key for Langfuse observability endpoint.
        langfuse_public_key: Public telemetry identifier for Langfuse tracing.
        langfuse_host: Telemetry collector endpoint URL.
        data_dir: Base directory for staging media, compendiums, and ledger databases.
        vault_dir: Target Obsidian Second Brain vault directory.
        sqlite_ledger_filename: Database filename for the SQLite WAL ledger.
        gemini_model: Primary model identifier for LLM transformation stages.
        whisper_model: Model variant for local audio transcription fallback.
        batch_size: Synthesis chunk size for atomic note generation.
    """

    DEFAULT_LANGUAGE: ClassVar[str] = DEFAULT_LANGUAGE
    DEFAULT_LANGFUSE_PROMPT_LABEL: ClassVar[str] = DEFAULT_LANGFUSE_PROMPT_LABEL
    DEFAULT_JUDGE_PASS_THRESHOLD: ClassVar[float] = DEFAULT_JUDGE_PASS_THRESHOLD
    DEFAULT_JUDGE_GEMINI_MODEL: ClassVar[str] = DEFAULT_JUDGE_GEMINI_MODEL
    DEFAULT_JUDGE_TEMPERATURE: ClassVar[float] = DEFAULT_JUDGE_TEMPERATURE

    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            str(_WORKSPACE_DIR / ".env"),
            str(_WORKSPACE_DIR / "vault" / ".env"),
            str(_WORKSPACE_DIR / "data" / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
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
        """Customise settings sources to safely parse comma-separated credentials from env."""

        def _safe_decode(field_name: str, field: Any, val: Any, orig_decode: Any) -> Any:
            if field_name == "gemini_api_keys" and isinstance(val, str):
                try:
                    return orig_decode(field_name, field, val)
                except (ValueError, TypeError):
                    return [p.strip() for p in val.split(",") if p.strip()]
            return orig_decode(field_name, field, val)

        orig_dot = dotenv_settings.decode_complex_value
        dotenv_settings.decode_complex_value = (  # type: ignore[method-assign]
            lambda field_name, field, value: _safe_decode(field_name, field, value, orig_dot)
        )

        orig_env = env_settings.decode_complex_value
        env_settings.decode_complex_value = (  # type: ignore[method-assign]
            lambda field_name, field, value: _safe_decode(field_name, field, value, orig_env)
        )

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    def __init__(
        self,
        *args: Any,
        _env_file: Path | str | None | Any = ...,
        **values: Any,
    ) -> None:
        """Initialize settings with optional explicit environment file override."""
        if _env_file is not ...:
            values["_env_file"] = _env_file
        if "gemini_api_key" in values and "gemini_api_keys" not in values:
            values["gemini_api_keys"] = values["gemini_api_key"]
        super().__init__(*args, **values)

    # =========================================================================
    # 🔴 Category 1: Secrets & Credentials
    # =========================================================================
    gemini_api_keys: list[SecretStr] = Field(
        default_factory=list,
        description="Google Gemini API Keys for quota-aware failover and rotation.",
    )

    @property
    def gemini_api_key(self) -> SecretStr:
        """Primary Google Gemini API Key for backward compatibility."""
        if self.gemini_api_keys:
            return self.gemini_api_keys[0]
        return SecretStr("")

    @model_validator(mode="before")
    @classmethod
    def _normalize_gemini_credentials(cls, data: Any) -> Any:
        """Normalize comma-separated strings or legacy single key into gemini_api_keys."""
        if isinstance(data, dict):
            raw_keys = (
                data.get("gemini_api_keys")
                or data.get("GEMINI_API_KEYS")
                or data.get("gemini_api_key")
                or data.get("GEMINI_API_KEY")
            )
            if raw_keys is not None:
                if isinstance(raw_keys, str):
                    data["gemini_api_keys"] = [
                        SecretStr(p.strip()) for p in raw_keys.split(",") if p.strip()
                    ]
                elif isinstance(raw_keys, SecretStr):
                    data["gemini_api_keys"] = [raw_keys]
                elif isinstance(raw_keys, list):
                    data["gemini_api_keys"] = [
                        item if isinstance(item, SecretStr) else SecretStr(item.strip())
                        for item in raw_keys
                        if (isinstance(item, SecretStr) or (isinstance(item, str) and item.strip()))
                    ]
        return data

    typesafe_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("typesafe_api_key", "TYPESAFE_API_KEY"),
        description="TypeSafe AI API Key for System One Jev decision evaluations.",
    )
    langfuse_secret_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("langfuse_secret_key", "LANGFUSE_SECRET_KEY"),
        description="Langfuse secret key for evaluation and observability.",
    )
    langfuse_public_key: str = Field(
        default="",
        validation_alias=AliasChoices("langfuse_public_key", "LANGFUSE_PUBLIC_KEY"),
        description="Langfuse public key for evaluation and observability.",
    )
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        validation_alias=AliasChoices("langfuse_host", "LANGFUSE_HOST", "LANGFUSE_BASE_URL"),
        description="Langfuse telemetry endpoint URL.",
    )
    langfuse_environment: str = Field(
        default="development",
        description="Langfuse telemetry environment (e.g. 'production', 'staging', 'development').",
    )
    langfuse_prompt_label: str = Field(
        default=DEFAULT_LANGFUSE_PROMPT_LABEL,
        description="Active prompt label tag in Langfuse (e.g. 'production', 'staging').",
    )
    langfuse_timeout_seconds: int = Field(
        default=30,
        description="Read and connect timeout in seconds for Langfuse client and OpenTelemetry exporter.",
    )
    anonymization_enabled: bool = Field(
        default=True,
        description="Enable PII and credential masking in telemetry, span attributes, and exports.",
    )
    preflight_probe_timeout_seconds: float = Field(
        default=2.0,
        description="Socket timeout in seconds for active preflight probes (Langfuse, Ollama).",
    )
    enable_preflight_probes: bool = Field(
        default=True,
        description="Enable active HTTP preflight probes before initializing telemetry or remote services.",
    )

    # =========================================================================
    # 🟡 Category 2: Infra & Storage Paths
    # =========================================================================
    data_dir: Path = Field(
        default_factory=lambda: _WORKSPACE_DIR / "data",
        description="Root directory for raw media lake, enriched compendiums, and ledger.",
    )
    vault_dir: Path = Field(
        default_factory=lambda: _WORKSPACE_DIR / "vault",
        description="Root directory for Obsidian Second Brain knowledge graph vault.",
    )

    @property
    def raw_dir(self) -> Path:
        """Directory for ingested raw media transcripts."""
        return self.data_dir / "raw"

    @property
    def fluid_dir(self) -> Path:
        """Directory for intermediate detranscribed fluid prose transcripts."""
        return self.data_dir / "fluid"

    @property
    def enriched_dir(self) -> Path:
        """Directory for enriched multi-pass compendiums."""
        return self.data_dir / "enriched"

    @property
    def master_dir(self) -> Path:
        """Directory for consolidated master compendiums per channel category for RAG."""
        return self.data_dir / "master"

    @property
    def index_path(self) -> Path:
        """Master lookup JSON index."""
        return self.vault_dir / "_index.json"

    @property
    def mocs_dir(self) -> Path:
        """Subdirectory within vault/ housing Maps of Content."""
        return self.vault_dir / "MOCs"

    sqlite_ledger_filename: str = Field(
        default="cresmo_ledger.db",
        description="Filename of the SQLite WAL database for processed content tracking.",
    )

    @property
    def sqlite_ledger_path(self) -> Path:
        """Absolute path to processed content SQLite WAL database file."""
        return self.data_dir / self.sqlite_ledger_filename

    playlist_filename: str = Field(
        default="playlist.txt",
        description="Filename of the main video manifest inside data_dir.",
    )
    playlist_priority_filename: str = Field(
        default="playlist-priority.txt",
        description="Filename of the priority video manifest inside data_dir.",
    )
    brain_csv_filename: str = Field(
        default="brain.csv",
        description="Filename of the global conceptual index CSV inside data_dir.",
    )

    @property
    def brain_csv_path(self) -> Path:
        """Absolute path to global brain.csv conceptual index file."""
        return self.data_dir / self.brain_csv_filename

    priority_texts_dirname: str = Field(
        default="priority",
        description="Directory name inside data_dir containing priority text files (.txt, .md).",
    )

    @property
    def playlist_path(self) -> Path:
        """Absolute path to the main video manifest."""
        return self.data_dir / self.playlist_filename

    @property
    def playlist_priority_path(self) -> Path:
        """Absolute path to the priority video manifest."""
        return self.data_dir / self.playlist_priority_filename

    @property
    def priority_texts_dir(self) -> Path:
        """Absolute path to the priority texts directory."""
        return self.data_dir / self.priority_texts_dirname

    def ensure_directories(self) -> None:
        """Ensure all runtime directories exist on the filesystem.

        Creates directory tree idempotently (equivalent to mkdir -p), preventing
        missing-directory IOErrors when writing raw transcripts, compendiums, or vault notes.
        """
        for directory in (
            self.data_dir,
            self.vault_dir,
            self.mocs_dir,
            self.raw_dir,
            self.enriched_dir,
            self.master_dir,
            self.priority_texts_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    browser_headers_path: Path | None = Field(
        default=None,
        description="Optional custom path to browser request headers pool JSON file.",
    )
    cookies_file: Path | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "cookies_file", "DEFAULT_COOKIES_FILE", "CRESMO_COOKIES_FILE"
        ),
        description="Path to Netscape cookies file for YouTube authentication.",
    )
    prompts_path: Path | None = Field(
        default=None,
        description="Optional custom path to LLM prompt templates JSON file.",
    )
    skills_dir: Path | None = Field(
        default=None,
        description="Optional custom path to .agents/skills directory for prompt enrichment.",
    )

    # =========================================================================
    # 🟢 Category 3: Operational Tunables
    # =========================================================================
    browser_cookies: str | None = Field(
        default="firefox",
        description="Default browser to extract cookies from if cookies_file is absent ('firefox', 'chrome', etc.).",
    )
    auto_extract_cookies: bool = Field(
        default=True,
        description="Whether to automatically extract cookies from browser if cookies_file is absent or expired.",
    )
    enable_channel_crawler: bool = Field(
        default=True,
        description="Whether batch discovery automatically crawls 365d uploads across all channels by default.",
    )
    require_auth_cookies: bool = Field(
        default=False,
        description="Whether to fail-fast if no valid authenticated YouTube session cookies are found.",
    )
    pipeline_version: str = Field(
        default="cresmo:v2",
        validation_alias=AliasChoices(
            "pipeline_version", "PIPELINE_VERSION", "CRESMO_PIPELINE_VERSION"
        ),
        description="Canonical pipeline version tag emitted to OpenTelemetry spans and Langfuse traces.",
    )
    gemini_model: str = Field(
        default="gemini-3.5-flash-lite",
        description="Default Gemini model variant for pipeline stages.",
    )
    gemini_fallback_model: str = Field(
        default="gemini-3.1-flash-lite",
        description="Fallback Gemini model variant if primary hits quota or demand spikes.",
    )
    prometheus_enabled: bool = Field(
        default=True,
        description="Whether Prometheus SRE Golden Signals and DORA metrics collection is enabled.",
    )
    prometheus_port: int = Field(
        default=9090,
        description="Local Prometheus scraping and exposition port.",
    )
    log_level: str = Field(
        default="WARNING",
        validation_alias=AliasChoices("log_level", "LOG_LEVEL", "CRESMO_LOG_LEVEL"),
        description="Root logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    log_format: str = Field(
        default="json",
        validation_alias=AliasChoices("log_format", "LOG_FORMAT", "CRESMO_LOG_FORMAT"),
        description="Log output format: 'json' for Loki structured ingestion, 'text' for local dev.",
    )
    whisper_model: str = Field(
        default="base",
        description="Whisper STT model variant for audio transcription.",
    )
    days_lookback: int = Field(
        default=365,
        description="Default crawling lookback window in days (default: 365 / 1 year).",
    )
    whisper_workers: int = Field(
        default=1,
        validation_alias=AliasChoices("whisper_workers", "max_whisper_workers"),
        description="Concurrent worker threads for local Whisper audio-to-text fallback (default: 1).",
    )
    subtitle_workers: int = Field(
        default=0,
        validation_alias=AliasChoices("subtitle_workers", "max_subtitle_workers"),
        description="Concurrent worker threads for native JSON/SRV subtitle downloading (defaults to whisper_workers * 5).",
    )
    channel_discovery_workers: int = Field(
        default=0,
        validation_alias=AliasChoices("channel_discovery_workers", "max_channel_workers"),
        description="Concurrent worker threads for scanning YouTube channel uploads feeds (defaults to whisper_workers * 10).",
    )
    discovery_queue_maxsize: int = Field(
        default=50,
        ge=1,
        validation_alias=AliasChoices("discovery_queue_maxsize", "max_discovery_queue_size"),
        description="Maximum bounded capacity for batch source streaming queue to enforce backpressure against OOM (default: 50).",
    )

    @model_validator(mode="after")
    def _compute_worker_multiples(self) -> Self:
        """Calculate dynamic worker pool sizes and resolve candidate cookie paths.

        Maintains healthy worker ratios (5x for network-bound subtitle downloads,
        10x for channel uploads feed polling) derived from the CPU-bound whisper_workers base,
        preventing thread starvation and CPU saturation.

        Returns:
            Self instance with calculated worker counts and auto-discovered cookies_file.
        """
        if self.subtitle_workers <= 0:
            self.subtitle_workers = max(1, self.whisper_workers * 5)
        if self.channel_discovery_workers <= 0:
            self.channel_discovery_workers = max(1, self.whisper_workers * 10)

        # Auto-resolve cookies_file candidate paths if not set
        if self.cookies_file is None or not self.cookies_file.exists():
            candidates = [
                self.data_dir / "cookies.txt",
                _WORKSPACE_DIR / "data" / "cookies.txt",
                _WORKSPACE_DIR / ".yt_dlp_cookies.txt",
            ]
            for candidate in candidates:
                if candidate.exists() and candidate.stat().st_size > 0:
                    self.cookies_file = candidate
                    break

        return self

    batch_size: int = Field(
        default=5,
        validation_alias=AliasChoices("batch_size", "CRESMO_BATCH_SIZE"),
        description="Batch size for Atomic Note synthesis.",
    )
    keep_audio: bool = Field(
        default=False,
        description="Whether to preserve downloaded raw audio files.",
    )
    expansion_max_passes: int = Field(
        default=5,
        ge=1,
        le=10,
        validation_alias=AliasChoices(
            "expansion_max_passes",
            "CRESMO_EXPANSION_MAX_PASSES",
            "EXPANSION_MAX_PASSES",
            "gap_filler_passes",
            "CRESMO_GAP_FILLER_PASSES",
            "GAP_FILLER_PASSES",
        ),
        description="Default multi-pass text expansion and refinement limit before mechanical saturation.",
    )

    @property
    def gap_filler_passes(self) -> int:
        """Backward-compatible property alias for expansion_max_passes."""
        return self.expansion_max_passes

    concat_max_words: int = Field(
        default=500_000,
        validation_alias=AliasChoices("concat_max_words", "CONCAT_MAX_WORDS", "MASTER_MAX_WORDS"),
        description="Maximum word limit per aggregated master document before sequential rollover without mid-file splits.",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        validation_alias=AliasChoices("ollama_base_url", "CRESMO_OLLAMA_URL", "OLLAMA_URL"),
        description="Local Ollama endpoint URL for raw transcript conceptual indexing.",
    )
    ollama_model: str = Field(
        default="qwen2.5:7b",
        validation_alias=AliasChoices("ollama_model", "CRESMO_OLLAMA_MODEL", "OLLAMA_MODEL"),
        description="Local Ollama model variant for raw transcript conceptual indexing.",
    )
    indexing_provider: str = Field(
        default="ollama",
        validation_alias=AliasChoices("indexing_provider", "CRESMO_INDEXING_PROVIDER"),
        description="Provider for raw transcript conceptual indexing: 'ollama' (default local) or 'gemini' (cloud API).",
    )
    ollama_timeout_seconds: float = Field(
        default=300.0,
        ge=1.0,
        validation_alias=AliasChoices(
            "ollama_timeout_seconds",
            "CRESMO_OLLAMA_TIMEOUT",
            "OLLAMA_TIMEOUT",
        ),
        description="HTTP timeout in seconds for local Ollama inference requests (CPU-only may need 300s+).",
    )
    ollama_warmup_timeout_seconds: float = Field(
        default=300.0,
        ge=1.0,
        validation_alias=AliasChoices(
            "ollama_warmup_timeout_seconds",
            "CRESMO_OLLAMA_WARMUP_TIMEOUT",
            "OLLAMA_WARMUP_TIMEOUT",
        ),
        description="Extended HTTP timeout in seconds for initial Ollama model preload into VRAM.",
    )
    ollama_keep_alive: str = Field(
        default="1h",
        validation_alias=AliasChoices(
            "ollama_keep_alive",
            "CRESMO_OLLAMA_KEEPALIVE",
            "OLLAMA_KEEPALIVE",
            "CRESMO_OLLAMA_KEEP_ALIVE",
        ),
        description="Duration to keep the model loaded in Ollama VRAM/RAM (e.g. '1h', '60m', '-1' for indefinite).",
    )
    ollama_num_predict: int = Field(
        default=0,
        ge=0,
        validation_alias=AliasChoices(
            "ollama_num_predict", "CRESMO_OLLAMA_NUM_PREDICT", "OLLAMA_NUM_PREDICT"
        ),
        description="Maximum tokens predicted by local Ollama model (0 means unconstrained / model default).",
    )
    raw_index_max_chars: int = Field(
        default=0,
        description="Maximum characters of transcript body passed to LLM for conceptual synthesis, zero means full text.",
    )
    language: str = Field(
        default=DEFAULT_LANGUAGE,
        validation_alias=AliasChoices("language", "CRESMO_LANGUAGE"),
        description="Target generation language for synthesis, compendiums, and conceptual indexing.",
    )
    llm_synthesis_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        validation_alias=AliasChoices(
            "llm_synthesis_temperature",
            "CRESMO_LLM_SYNTHESIS_TEMPERATURE",
        ),
        description="Default sampling temperature for generative synthesis and expansion stages.",
    )
    llm_indexing_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        validation_alias=AliasChoices(
            "llm_indexing_temperature",
            "CRESMO_LLM_INDEXING_TEMPERATURE",
        ),
        description="Sampling temperature for raw transcript conceptual indexing.",
    )

    raw_index_max_attempts: int = Field(
        default=3,
        ge=0,
        validation_alias=AliasChoices(
            "raw_index_max_attempts", "CRESMO_RAW_INDEX_MAX_ATTEMPTS", "RAW_INDEX_MAX_ATTEMPTS"
        ),
        description="Maximum LLM judge rewrite attempts for raw indexing (0 means unconstrained / infinite loop).",
    )

    inventory_max_attempts: int = Field(
        default=3,
        ge=0,
        validation_alias=AliasChoices(
            "inventory_max_attempts", "CRESMO_INVENTORY_MAX_ATTEMPTS", "INVENTORY_MAX_ATTEMPTS"
        ),
        description="Maximum LLM judge rewrite attempts for atomic inventory discovery (0 means unconstrained / infinite loop).",
    )

    # =========================================================================
    # 🔴 Category 3: Quality Judge & Decision-Model Evaluator Settings (ADR-029)
    # =========================================================================
    typesafe_model: str = Field(
        default="jev-latest",
        validation_alias=AliasChoices("typesafe_model", "TYPESAFE_MODEL"),
        description="Model identifier for TypeSafe AI System One decision evaluations.",
    )
    typesafe_base_url: str = Field(
        default="https://api.typesafe.ai/v1",
        validation_alias=AliasChoices("typesafe_base_url", "TYPESAFE_BASE_URL"),
        description="Base URL endpoint for TypeSafe AI API.",
    )
    judge_provider: str = Field(
        default="gemini",  # default original typesafe
        validation_alias=AliasChoices("judge_provider", "CRESMO_JUDGE_PROVIDER"),
        description="Primary quality judge provider ('gemini', 'typesafe', 'ollama').",
    )
    judge_fallback_provider: str = Field(
        default="ollama",
        validation_alias=AliasChoices("judge_fallback_provider", "CRESMO_JUDGE_FALLBACK_PROVIDER"),
        description="Fallback quality judge provider when primary fails.",
    )
    judge_blocking: bool = Field(
        default=False,
        validation_alias=AliasChoices("judge_blocking", "CRESMO_JUDGE_BLOCKING"),
        description="Whether failed quality evaluations raise DomainValidationError or log warning scores.",
    )
    judge_max_attempts: int = Field(
        default=1,
        validation_alias=AliasChoices("judge_max_attempts", "CRESMO_JUDGE_MAX_ATTEMPTS"),
        description="Maximum attempts to re-execute a stage when quality evaluation fails.",
    )
    judge_pass_threshold: float = Field(
        default=DEFAULT_JUDGE_PASS_THRESHOLD,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "judge_pass_threshold",
            "CRESMO_JUDGE_PASS_THRESHOLD",
            "JUDGE_PASS_THRESHOLD",
        ),
        description="Minimum score threshold required for quality judge evaluations to pass.",
    )
    gap_filler_judge_threshold: float = Field(
        default=DEFAULT_JUDGE_PASS_THRESHOLD,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "gap_filler_judge_threshold",
            "CRESMO_GAP_FILLER_JUDGE_THRESHOLD",
            "GAP_FILLER_JUDGE_THRESHOLD",
        ),
        description="Minimum score threshold required for gap_filler judge evaluations to pass.",
    )
    gap_filler_judge_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "factual_grounding": 0.25,
            "socratic_epistemic_depth": 0.25,
            "causal_stratification_agency": 0.20,
            "complementary_substance": 0.15,
            "authorial_naturalism": 0.15,
        },
        validation_alias=AliasChoices(
            "gap_filler_judge_weights",
            "CRESMO_GAP_FILLER_JUDGE_WEIGHTS",
            "GAP_FILLER_JUDGE_WEIGHTS",
        ),
        description="Criterion weights for gap_filler stage judge evaluation.",
    )
    judge_gemini_model: str = Field(
        default=DEFAULT_JUDGE_GEMINI_MODEL,
        validation_alias=AliasChoices(
            "judge_gemini_model",
            "CRESMO_JUDGE_GEMINI_MODEL",
            "JUDGE_GEMINI_MODEL",
        ),
        description="Gemini model variant for quality judge evaluations.",
    )
    judge_temperature: float = Field(
        default=DEFAULT_JUDGE_TEMPERATURE,
        ge=0.0,
        le=2.0,
        validation_alias=AliasChoices(
            "judge_temperature",
            "CRESMO_JUDGE_TEMPERATURE",
            "JUDGE_TEMPERATURE",
        ),
        description="Sampling temperature for quality judge evaluation models.",
    )


__all__ = [
    "DEFAULT_JUDGE_GEMINI_MODEL",
    "DEFAULT_JUDGE_PASS_THRESHOLD",
    "DEFAULT_JUDGE_TEMPERATURE",
    "DEFAULT_LANGFUSE_PROMPT_LABEL",
    "CresmoSettings",
]
