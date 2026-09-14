"""Stage 2 Use Case: Fill Gaps and Expand Fluid Prose.

Executes Socratic audit and multi-pass fluid prose expansion (cresmo-expander).
"""

from __future__ import annotations

import re

from cresmo.application.ports import (
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import EnrichedCompendium, RawTranscript
from cresmo.domain.exceptions import CompendiumStructureError
from cresmo.domain.value_objects import NoteTitle

_TITLE_H1_PATTERN = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)
_COMPLEMENTARY_TAG = "## Informações Complementares"
_COMPLEMENTARY_REGEX = re.compile(
    r"^\s*#{2,3}\s+\*?\*?(?:Informa[cç][oõ]es\s+Complementares|Notas\s+Complementares|Informa[cç][oõ]es\s+Adicionais)\*?\*?.*$",
    re.MULTILINE | re.IGNORECASE,
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁFillGapsFluidProseUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore


class FillGapsFluidProseUseCase:
    """Stage 2: Multi-pass Socratic gap analysis & fluid prose expansion."""

    @_mutmut_mutated(mutants_xǁFillGapsFluidProseUseCaseǁ__init____mutmut)
    def __init__(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

    def xǁFillGapsFluidProseUseCaseǁ__init____mutmut_orig(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

    def xǁFillGapsFluidProseUseCaseǁ__init____mutmut_1(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = None
        self.vault_port = vault_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

    def xǁFillGapsFluidProseUseCaseǁ__init____mutmut_2(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = None
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

    def xǁFillGapsFluidProseUseCaseǁ__init____mutmut_3(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port
        if prompt_provider is not None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = prompt_provider

    def xǁFillGapsFluidProseUseCaseǁ__init____mutmut_4(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = None
        else:
            self.prompt_provider = prompt_provider

    def xǁFillGapsFluidProseUseCaseǁ__init____mutmut_5(
        self,
        llm_port: LLMTransformationPort,
        vault_port: VaultRepositoryPort,
        prompt_provider: PromptProviderPort | None = None,
    ) -> None:
        self.llm_port = llm_port
        self.vault_port = vault_port
        if prompt_provider is None:
            from cresmo.infrastructure.adapters.prompt_provider import JsonPromptProvider

            self.prompt_provider: PromptProviderPort = JsonPromptProvider()
        else:
            self.prompt_provider = None

    @_mutmut_mutated(mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut)
    def execute(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_orig(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_1(
        self,
        raw_transcript: RawTranscript,
        passes: int = 4,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_2(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = None
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_3(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = None

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_4(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(None):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_5(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = None
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_6(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=None,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_7(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=None,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_8(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=None,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_9(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=None,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_10(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=None,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_11(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_12(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_13(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_14(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_15(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_16(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_17(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_18(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p - 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_19(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 2,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_20(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p >= 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_21(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 1 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_22(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = None

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_23(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=None)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_24(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = None
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_25(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(None)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_26(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = None
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_27(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(None).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_28(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(2).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_29(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = None

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_30(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title and "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_31(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "XXUntitled CompendiumXX"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_32(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "untitled compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_33(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "UNTITLED COMPENDIUM"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_34(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = None
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_35(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(None)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_36(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = None
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_37(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = None
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_38(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = None
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_39(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub(None, body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_40(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", None).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_41(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub(body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_42(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", ).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_43(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("XXXX", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_44(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG not in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_45(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = None
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_46(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(None, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_47(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, None)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_48(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_49(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, )
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_50(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.rsplit(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_51(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 2)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_52(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = None
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_53(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[1].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_54(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = None
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_55(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub(None, body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_56(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", None).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_57(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub(body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_58(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", ).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_59(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("XXXX", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_60(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = None
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_61(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[2].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_62(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(None)

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_63(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_64(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                None
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_65(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "XXEnrichedCompendium must contain a non-empty 'Informações Complementares' section.XX"
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_66(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "enrichedcompendium must contain a non-empty 'informações complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_67(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "ENRICHEDCOMPENDIUM MUST CONTAIN A NON-EMPTY 'INFORMAÇÕES COMPLEMENTARES' SECTION."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_68(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = None
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_69(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime(None) if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_70(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("XX%Y%m%dXX") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_71(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_72(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%M%D") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_73(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else "XXXX"
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_74(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = None
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_75(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=None,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_76(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=None,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_77(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=None,
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_78(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=None,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_79(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=None,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_80(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=None,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_81(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=None,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_82(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=None,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_83(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=None,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_84(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=None,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_85(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=None,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_86(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_87(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_88(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_89(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_90(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_91(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_92(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_93(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_94(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_95(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_96(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_97(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(None),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(compendium)
        return compendium

    def xǁFillGapsFluidProseUseCaseǁexecute__mutmut_98(
        self,
        raw_transcript: RawTranscript,
        passes: int = 3,
    ) -> EnrichedCompendium:
        """Execute Stage 2 multi-pass progressive enrichment."""
        current_text = raw_transcript.body
        file_name = f"{raw_transcript.content_id.value}.txt"

        for p in range(passes):
            prompt = self.prompt_provider.get_gap_filler_prompt(
                pass_num=p + 1,
                total_passes=passes,
                channel_name=raw_transcript.channel_name,
                file_name=file_name,
                raw_text=raw_transcript.body,
                current_text=current_text if p > 0 else None,
            )
            current_text = self.llm_port.transform(prompt=prompt)

        # Extract title from H1 or fallback to raw title
        m_title = _TITLE_H1_PATTERN.search(current_text)
        if m_title:
            extracted_title = m_title.group(1).strip()
        else:
            extracted_title = raw_transcript.title or "Untitled Compendium"

        # Split body and complementary info (case-insensitive and whitespace resilient)
        m_comp = _COMPLEMENTARY_REGEX.search(current_text)
        if m_comp:
            body = current_text[: m_comp.start()].strip()
            comp_info = current_text[m_comp.end() :].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
        elif _COMPLEMENTARY_TAG in current_text:
            parts = current_text.split(_COMPLEMENTARY_TAG, 1)
            body = parts[0].strip()
            body = _TITLE_H1_PATTERN.sub("", body).strip()
            comp_info = parts[1].strip()
        else:
            raise CompendiumStructureError(f"Missing mandatory section '{_COMPLEMENTARY_TAG}'")

        if not comp_info:
            raise CompendiumStructureError(
                "EnrichedCompendium must contain a non-empty 'Informações Complementares' section."
            )

        video_date_str = (
            raw_transcript.upload_date.strftime("%Y%m%d") if raw_transcript.upload_date else ""
        )
        compendium = EnrichedCompendium(
            content_id=raw_transcript.content_id,
            channel_name=raw_transcript.channel_name,
            title=NoteTitle(extracted_title),
            body=body,
            complementary_info=comp_info,
            pass_count=passes,
            channel_id=raw_transcript.channel_id,
            channel_category=raw_transcript.channel_category,
            source_url=raw_transcript.source_url,
            video_date=video_date_str,
            video_description=raw_transcript.video_description,
        )
        self.vault_port.save_enriched_compendium(None)
        return compendium

mutants_xǁFillGapsFluidProseUseCaseǁ__init____mutmut['_mutmut_orig'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁ__init____mutmut['xǁFillGapsFluidProseUseCaseǁ__init____mutmut_1'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁ__init____mutmut['xǁFillGapsFluidProseUseCaseǁ__init____mutmut_2'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁ__init____mutmut['xǁFillGapsFluidProseUseCaseǁ__init____mutmut_3'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁ__init____mutmut['xǁFillGapsFluidProseUseCaseǁ__init____mutmut_4'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁ__init____mutmut['xǁFillGapsFluidProseUseCaseǁ__init____mutmut_5'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁ__init____mutmut_5 # type: ignore # mutmut generated

mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['_mutmut_orig'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_1'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_2'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_3'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_4'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_5'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_6'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_7'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_8'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_9'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_10'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_11'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_12'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_13'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_14'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_15'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_15 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_16'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_16 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_17'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_17 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_18'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_18 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_19'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_19 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_20'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_20 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_21'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_21 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_22'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_22 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_23'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_23 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_24'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_24 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_25'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_25 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_26'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_26 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_27'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_27 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_28'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_28 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_29'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_29 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_30'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_30 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_31'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_31 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_32'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_32 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_33'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_33 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_34'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_34 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_35'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_35 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_36'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_36 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_37'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_37 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_38'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_38 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_39'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_39 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_40'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_40 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_41'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_41 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_42'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_42 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_43'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_43 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_44'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_44 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_45'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_45 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_46'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_46 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_47'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_47 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_48'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_48 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_49'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_49 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_50'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_50 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_51'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_51 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_52'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_52 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_53'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_53 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_54'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_54 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_55'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_55 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_56'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_56 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_57'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_57 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_58'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_58 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_59'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_59 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_60'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_60 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_61'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_61 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_62'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_62 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_63'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_63 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_64'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_64 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_65'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_65 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_66'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_66 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_67'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_67 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_68'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_68 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_69'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_69 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_70'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_70 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_71'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_71 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_72'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_72 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_73'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_73 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_74'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_74 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_75'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_75 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_76'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_76 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_77'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_77 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_78'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_78 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_79'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_79 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_80'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_80 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_81'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_81 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_82'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_82 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_83'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_83 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_84'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_84 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_85'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_85 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_86'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_86 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_87'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_87 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_88'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_88 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_89'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_89 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_90'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_90 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_91'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_91 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_92'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_92 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_93'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_93 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_94'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_94 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_95'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_95 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_96'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_96 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_97'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_97 # type: ignore # mutmut generated
mutants_xǁFillGapsFluidProseUseCaseǁexecute__mutmut['xǁFillGapsFluidProseUseCaseǁexecute__mutmut_98'] = FillGapsFluidProseUseCase.xǁFillGapsFluidProseUseCaseǁexecute__mutmut_98 # type: ignore # mutmut generated
