"""Stage 6 Use Case: Reconcile Maps of Content (MOC).

Reconciles atomic notes into thematic Maps of Content, enforcing zero orphaned notes.
"""

from __future__ import annotations

import json

from cresmo.application.json_parser import extract_json_data
from cresmo.application.ports import (
    LLMTransformationPort,
    PromptProviderPort,
    VaultRepositoryPort,
)
from cresmo.domain.entities import MapOfContent
from cresmo.domain.exceptions import DomainValidationError
from cresmo.domain.value_objects import NoteTitle


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁReconcileMOCsUseCaseǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut: MutantDict = {}  # type: ignore


class ReconcileMOCsUseCase:
    """Stage 6: Map of Content reconciliation and graph topological governance."""

    @_mutmut_mutated(mutants_xǁReconcileMOCsUseCaseǁ__init____mutmut)
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

    def xǁReconcileMOCsUseCaseǁ__init____mutmut_orig(
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

    def xǁReconcileMOCsUseCaseǁ__init____mutmut_1(
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

    def xǁReconcileMOCsUseCaseǁ__init____mutmut_2(
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

    def xǁReconcileMOCsUseCaseǁ__init____mutmut_3(
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

    def xǁReconcileMOCsUseCaseǁ__init____mutmut_4(
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

    def xǁReconcileMOCsUseCaseǁ__init____mutmut_5(
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

    @_mutmut_mutated(mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut)
    def execute(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_orig(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_1(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = None
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_2(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = None

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_3(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"XXtitleXX": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_4(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"TITLE": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_5(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "XXtypeXX": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_6(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "TYPE": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_7(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "XXdomainXX": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_8(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "DOMAIN": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_9(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = None

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_10(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=None,
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_11(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(None, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_12(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=None),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_13(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_14(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_15(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=True),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_16(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = None
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_17(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=None)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_18(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = None
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_19(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(None)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_20(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_21(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                None
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_22(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(None).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_23(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = None
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_24(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_25(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                break
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_26(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = None
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_27(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get(None)
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_28(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("XXtitleXX")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_29(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("TITLE")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_30(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str and not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_31(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_32(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_33(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                break
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_34(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = None
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_35(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(None)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_36(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = None
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_37(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(None).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_38(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get(None, "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_39(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", None)).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_40(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_41(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", )).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_42(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("XXthemeXX", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_43(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("THEME", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_44(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "XXXX")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_45(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = None

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_46(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(None).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_47(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get(None, "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_48(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", None)).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_49(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_50(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", )).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_51(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("XXoverviewXX", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_52(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("OVERVIEW", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_53(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "XXXX")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_54(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = None
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_55(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get(None, [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_56(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", None)
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_57(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get([])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_58(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", )
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_59(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("XXassociated_notesXX", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_60(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("ASSOCIATED_NOTES", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_61(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = None
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_62(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = None
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_63(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) or n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_64(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = None
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_65(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(None)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_66(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = None
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_67(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.upper()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_68(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_69(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(None)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_70(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(None)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_71(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_72(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                break

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_73(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = None

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_74(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=None,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_75(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=None,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_76(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=None,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_77(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=None,
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_78(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_79(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_80(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_81(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_82(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(None),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_83(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(None)
            mocs.append(moc)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

    def xǁReconcileMOCsUseCaseǁexecute__mutmut_84(self) -> list[MapOfContent]:
        """Execute Stage 6 MOC reconciliation.

        Returns:
            List of generated or updated MapOfContent domain aggregates.

        Raises:
            DomainValidationError: If MOC generation payload is malformed.
        """
        # Step 1: Read all existing atomic notes from vault.
        notes = self.vault_port.get_all_atomic_notes()
        note_summaries = [
            {"title": n.title.value, "type": n.note_type.value, "domain": n.domain} for n in notes
        ]

        # Step 2: Prompt LLM to cluster notes into thematic Maps of Content.
        prompt = self.prompt_provider.get_mocs_prompt(
            notes_json=json.dumps(note_summaries, ensure_ascii=False),
        )

        response = self.llm_port.transform(prompt=prompt)
        data = extract_json_data(response)
        if not isinstance(data, list):
            raise DomainValidationError(
                f"MOC reconciliation expected JSON array, got: {type(data).__name__}"
            )

        # Step 3: Parse response and instantiate MapOfContent aggregates.
        mocs: list[MapOfContent] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            title_str = entry.get("title")
            if not title_str or not isinstance(title_str, str):
                continue
            title = NoteTitle(title_str)
            theme = str(entry.get("theme", "")).strip()
            overview = str(entry.get("overview", "")).strip()

            raw_associated = entry.get("associated_notes", [])
            seen_associated: set[str] = set()
            associated_notes: list[NoteTitle] = []
            for n in raw_associated:
                if isinstance(n, str) and n.strip():
                    nt = NoteTitle(n)
                    k = nt.value.lower()
                    if k not in seen_associated:
                        seen_associated.add(k)
                        associated_notes.append(nt)

            if not associated_notes:
                continue

            moc = MapOfContent(
                title=title,
                theme=theme,
                overview=overview,
                associated_notes=tuple(associated_notes),
            )

            # Step 4: Persist via vault repository port.
            self.vault_port.save_map_of_content(moc)
            mocs.append(None)

        # Step 5: Return reconciled MapOfContent list.
        return mocs

mutants_xǁReconcileMOCsUseCaseǁ__init____mutmut['_mutmut_orig'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁ__init____mutmut['xǁReconcileMOCsUseCaseǁ__init____mutmut_1'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁ__init____mutmut['xǁReconcileMOCsUseCaseǁ__init____mutmut_2'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁ__init____mutmut['xǁReconcileMOCsUseCaseǁ__init____mutmut_3'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁ__init____mutmut['xǁReconcileMOCsUseCaseǁ__init____mutmut_4'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁ__init____mutmut['xǁReconcileMOCsUseCaseǁ__init____mutmut_5'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁ__init____mutmut_5 # type: ignore # mutmut generated

mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['_mutmut_orig'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_orig # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_1'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_1 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_2'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_2 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_3'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_3 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_4'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_4 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_5'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_5 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_6'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_6 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_7'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_7 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_8'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_8 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_9'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_9 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_10'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_10 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_11'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_11 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_12'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_12 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_13'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_13 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_14'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_14 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_15'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_15 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_16'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_16 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_17'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_17 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_18'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_18 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_19'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_19 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_20'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_20 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_21'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_21 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_22'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_22 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_23'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_23 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_24'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_24 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_25'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_25 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_26'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_26 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_27'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_27 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_28'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_28 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_29'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_29 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_30'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_30 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_31'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_31 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_32'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_32 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_33'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_33 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_34'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_34 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_35'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_35 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_36'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_36 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_37'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_37 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_38'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_38 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_39'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_39 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_40'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_40 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_41'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_41 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_42'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_42 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_43'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_43 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_44'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_44 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_45'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_45 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_46'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_46 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_47'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_47 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_48'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_48 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_49'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_49 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_50'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_50 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_51'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_51 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_52'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_52 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_53'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_53 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_54'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_54 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_55'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_55 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_56'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_56 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_57'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_57 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_58'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_58 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_59'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_59 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_60'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_60 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_61'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_61 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_62'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_62 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_63'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_63 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_64'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_64 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_65'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_65 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_66'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_66 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_67'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_67 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_68'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_68 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_69'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_69 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_70'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_70 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_71'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_71 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_72'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_72 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_73'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_73 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_74'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_74 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_75'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_75 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_76'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_76 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_77'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_77 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_78'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_78 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_79'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_79 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_80'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_80 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_81'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_81 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_82'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_82 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_83'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_83 # type: ignore # mutmut generated
mutants_xǁReconcileMOCsUseCaseǁexecute__mutmut['xǁReconcileMOCsUseCaseǁexecute__mutmut_84'] = ReconcileMOCsUseCase.xǁReconcileMOCsUseCaseǁexecute__mutmut_84 # type: ignore # mutmut generated
