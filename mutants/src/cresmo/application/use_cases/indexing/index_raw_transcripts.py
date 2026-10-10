"""Application Use Case for incrementally indexing raw transcripts.

Extracts a concise key concept and a dense paratactic synthesis paragraph from raw transcripts,
appending the result incrementally to both the channel's semantic catalog (_canal.md) and
the global tabular index (brain.csv).

Conforms to:
- SPEC-001: Core Knowledge Synthesis Specifications
- ADR-001: Modular Monolith Domain Integrity
- ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
- ADR-013: Iterative LLM-as-a-Judge Indexing Loops
- ADR-019: SOTA KISS Nomenclature & Value Objects
- ADR-028: Strict Rejection of Standalone Raw Indexing & Universal FluidTranscript Contract
"""

from __future__ import annotations

import logging

from cresmo.application.ports import (
    LlmJudgePort,
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.application.ports.settings import DEFAULT_LANGUAGE
from cresmo.application.use_cases.indexing.distiller import LLMTranscriptDistiller
from cresmo.domain.entities import FluidTranscript, UserIdentity
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.taxonomy import classify_channel
from cresmo.domain.value_objects import (
    ChannelName,
    RawIndexEntry,
)

logger = logging.getLogger(__name__)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut: MutantDict = {}  # type: ignore
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore


class IndexRawTranscriptsUseCase:
    """Orchestrates paratactic conceptual indexing of media transcripts from clean fluid prose.

    Conforms to:
        - SPEC-001: Core Knowledge Synthesis Specifications (Incremental Indexing)
        - SPEC-011: Fluid Prose Detranscription and Gap Filler Decoupling
        - ADR-001: Modular Monolith Domain Integrity
        - ADR-011: Zero Hardcoded Tunables and Self-Healing Output Validation
        - ADR-028: Strict Rejection of Standalone Raw Indexing & Universal FluidTranscript Contract

    Attributes:
        vault_port: Repository port for reading transcripts and appending indexes.
        llm_indexing_port: LLM transformation port for key concept and synthesis extraction.
        prompt_provider: Provider port supplying indexing prompt templates.
        max_chars: Maximum character limit from transcript body fed into LLM prompt (0 = full text).
        temperature: Generation sampling temperature.
        language: Target synthesis language.
        max_rewrites: Maximum corrective rewrite attempts if output violates formatting.
    """

    @_mutmut_mutated(mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut)
    def __init__(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_orig(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_1(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 1,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_2(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 1.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_3(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 4,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_4(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = None
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_5(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port and vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_6(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is not None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_7(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError(None)
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_8(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("XXvault_port is required.XX")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_9(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("VAULT_PORT IS REQUIRED.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_10(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = None
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_11(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port and llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_12(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is not None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_13(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError(None)
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_14(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("XXllm_indexing_port is required.XX")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_15(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("LLM_INDEXING_PORT IS REQUIRED.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_16(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is not None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_17(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError(None)

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_18(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("XXprompt_provider is required.XX")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_19(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("PROMPT_PROVIDER IS REQUIRED.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_20(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = None
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_21(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = None  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_22(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = None
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_23(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = None  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_24(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = None
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_25(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = None
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_26(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = None
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_27(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = None
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_28(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = None
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_29(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = None

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_30(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = None

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_31(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=None,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_32(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=None,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_33(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=None,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_34(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=None,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_35(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=None,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_36(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=None,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_37(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_38(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_39(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            language=self.language,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_40(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            max_rewrites=self.max_rewrites,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_41(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            llm_judge_port=self.llm_judge_port,
        )

    def xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_42(
        self,
        vault_port: VaultRepositoryPort | None = None,
        llm_indexing_port: LLMTransformationPort | None = None,
        prompt_provider: PromptProviderPort | None = None,
        max_chars: int = 0,
        temperature: float = 0.2,
        language: str = DEFAULT_LANGUAGE,
        max_rewrites: int = 3,
        llm_judge_port: LlmJudgePort | None = None,
        *,
        vault_repo: VaultRepositoryPort | None = None,
        llm: LLMTransformationPort | None = None,
    ) -> None:
        """Initialize IndexRawTranscriptsUseCase with required ports and tunables.

        Conforms to ADR-019 (vault_port & llm_indexing_port naming symmetry).
        """
        resolved_vault = vault_port or vault_repo
        if resolved_vault is None:
            raise ValueError("vault_port is required.")
        resolved_llm = llm_indexing_port or llm
        if resolved_llm is None:
            raise ValueError("llm_indexing_port is required.")
        if prompt_provider is None:
            raise ValueError("prompt_provider is required.")

        self.vault_port = resolved_vault
        self.vault_repo = resolved_vault  # Backward-compatible alias
        self.llm_indexing_port = resolved_llm
        self.llm = resolved_llm  # Backward-compatible alias
        self.prompt_provider = prompt_provider
        self.max_chars = max_chars
        self.temperature = temperature
        self.language = language
        self.max_rewrites = max_rewrites
        self.llm_judge_port = llm_judge_port

        self._distiller = LLMTranscriptDistiller(
            llm_indexing_port=self.llm_indexing_port,
            prompt_provider=self.prompt_provider,
            temperature=self.temperature,
            language=self.language,
            max_rewrites=self.max_rewrites,
            )

    @_mutmut_mutated(mutants_xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut)
    def warmup(self, timeout_seconds: float | None = None) -> None:
        """Trigger warmup on the underlying indexing LLM port (ADR-019: direct contract call)."""
        self.llm_indexing_port.warmup(timeout_seconds=timeout_seconds)

    def xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut_orig(self, timeout_seconds: float | None = None) -> None:
        """Trigger warmup on the underlying indexing LLM port (ADR-019: direct contract call)."""
        self.llm_indexing_port.warmup(timeout_seconds=timeout_seconds)

    def xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut_1(self, timeout_seconds: float | None = None) -> None:
        """Trigger warmup on the underlying indexing LLM port (ADR-019: direct contract call)."""
        self.llm_indexing_port.warmup(timeout_seconds=None)

    @_mutmut_mutated(mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut)
    def execute(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_orig(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_1(
        self,
        transcript: FluidTranscript,
        force: bool = True,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_2(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_3(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                None
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_4(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(None).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_5(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = None
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_6(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = None

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_7(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(None)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_8(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_9(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = None
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_10(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(None)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_11(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id not in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_12(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    None,
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_13(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    None,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_14(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    None,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_15(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_16(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_17(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_18(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "XX[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.XX",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_19(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[indexraw] skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_20(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[INDEXRAW] SKIPPING ALREADY INDEXED TRANSCRIPT '%S' FOR CHANNEL '%S'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_21(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = None

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_22(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title and video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_23(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = None
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_24(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars >= 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_25(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 1:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_26(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = None

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_27(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = None
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_28(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=None,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_29(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=None,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_30(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=None,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_31(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=None,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_32(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=None,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_33(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=None,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_34(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_35(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_36(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_37(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_38(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_39(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_40(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = None
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_41(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=None,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_42(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=None,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_43(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=None,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_44(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=None,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_45(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=None,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_46(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=None,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_47(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_48(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_49(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_50(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_51(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_52(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_53(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = None
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_54(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=None,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_55(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=None,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_56(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=None,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_57(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=None,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_58(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=None,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_59(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=None,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_60(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=None,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_61(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_62(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_63(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_64(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_65(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_66(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_67(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_68(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                None,
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_69(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                None,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_70(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                None,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_71(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                None,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_72(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=None,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_73(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_74(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_75(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_76(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_77(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_78(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "XX[IndexRaw] Skipped '%s' (%s) due to inference error: %sXX",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_79(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[indexraw] skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_80(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[INDEXRAW] SKIPPED '%S' (%S) DUE TO INFERENCE ERROR: %S",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_81(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=False,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_82(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = None

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_83(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = None
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_84(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else "XXXX"
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_85(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_86(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = None

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_87(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(None)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_88(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = None

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_89(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=None,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_90(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=None,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_91(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=None,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_92(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=None,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_93(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=None,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_94(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=None,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_95(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=None,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_96(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=None,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_97(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=None,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_98(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_99(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_100(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_101(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_102(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_103(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_104(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_105(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_106(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_107(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(None, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_108(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, None)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_109(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_110(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, )
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_111(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(None)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_112(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            None,
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_113(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            None,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_114(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            None,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_115(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            None,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_116(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_117(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_118(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_119(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[IndexRaw] Indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_120(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "XX[IndexRaw] Indexed '%s' | %s | '%s'XX",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_121(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[indexraw] indexed '%s' | %s | '%s'",
            video_id,
            channel_name,
            concept,
        )
        return entry

    def xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_122(
        self,
        transcript: FluidTranscript,
        force: bool = False,
        user: UserIdentity | None = None,
    ) -> RawIndexEntry | None:
        """Index a single fluid transcript incrementally if not already indexed (Primary entrypoint).

        Conforms to ADR-028: strictly requires FluidTranscript input. Standalone raw indexing is rejected.
        """
        if not isinstance(transcript, FluidTranscript):
            raise DomainValidationError(
                f"IndexRawTranscriptsUseCase strictly requires FluidTranscript, got: {type(transcript).__name__}"
            )

        video_id = transcript.content.id
        channel_name = ChannelName(transcript.channel.name)

        # ACL check: Avoid redundant token expenditure if already indexed
        if not force:
            indexed_ids = self.vault_port.get_indexed_video_ids_for_channel(channel_name)
            if video_id in indexed_ids:
                logger.info(
                    "[IndexRaw] Skipping already indexed transcript '%s' for channel '%s'.",
                    video_id.value,
                    channel_name,
                )
                return None

        title = transcript.content.title or video_id.value

        # Build prompt from bounded transcript excerpt to preserve context budget
        excerpt = transcript.content.body.strip()
        if self.max_chars > 0:
            excerpt = excerpt[: self.max_chars]

        try:
            concept = self._distiller.extract_concepts(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            summary = self._distiller.extract_summary(
                video_id=video_id,
                title=title,
                text=excerpt,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
            synthesis = self._distiller.extract_synthesis(
                video_id=video_id,
                title=title,
                excerpt=excerpt,
                summary=summary,
                channel_name=channel_name,
                channel_id=transcript.channel.id,
                user=user,
            )
        except Exception as exc:
            # Gracefully degrade on network/inference outage to prevent aborting batch runs
            logger.warning(
                "[IndexRaw] Skipped '%s' (%s) due to inference error: %s",
                video_id,
                channel_name,
                exc,
                exc_info=True,
            )
            return None

        url = (
            transcript.provenance.url
            if transcript.provenance.url
            else f"https://youtube.com/watch?v={video_id}"
        )

        category = transcript.channel.category.strip() if transcript.channel.category else ""
        if not category:
            category, _ = classify_channel(channel_name)

        entry = RawIndexEntry(
            video_id=transcript.content.id,
            url=url,
            title=title,
            channel_name=channel_name,
            key_concept=concept,
            synthesis=synthesis,
            channel_category=category,
            summary=summary,
            excerpt=excerpt,
        )

        # Dual output persistence: channel markdown index and global tabular catalog (brain.csv)
        self.vault_port.append_channel_index_entry(channel_name, entry)
        self.vault_port.append_brain_csv_entry(entry)

        logger.info(
            "[INDEXRAW] INDEXED '%S' | %S | '%S'",
            video_id,
            channel_name,
            concept,
        )
        return entry

mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['_mutmut_orig'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_1'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_2'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_3'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_4'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_5'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_6'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_7'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_8'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_9'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_10'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_11'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_12'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_13'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_14'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_15'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_16'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_17'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_18'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_18 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_19'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_19 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_20'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_20 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_21'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_21 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_22'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_22 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_23'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_23 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_24'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_24 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_25'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_25 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_26'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_26 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_27'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_27 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_28'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_28 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_29'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_29 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_30'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_30 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_31'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_31 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_32'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_32 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_33'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_33 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_34'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_34 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_35'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_35 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_36'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_36 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_37'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_37 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_38'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_38 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_39'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_39 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_40'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_40 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_41'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_41 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁ__init____mutmut['xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_42'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁ__init____mutmut_42 # type: ignore # mutmut generated

mutants_xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut['_mutmut_orig'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut_orig # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut['xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut_1'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁwarmup__mutmut_1 # type: ignore # mutmut generated

mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['_mutmut_orig'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_1'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_2'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_3'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_4'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_5'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_6'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_7'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_8'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_9'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_10'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_11'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_12'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_13'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_14'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_15'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_15 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_16'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_16 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_17'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_17 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_18'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_18 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_19'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_19 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_20'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_20 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_21'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_21 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_22'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_22 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_23'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_23 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_24'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_24 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_25'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_25 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_26'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_26 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_27'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_27 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_28'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_28 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_29'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_29 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_30'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_30 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_31'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_31 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_32'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_32 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_33'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_33 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_34'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_34 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_35'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_35 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_36'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_36 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_37'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_37 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_38'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_38 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_39'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_39 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_40'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_40 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_41'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_41 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_42'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_42 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_43'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_43 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_44'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_44 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_45'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_45 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_46'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_46 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_47'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_47 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_48'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_48 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_49'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_49 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_50'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_50 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_51'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_51 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_52'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_52 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_53'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_53 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_54'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_54 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_55'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_55 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_56'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_56 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_57'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_57 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_58'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_58 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_59'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_59 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_60'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_60 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_61'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_61 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_62'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_62 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_63'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_63 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_64'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_64 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_65'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_65 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_66'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_66 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_67'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_67 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_68'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_68 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_69'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_69 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_70'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_70 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_71'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_71 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_72'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_72 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_73'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_73 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_74'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_74 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_75'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_75 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_76'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_76 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_77'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_77 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_78'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_78 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_79'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_79 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_80'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_80 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_81'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_81 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_82'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_82 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_83'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_83 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_84'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_84 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_85'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_85 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_86'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_86 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_87'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_87 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_88'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_88 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_89'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_89 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_90'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_90 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_91'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_91 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_92'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_92 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_93'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_93 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_94'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_94 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_95'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_95 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_96'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_96 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_97'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_97 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_98'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_98 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_99'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_99 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_100'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_100 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_101'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_101 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_102'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_102 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_103'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_103 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_104'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_104 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_105'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_105 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_106'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_106 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_107'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_107 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_108'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_108 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_109'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_109 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_110'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_110 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_111'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_111 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_112'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_112 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_113'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_113 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_114'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_114 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_115'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_115 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_116'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_116 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_117'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_117 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_118'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_118 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_119'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_119 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_120'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_120 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_121'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_121 # type: ignore # mutmut generated
mutants_xǁIndexRawTranscriptsUseCaseǁexecute__mutmut['xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_122'] = IndexRawTranscriptsUseCase.xǁIndexRawTranscriptsUseCaseǁexecute__mutmut_122 # type: ignore # mutmut generated
